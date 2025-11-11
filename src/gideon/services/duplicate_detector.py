"""Smart duplicate detection system."""

from pathlib import Path
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import asyncio

from ..utils.logging import log_info, log_success, log_error


class DuplicateType(Enum):
    """Types of duplicate detection."""
    EXACT = "exact"              # Identical files (hash match)
    VERSION = "version"          # Different versions of same document


@dataclass
class DuplicateGroup:
    """Group of duplicate files."""
    duplicate_type: DuplicateType
    files: List[Path]
    primary_file: Path = None

    def __post_init__(self):
        """Auto-select primary file if not set."""
        if not self.primary_file and self.files:
            self.primary_file = self._select_best_file()

    def _select_best_file(self) -> Path:
        """
        Select the best file to keep.

        Strategy:
        1. Prefer files without version indicators
        2. Prefer larger files
        3. Prefer newer files
        """
        scored_files = []

        for file_path in self.files:
            score = 0

            # Penalize version indicators
            name_lower = file_path.stem.lower()
            version_indicators = ['draft', 'v1', 'v2', 'v3', 'copy', 'temp', 'old']
            if not any(indicator in name_lower for indicator in version_indicators):
                score += 100

            # Reward larger files
            size = file_path.stat().st_size
            score += min(size / 1024 / 1024, 50)

            # Reward newer files
            mtime = file_path.stat().st_mtime
            score += mtime / 1e9

            scored_files.append((score, file_path))

        scored_files.sort(reverse=True)
        return scored_files[0][1]

    def get_files_to_remove(self) -> List[Path]:
        """Get files that should be removed."""
        return [f for f in self.files if f != self.primary_file]


class SmartDuplicateDetector:
    """
    Multi-level duplicate detector.

    Detection levels:
    1. EXACT: SHA-256 hash matching (100% identical)
    2. VERSION: Pattern-based version detection
    """

    def __init__(self):
        self.exact_hashes: Dict[str, List[Path]] = {}

    async def detect_duplicates(
        self,
        files: List[Path],
        detection_levels: List[DuplicateType] = None
    ) -> List[DuplicateGroup]:
        """
        Detect duplicates across all files.

        Args:
            files: List of file paths to check
            detection_levels: Which detection levels to use

        Returns:
            List of duplicate groups
        """
        if detection_levels is None:
            detection_levels = [DuplicateType.EXACT, DuplicateType.VERSION]

        duplicate_groups = []

        # Level 1: Exact duplicates
        if DuplicateType.EXACT in detection_levels:
            exact_groups = await self._detect_exact_duplicates(files)
            duplicate_groups.extend(exact_groups)

        # Level 2: Version detection
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
                log_error(f"Error hashing {file_path}: {e}")

        # Create duplicate groups
        groups = []
        for file_hash, file_list in hash_groups.items():
            if len(file_list) > 1:
                groups.append(DuplicateGroup(
                    duplicate_type=DuplicateType.EXACT,
                    files=file_list
                ))

        return groups

    async def _detect_versions(self, files: List[Path]) -> List[DuplicateGroup]:
        """Detect different versions of same document."""
        import re
        from collections import defaultdict

        base_to_files = defaultdict(list)

        version_patterns = [
            r'[_-]v\d+',
            r'[_-]version\d+',
            r'[_-]draft',
            r'[_-]final',
            r'[_-]copy(\d*)',
            r'[_-]old',
            r'[_-]new',
            r'\s*\(\d+\)',
        ]

        for file_path in files:
            stem = file_path.stem

            # Remove version indicators
            base_name = stem
            for pattern in version_patterns:
                base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)

            base_name = base_name.strip('_- ')
            base_to_files[base_name].append(file_path)

        # Create groups
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
