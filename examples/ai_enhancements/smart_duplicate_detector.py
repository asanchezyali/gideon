"""
Ejemplo: Detección Inteligente de Duplicados
=============================================

Este ejemplo implementa un detector de duplicados multi-nivel:
1. Exacto: Hash SHA-256
2. Casi-exacto: Fuzzy hashing (ssdeep)
3. Semántico: Embeddings + cosine similarity
4. Versiones: Detectar drafts, v1, v2, final
"""

from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import asyncio
from langchain_community.embeddings import OllamaEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class DuplicateType(Enum):
    """Types of duplicate detection."""
    EXACT = "exact"              # Identical files (hash match)
    FUZZY = "fuzzy"              # Similar files (fuzzy hash)
    SEMANTIC = "semantic"        # Similar content (embedding similarity)
    VERSION = "version"          # Different versions of same document


@dataclass
class DuplicateGroup:
    """Group of duplicate files."""
    duplicate_type: DuplicateType
    files: List[Path]
    similarity_scores: Dict[Tuple[Path, Path], float] = field(default_factory=dict)
    primary_file: Optional[Path] = None  # Best version to keep

    def __post_init__(self):
        """Auto-select primary file if not set."""
        if not self.primary_file and self.files:
            # Select newest or most complete file as primary
            self.primary_file = self._select_best_file()

    def _select_best_file(self) -> Path:
        """
        Select the best file to keep.

        Strategy:
        1. Prefer files without version indicators (draft, v1, etc.)
        2. Prefer larger files (more content)
        3. Prefer newer files (modification time)
        """
        scored_files = []

        for file_path in self.files:
            score = 0

            # Penalize version indicators
            name_lower = file_path.stem.lower()
            version_indicators = ['draft', 'v1', 'v2', 'v3', 'copy', 'temp', 'old']
            if not any(indicator in name_lower for indicator in version_indicators):
                score += 100

            # Reward larger files (normalize to 0-50 range)
            size = file_path.stat().st_size
            score += min(size / 1024 / 1024, 50)  # MB

            # Reward newer files (normalize to 0-50 range)
            mtime = file_path.stat().st_mtime
            score += mtime / 1e9  # Normalize timestamp

            scored_files.append((score, file_path))

        # Return file with highest score
        scored_files.sort(reverse=True)
        return scored_files[0][1]

    def get_files_to_remove(self) -> List[Path]:
        """Get files that should be removed (all except primary)."""
        return [f for f in self.files if f != self.primary_file]


