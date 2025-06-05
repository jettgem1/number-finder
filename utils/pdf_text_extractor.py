from typing import List
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract text from each page of a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        List[str]: List of strings, where each string represents the text content of a page
    """
    pages = []
    for page_layout in extract_pages(pdf_path):
        page_text = ""
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                page_text += element.get_text()
        pages.append(page_text)
    return pages
