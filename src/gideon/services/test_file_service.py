import pytest
import tempfile
from pathlib import Path
from gideon.services.file_service import FileService


@pytest.fixture
def temp_dir_with_duplicates():
    with tempfile.TemporaryDirectory() as tmpdirname:
        dir_path = Path(tmpdirname)
        file1 = dir_path / "file1.pdf"
        file2 = dir_path / "file2.pdf"
        file3 = dir_path / "file3.pdf"
        file4 = dir_path / "file4.pdf"
        content_a = b"duplicate content"
        content_b = b"unique content"
        file1.write_bytes(content_a)
        file2.write_bytes(content_a)
        file3.write_bytes(content_b)
        file4.write_bytes(content_a)
        yield dir_path


def test_remove_duplicates(temp_dir_with_duplicates):
    dir_path = temp_dir_with_duplicates
    assert len(list(dir_path.glob("*.pdf"))) == 4
    FileService.remove_duplicates(dir_path)
    remaining_files = list(dir_path.glob("*.pdf"))
    assert len(remaining_files) == 2
    contents = set(f.read_bytes() for f in remaining_files)
    assert b"duplicate content" in contents
    assert b"unique content" in contents