class SmartDuplicateDetector:
    """
    Multi-level duplicate detector.

    Detection levels:
    1. EXACT: SHA-256 hash matching (100% identical)
    2. FUZZY: Fuzzy hashing for near-duplicates (requires ssdeep)
    3. SEMANTIC: Embedding-based similarity (requires content extraction)
    4. VERSION: Detect different versions of same document
    """

    def __init__(
        self,
        semantic_threshold: float = 0.95,
        fuzzy_threshold: int = 80,
        enable_fuzzy: bool = True,
        enable_semantic: bool = True,
        embedding_model: str = "nomic-embed-text"
    ):
        self.semantic_threshold = semantic_threshold
        self.fuzzy_threshold = fuzzy_threshold
        self.enable_fuzzy = enable_fuzzy
        self.enable_semantic = enable_semantic

        # Storage for file signatures
        self.exact_hashes: Dict[str, List[Path]] = {}
        self.fuzzy_hashes: Dict[str, List[Path]] = {}
        self.embeddings_cache: Dict[Path, np.ndarray] = {}

        # Initialize embeddings if semantic detection enabled
        if enable_semantic:
            self.embeddings_model = OllamaEmbeddings(model=embedding_model)

    async def detect_duplicates(
        self,
        files: List[Path],
        file_service: Any,  # FileService instance
        detection_levels: Optional[List[DuplicateType]] = None
    ) -> List[DuplicateGroup]:
        """
        Detect duplicates across all files.

        Args:
            files: List of file paths to check
            file_service: FileService for content extraction
            detection_levels: Which detection levels to use (default: all)

        Returns:
            List of duplicate groups
        """
        if detection_levels is None:
            detection_levels = [
                DuplicateType.EXACT,
                DuplicateType.SEMANTIC,
                DuplicateType.VERSION
            ]
            if self.enable_fuzzy:
                detection_levels.append(DuplicateType.FUZZY)

        duplicate_groups = []

        # Level 1: Exact duplicates (fast)
        if DuplicateType.EXACT in detection_levels:
            exact_groups = await self._detect_exact_duplicates(files)
            duplicate_groups.extend(exact_groups)

        # Level 2: Fuzzy duplicates (medium speed)
        if DuplicateType.FUZZY in detection_levels:
            # Only check files not already marked as exact duplicates
            remaining_files = self._get_non_duplicate_files(files, duplicate_groups)
            fuzzy_groups = await self._detect_fuzzy_duplicates(remaining_files)
            duplicate_groups.extend(fuzzy_groups)

        # Level 3: Semantic duplicates (slow, requires content)
        if DuplicateType.SEMANTIC in detection_levels:
            remaining_files = self._get_non_duplicate_files(files, duplicate_groups)
            semantic_groups = await self._detect_semantic_duplicates(
                remaining_files,
                file_service
            )
            duplicate_groups.extend(semantic_groups)

        # Level 4: Version detection (pattern-based)
        if DuplicateType.VERSION in detection_levels:
            remaining_files = self._get_non_duplicate_files(files, duplicate_groups)
            version_groups = await self._detect_versions(remaining_files)
            duplicate_groups.extend(version_groups)

        return duplicate_groups

    async def _detect_exact_duplicates(self, files: List[Path]) -> List[DuplicateGroup]:
        """Detect exact duplicates using SHA-256 hash."""
        hash_groups: Dict[str, List[Path]] = {}

        for file_path in files:
            try:
                file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(file_path)
            except Exception as e:
                print(f"Error hashing {file_path}: {e}")

        # Create duplicate groups (only for hashes with >1 file)
        groups = []
        for file_hash, file_list in hash_groups.items():
            if len(file_list) > 1:
                groups.append(DuplicateGroup(
                    duplicate_type=DuplicateType.EXACT,
                    files=file_list
                ))

        return groups

    async def _detect_fuzzy_duplicates(self, files: List[Path]) -> List[DuplicateGroup]:
        """
        Detect near-duplicates using fuzzy hashing.

        Requires: pip install ssdeep
        """
        try:
            import ssdeep
        except ImportError:
            print("Warning: ssdeep not installed. Skipping fuzzy duplicate detection.")
            return []

        # Compute fuzzy hashes
        fuzzy_hashes: Dict[Path, str] = {}
        for file_path in files:
            try:
                fuzzy_hash = ssdeep.hash_from_file(str(file_path))
                fuzzy_hashes[file_path] = fuzzy_hash
            except Exception as e:
                print(f"Error computing fuzzy hash for {file_path}: {e}")

        # Compare all pairs
        groups = []
        visited = set()

        for file1, hash1 in fuzzy_hashes.items():
            if file1 in visited:
                continue

            similar_files = [file1]
            similarity_scores = {}

            for file2, hash2 in fuzzy_hashes.items():
                if file1 == file2 or file2 in visited:
                    continue

                # Compare fuzzy hashes
                similarity = ssdeep.compare(hash1, hash2)

                if similarity >= self.fuzzy_threshold:
                    similar_files.append(file2)
                    similarity_scores[(file1, file2)] = similarity / 100.0
                    visited.add(file2)

            if len(similar_files) > 1:
                visited.add(file1)
                groups.append(DuplicateGroup(
                    duplicate_type=DuplicateType.FUZZY,
                    files=similar_files,
                    similarity_scores=similarity_scores
                ))

        return groups

    async def _detect_semantic_duplicates(
        self,
        files: List[Path],
        file_service: Any
    ) -> List[DuplicateGroup]:
        """Detect semantically similar documents using embeddings."""
        if not self.enable_semantic:
            return []

        # Extract content and generate embeddings
        embeddings_list = []
        valid_files = []

        for file_path in files:
            try:
                # Extract content
                content = await file_service.extract_pdf_content(file_path)
                if not content:
                    continue

                # Generate embedding
                if file_path not in self.embeddings_cache:
                    embedding = await self.embeddings_model.aembed_query(content[:5000])
                    self.embeddings_cache[file_path] = np.array(embedding)

                embeddings_list.append(self.embeddings_cache[file_path])
                valid_files.append(file_path)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        if len(valid_files) < 2:
            return []

        # Compute similarity matrix
        embeddings_matrix = np.array(embeddings_list)
        similarity_matrix = cosine_similarity(embeddings_matrix)

        # Find similar groups
        groups = []
        visited = set()

        for i, file1 in enumerate(valid_files):
            if file1 in visited:
                continue

            similar_files = [file1]
            similarity_scores = {}

            for j, file2 in enumerate(valid_files):
                if i == j or file2 in visited:
                    continue

                similarity = similarity_matrix[i][j]

                if similarity >= self.semantic_threshold:
                    similar_files.append(file2)
                    similarity_scores[(file1, file2)] = similarity
                    visited.add(file2)

            if len(similar_files) > 1:
                visited.add(file1)
                groups.append(DuplicateGroup(
                    duplicate_type=DuplicateType.SEMANTIC,
                    files=similar_files,
                    similarity_scores=similarity_scores
                ))

        return groups

    async def _detect_versions(self, files: List[Path]) -> List[DuplicateGroup]:
        """
        Detect different versions of same document.

        Pattern matching for:
        - paper_v1.pdf, paper_v2.pdf
        - paper_draft.pdf, paper_final.pdf
        - paper.pdf, paper_copy.pdf
        """
        import re
        from collections import defaultdict

        # Normalize filenames to base form
        base_to_files = defaultdict(list)

        version_patterns = [
            r'[_-]v\d+',           # _v1, -v2
            r'[_-]version\d+',     # _version1
            r'[_-]draft',          # _draft
            r'[_-]final',          # _final
            r'[_-]copy(\d*)',      # _copy, _copy1
            r'[_-]old',            # _old
            r'[_-]new',            # _new
            r'\s*\(\d+\)',         # (1), (2)
        ]

        for file_path in files:
            stem = file_path.stem

            # Remove version indicators
            base_name = stem
            for pattern in version_patterns:
                base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)

            # Normalize
            base_name = base_name.strip('_- ')
            base_to_files[base_name].append(file_path)

        # Create groups for files with same base name
        groups = []
        for base_name, file_list in base_to_files.items():
            if len(file_list) > 1:
                groups.append(DuplicateGroup(
                    duplicate_type=DuplicateType.VERSION,
                    files=file_list
                ))

        return groups

    def _get_non_duplicate_files(
        self,
        all_files: List[Path],
        duplicate_groups: List[DuplicateGroup]
    ) -> List[Path]:
        """Get files that are not in any duplicate group."""
        duplicate_files = set()
        for group in duplicate_groups:
            duplicate_files.update(group.files)

        return [f for f in all_files if f not in duplicate_files]


