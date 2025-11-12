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
            # Open image with context manager to ensure proper cleanup
            with Image.open(str(file_path)) as image:
                # Convert RGBA to RGB if needed (tesseract doesn't handle alpha channel well)
                if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                    # Create white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background

                # Perform OCR
                text = pytesseract.image_to_string(image, lang='eng')

            if not text.strip():
                return "No text detected in image"

            return text.strip()

        except pytesseract.TesseractNotFoundError:
            raise ValueError(
                "Tesseract OCR not found. Please install tesseract-ocr:\n"
                "  Ubuntu/Debian: sudo apt-get install tesseract-ocr\n"
                "  macOS: brew install tesseract\n"
                "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )
        except OSError as e:
            raise ValueError(f"Failed to open image {file_path}: {str(e)}")
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
            with Image.open(str(file_path)) as image:
                metadata = {
                    "title": file_path.stem,
                    "width": image.width,
                    "height": image.height,
                    "format": image.format,
                    "mode": image.mode,
                    "file_format": "image",
                    "file_size_bytes": file_path.stat().st_size,
                }

                # Extract EXIF data if available
                try:
                    exif = image.getexif()
                    if exif:
                        # Common EXIF tags
                        datetime_val = exif.get(306, "")
                        if datetime_val:
                            metadata["exif_datetime"] = datetime_val
                        make_val = exif.get(271, "")
                        if make_val:
                            metadata["exif_make"] = make_val
                        model_val = exif.get(272, "")
                        if model_val:
                            metadata["exif_model"] = model_val
                except (AttributeError, KeyError, TypeError) as e:
                    # EXIF not available or corrupted, ignore
                    pass

            return metadata

        except OSError as e:
            raise ValueError(f"Failed to open image {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from {file_path}: {str(e)}")
