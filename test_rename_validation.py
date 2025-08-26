#!/usr/bin/env python3
"""Simple test to verify the rename validation functionality."""

from pathlib import Path
from src.gideon.validators.filename_validator import FilenameValidator

def test_filename_validation():
    """Test filename validation with various cases."""
    validator = FilenameValidator()
    
    # Test valid filename format
    valid_filename = "John_Smith.2023.Introduction_to_machine_learning.Machine_Learning.20231215_143000.pdf"
    assert validator.is_valid_format(valid_filename), f"Should be valid: {valid_filename}"
    
    # Test invalid filename format
    invalid_filename = "some_random_file.pdf"
    assert not validator.is_valid_format(invalid_filename), f"Should be invalid: {invalid_filename}"
    
    # Test filename without .pdf extension
    no_pdf_filename = "John_Smith.2023.Introduction_to_machine_learning.Machine_Learning.20231215_143000"
    assert not validator.is_valid_format(no_pdf_filename), f"Should be invalid: {no_pdf_filename}"
    
    print("✓ All filename validation tests passed!")

def test_extract_info():
    """Test extracting information from valid filenames."""
    validator = FilenameValidator()
    
    filename = "John_Smith.2023.Introduction_to_machine_learning.Machine_Learning.20231215_143000.pdf"
    info = validator.extract_info_from_filename(filename)
    
    assert info is not None, "Should extract info from valid filename"
    author, year, title, topic, timestamp = info
    
    assert author == "John_Smith", f"Expected 'John_Smith', got '{author}'"
    assert year == "2023", f"Expected '2023', got '{year}'"
    assert title == "Introduction_to_machine_learning", f"Expected 'Introduction_to_machine_learning', got '{title}'"
    assert topic == "Machine_Learning", f"Expected 'Machine_Learning', got '{topic}'"
    assert timestamp == "20231215_143000", f"Expected '20231215_143000', got '{timestamp}'"
    
    print("✓ All info extraction tests passed!")

if __name__ == "__main__":
    try:
        test_filename_validation()
        test_extract_info()
        print("🎉 All tests passed! The filename validation is working correctly.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)