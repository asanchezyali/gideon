"""Image OCR extractor."""

from pathlib import Path
from typing import Dict, Any
from PIL import Image
import pytesseract

from .base import BaseExtractor


class ImageOCRExtractor(BaseExtractor):
    """Extractor for images using OCR (.jpg, .jpeg, .png, .tiff, .bmp)."""

    def __init__(self):
        """Initialize OCR extractor."""
        super().__init__()
        # Configure tesseract (can be customized per environment)
        # For production, you might need to set: pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    async def extract_content(self, file_path: Path) -> str:
        """
        Extract text from image using OCR.

        Args:
            file_path: Path to image file

        Returns:
            Extracted text content via OCR

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If OCR fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Open image
            image = Image.open(str(file_path))

            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')

            if not text.strip():
                return "No text detected in image"

            return text.strip()

        except pytesseract.TesseractNotFoundError:
            raise ValueError(
                "Tesseract OCR not found. Please install tesseract-ocr: "
                "Ubuntu/Debian: sudo apt-get install tesseract-ocr "
                "macOS: brew install tesseract "
                "Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )
        except Exception as e:
            raise ValueError(f"Failed to extract text from image {file_path}: {str(e)}")

    async def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from image file.

        Args:
            file_path: Path to image file

        Returns:
            Dictionary containing metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If metadata cannot be extracted
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            image = Image.open(str(file_path))

            metadata = {
                "title": file_path.stem,
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "file_format": "image",
            }

            # Extract EXIF data if available
            try:
                exif = image.getexif()
                if exif:
                    # Common EXIF tags
                    metadata["exif_datetime"] = exif.get(306, "")  # DateTime
                    metadata["exif_make"] = exif.get(271, "")  # Make
                    metadata["exif_model"] = exif.get(272, "")  # Model
            except:
                pass

            return metadata

        except Exception as e:
            raise ValueError(f"Failed to extract metadata from {file_path}: {str(e)}")
