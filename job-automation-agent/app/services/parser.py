from pypdf import PdfReader
import logging
import os

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return ""

    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return ""