# ============================================================================
# CLI Command Example
# ============================================================================

async def deduplicate_command(
    directory: Path,
    mode: str = "all",
    threshold: float = 0.95,
    auto_remove: bool = False
):
    """
    Example: Deduplicate command.

    Args:
        directory: Directory to scan
        mode: Detection mode (exact/fuzzy/semantic/version/all)
        threshold: Similarity threshold for semantic detection
        auto_remove: Automatically remove duplicates (keep best version)
    """
    from gideon.services.file_service import FileService

    print(f"Scanning for duplicates in {directory}...")

    file_service = FileService()
    files = file_service.get_files_by_extension(directory, ".pdf")

    print(f"Found {len(files)} files to check.\n")

    # Initialize detector
    detector = SmartDuplicateDetector(
        semantic_threshold=threshold,
        enable_semantic=(mode in ["semantic", "all"]),
        enable_fuzzy=(mode in ["fuzzy", "all"])
    )

    # Detect duplicates
    detection_levels = []
    if mode == "all":
        detection_levels = [DuplicateType.EXACT, DuplicateType.SEMANTIC, DuplicateType.VERSION]
    elif mode == "exact":
        detection_levels = [DuplicateType.EXACT]
    elif mode == "semantic":
        detection_levels = [DuplicateType.SEMANTIC]
    elif mode == "version":
        detection_levels = [DuplicateType.VERSION]

    duplicate_groups = await detector.detect_duplicates(
        files,
        file_service,
        detection_levels
    )

    # Display results
    if not duplicate_groups:
        print("✅ No duplicates found!")
        return

    print(f"Found {len(duplicate_groups)} duplicate groups:\n")

    total_duplicates = 0
    total_space_saved = 0

    for i, group in enumerate(duplicate_groups, 1):
        print(f"Group {i} - {group.duplicate_type.value.upper()}")
        print(f"  Primary (keep): {group.primary_file.name}")
        print(f"  Duplicates ({len(group.files) - 1}):")

        for file_path in group.get_files_to_remove():
            size_mb = file_path.stat().st_size / 1024 / 1024

            # Show similarity score if available
            score_info = ""
            for (f1, f2), score in group.similarity_scores.items():
                if file_path in (f1, f2):
                    score_info = f" (similarity: {score:.2%})"
                    break

            print(f"    - {file_path.name} ({size_mb:.2f} MB){score_info}")
            total_duplicates += 1
            total_space_saved += size_mb

        print()

    print(f"Summary:")
    print(f"  Total duplicate files: {total_duplicates}")
    print(f"  Potential space saved: {total_space_saved:.2f} MB")

    # Auto-remove if requested
    if auto_remove:
        print(f"\nRemoving duplicates...")
        removed = 0
        for group in duplicate_groups:
            for file_path in group.get_files_to_remove():
                try:
                    file_path.unlink()
                    print(f"  ✓ Removed: {file_path.name}")
                    removed += 1
                except Exception as e:
                    print(f"  ✗ Error removing {file_path.name}: {e}")

        print(f"\n✅ Removed {removed} duplicate files!")
    else:
        print(f"\nRun with --auto-remove to delete duplicates.")


# Example usage
if __name__ == "__main__":
    # Example: Detect all types of duplicates
    # asyncio.run(deduplicate_command(
    #     Path("./documents"),
    #     mode="all",
    #     threshold=0.95,
    #     auto_remove=False
    # ))

    pass
