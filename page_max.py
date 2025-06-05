import sys
import os
from utils.pdf_text_extractor import extract_text_from_pdf
from utils.number_parser import extract_numbers_with_local_units, find_max_number, format_number


def main():
    if len(sys.argv) != 2:
        print("Usage: python page_max.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Check if file is a PDF
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: File must be a PDF: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        # Extract text from all pages
        pages = extract_text_from_pdf(pdf_path)

        if not pages:
            print("Error: No text content found in PDF", file=sys.stderr)
            sys.exit(1)

        # Process each page and find the maximum number
        print("\nLargest numbers per page:")
        print("-" * 40)
        print("Page | Largest Number")
        print("-" * 40)

        for i, page in enumerate(pages, 1):
            numbers = extract_numbers_with_local_units(page)
            if numbers:
                max_number = find_max_number(numbers)
                print(f"{i:4d} | {format_number(max_number)}")
            else:
                print(f"{i:4d} | No numbers found")

        print("-" * 40)

    except Exception as e:
        print(f"Error processing PDF: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
