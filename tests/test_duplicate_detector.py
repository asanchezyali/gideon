"""Tests for duplicate detector."""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.gideon.services.duplicate_detector import (
    SmartDuplicateDetector,
    DuplicateType,
    DuplicateGroup
)


class TestDuplicateGroup:
    """Test duplicate group."""

    def test_select_best_file(self, tmp_path):
        """Test selecting best file from group."""
        # Create test files
        file1 = tmp_path / "paper.pdf"
        file2 = tmp_path / "paper_v1.pdf"
        file3 = tmp_path / "paper_draft.pdf"

        for f in [file1, file2, file3]:
            f.write_text("content")

        group = DuplicateGroup(
            duplicate_type=DuplicateType.VERSION,
            files=[file1, file2, file3]
        )

        # Should prefer file without version indicators
        assert group.primary_file == file1

    def test_get_files_to_remove(self, tmp_path):
        """Test getting files to remove."""
        file1 = tmp_path / "paper.pdf"
        file2 = tmp_path / "paper_copy.pdf"

        for f in [file1, file2]:
            f.write_text("content")

        group = DuplicateGroup(
            duplicate_type=DuplicateType.VERSION,
            files=[file1, file2],
            primary_file=file1
        )

        to_remove = group.get_files_to_remove()
        assert len(to_remove) == 1
        assert file2 in to_remove


class TestSmartDuplicateDetector:
    """Test smart duplicate detector."""

    @pytest.mark.asyncio
    async def test_detect_exact_duplicates(self, tmp_path):
        """Test detecting exact duplicates."""
        # Create identical files
        content = b"This is test content"
        file1 = tmp_path / "file1.pdf"
        file2 = tmp_path / "file2.pdf"
        file3 = tmp_path / "different.pdf"

        file1.write_bytes(content)
        file2.write_bytes(content)
        file3.write_bytes(b"Different content")

        detector = SmartDuplicateDetector()
        groups = await detector.detect_duplicates(
            [file1, file2, file3],
            [DuplicateType.EXACT]
        )

        assert len(groups) == 1
        assert len(groups[0].files) == 2
        assert file1 in groups[0].files
        assert file2 in groups[0].files

    @pytest.mark.asyncio
    async def test_detect_versions(self, tmp_path):
        """Test detecting version duplicates."""
        # Create version files
        file1 = tmp_path / "paper.pdf"
        file2 = tmp_path / "paper_v1.pdf"
        file3 = tmp_path / "paper_v2.pdf"

        for f in [file1, file2, file3]:
            f.write_text(f"content-{f.name}")

        detector = SmartDuplicateDetector()
        groups = await detector.detect_duplicates(
            [file1, file2, file3],
            [DuplicateType.VERSION]
        )

        assert len(groups) == 1
        assert len(groups[0].files) == 3

    @pytest.mark.asyncio
    async def test_no_duplicates(self, tmp_path):
        """Test when no duplicates exist."""
        file1 = tmp_path / "file1.pdf"
        file2 = tmp_path / "file2.pdf"

        file1.write_text("content1")
        file2.write_text("content2")

        detector = SmartDuplicateDetector()
        groups = await detector.detect_duplicates([file1, file2])

        assert len(groups) == 0
