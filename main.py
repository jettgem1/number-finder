import sys
import os
from utils.pdf_text_extractor import extract_text_from_pdf
from utils.number_parser import extract_numbers_with_local_units, find_max_number, format_number, parse_number, NUMBER_PATTERN, is_year
from decimal import Decimal
import re
import decimal


def main():
    if len(sys.argv) != 2:
        print("Usage: python page_max.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    maxi = Decimal('0')  # Initialize with Decimal zero
    max_raw = Decimal('0')  # Initialize largest raw number

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

        for i, page in enumerate(pages, 1):
            # Get adjusted numbers (with multipliers)
            adjusted_numbers = extract_numbers_with_local_units(page)
            if adjusted_numbers:
                max_number = find_max_number(adjusted_numbers)
                print(format_number(max_number))
                if max_number > maxi:
                    maxi = max_number

            raw_numbers = []
            for match in re.finditer(NUMBER_PATTERN, page):
                try:
                    number, _ = parse_number(match.group())
                    if number > 0:
                        raw_numbers.append(number)
                except (ValueError, decimal.InvalidOperation):
                    continue

            if raw_numbers:
                page_raw_max = find_max_number(raw_numbers)
                if page_raw_max > max_raw:
                    max_raw = page_raw_max

        print(f"\nLargest raw number found: {format_number(max_raw)}")
        print(f"Largest number after unit adjustments: {format_number(maxi)}")
        return maxi

    except Exception as e:
        print(f"Error processing PDF: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
