import re
from typing import List, Tuple, Dict
from decimal import Decimal, ROUND_HALF_UP

# Unit hint patterns and their multipliers
UNIT_PATTERNS = {
    # Thousands (always multiply by 1000)
    r'in\s+thousands': 1000,
    r'\(thousands\)': 1000,
    r'\(hours?\s+in\s+thousands\)': 1000,
    r'\(units?\s+in\s+thousands\)': 1000,
    # Millions
    r'in\s+millions': 1000000,
    r'\(millions\)': 1000000,
    r'\(\$?\s*millions\)': 1000000,
    r'\(\$?\s*M\)': 1000000,
    r'\(dollars?\s+in\s+millions\)': 1000000,
    # Billions (only explicit "Billion" or "Billions")
    r'in\s+billions': 1000000000,
    r'\(billions\)': 1000000000,
    # Currency symbols (only K and M)
    r'\$K': 1000,
    r'\$M': 1000000,
}

# Pattern for matching numbers (including those with commas, dollar signs, and parentheses)
NUMBER_PATTERN = r'[$]?[-]?\(?\d+(?:,\d{3})*(?:\.\d+)?\)?(?:\s*(?:billion|million|thousand|M|K))?'


def is_year(number: int) -> bool:
    """
    Check if a number is likely to be a year.

    Args:
        number (int): The number to check

    Returns:
        bool: True if the number is likely to be a year
    """
    return 1900 <= number <= 2100


def find_unit_hints(text: str) -> List[Tuple[int, int, str]]:
    """
    Find all unit hints in the text and return their positions, multipliers, and context.

    Args:
        text (str): The text to search in

    Returns:
        List[Tuple[int, int, str]]: List of (position, multiplier, context) tuples
    """
    hints = []

    # First, look for the main table header that applies to the whole page
    main_header_patterns = [
        r'\(dollars?\s+in\s+millions\)',
        r'\(dollars?\s+in\s+thousands\)'
    ]
    for main_header_pattern in main_header_patterns:
        main_header_match = re.search(main_header_pattern, text, re.IGNORECASE)
        if main_header_match:
            # If we find the main header, apply it to the whole page and return immediately
            start = 0
            end = len(text)
            context = text[start:end]
            multiplier = 1000000 if 'million' in main_header_pattern else 1000
            hints.append((start, multiplier, context))
            return hints  # Return early since this applies to everything

    # If no main header found, look for other unit hints
    header_patterns = {
        r'\(thousands\)': 1000,
        r'\(hours?\s+in\s+thousands\)': 1000,
        r'\(units?\s+in\s+thousands\)': 1000,
        r'\(millions\)': 1000000,
        r'\(\$?\s*millions\)': 1000000,
        r'\(\$?\s*M\)': 1000000,
        r'\(billions\)': 1000000000,
        r'\(\$?\s*billions\)': 1000000000,
        r'\(\$?\s*B\)': 1000000000,
    }

    # Look for table headers with unit hints
    for pattern, multiplier in header_patterns.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            # Get more context around the match
            start = max(0, match.start() - 200)
            end = min(len(text), match.end() + 200)
            context = text[start:end]

            # Check if this is a count or quantity (don't apply multiplier)
            count_indicators = [
                'number of issues',
                'number of receipts',
                'number of requisitions',
                'items managed',
                'contracts executed',
                'purchase inflation',
                'supply item quantity requirements'
            ]

            # If any count indicator is found in the context, skip this multiplier
            if any(indicator in context.lower() for indicator in count_indicators):
                continue

            # Only apply multiplier if it's in a financial context
            financial_indicators = [
                'dollars', '$', 'funding', 'budget', 'cost', 'expense', 'revenue']
            if any(indicator in context.lower() for indicator in financial_indicators):
                hints.append((match.start(), multiplier, context))

    # Then look for other unit hints (lower priority)
    other_patterns = {
        r'in\s+thousands': 1000,
        r'in\s+millions': 1000000,
        r'in\s+billions': 1000000000,
        r'\$K': 1000,
        r'\$M': 1000000,
        r'\$B': 1000000000
    }

    for pattern, multiplier in other_patterns.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            # Get more context around the match
            start = max(0, match.start() - 200)
            end = min(len(text), match.end() + 200)
            context = text[start:end]

            # Check if this is a count or quantity (don't apply multiplier)
            count_indicators = [
                'number of issues',
                'number of receipts',
                'number of requisitions',
                'items managed',
                'contracts executed',
                'purchase inflation',
                'supply item quantity requirements'
            ]

            # If any count indicator is found in the context, skip this multiplier
            if any(indicator in context.lower() for indicator in count_indicators):
                continue

            # Only apply multiplier if it's in a financial context
            financial_indicators = [
                'dollars', '$', 'funding', 'budget', 'cost', 'expense', 'revenue']
            if any(indicator in context.lower() for indicator in financial_indicators):
                hints.append((match.start(), multiplier, context))

    # Sort hints by position and remove any duplicates or overlapping hints
    sorted_hints = sorted(hints, key=lambda x: x[0])
    filtered_hints = []
    last_end = -1

    for hint in sorted_hints:
        start, multiplier, context = hint
        if start > last_end:  # Only add if it doesn't overlap with previous hint
            filtered_hints.append(hint)
            last_end = start + len(context)

    return filtered_hints


def parse_number(number_str: str) -> Tuple[Decimal, Decimal]:
    """
    Parse a number string and return the number and its multiplier.

    Args:
        number_str (str): The number string to parse

    Returns:
        Tuple[Decimal, Decimal]: (number, multiplier)
    """
    # Extract the unit if present
    unit_multiplier = Decimal('1')
    for unit, mult in {
        'billion': 1000000000,
        'million': 1000000,
        'thousand': 1000
    }.items():
        # Only match if the unit is directly adjacent to the number (no whitespace)
        if re.search(rf'\d+\s*{unit}\b', number_str, re.IGNORECASE):
            unit_multiplier = Decimal(str(mult))
            # Remove the unit from the string
            number_str = re.sub(rf'\s*{unit}\b', '',
                                number_str, flags=re.IGNORECASE).strip()
            break

    # Remove dollar sign and spaces
    number_str = number_str.replace('$', '').strip()

    # Handle negative numbers in parentheses
    if number_str.startswith('(') and number_str.endswith(')'):
        number_str = '-' + number_str[1:-1]
    elif number_str.endswith(')'):
        number_str = number_str[:-1]

    try:
        number = Decimal(number_str.replace(',', ''))
        return number, unit_multiplier
    except:
        numeric_part = re.search(r'[-]?\d+(?:,\d{3})*(?:\.\d+)?', number_str)
        if numeric_part:
            number = Decimal(numeric_part.group().replace(',', ''))
            return number, unit_multiplier
        raise ValueError(f"Could not parse number: {number_str}")


def get_number_context(text: str, number_pos: int) -> str:
    """Get the context around a number (50 characters before and after)."""
    start = max(0, number_pos - 50)
    end = min(len(text), number_pos + 50)
    return text[start:end]


def contexts_overlap(context1: str, context2: str) -> bool:
    """
    Check if two contexts are likely from the same table/section.
    Now less restrictive about table boundaries and more focused on content similarity.
    """
    context1 = context1.lower()
    context2 = context2.lower()

    # Check for major section breaks
    major_breaks = ['\n\n\n', 'page', 'chapter', 'section']
    for break_marker in major_breaks:
        if break_marker in context1 and break_marker in context2:
            return False

    # Get all words from both contexts
    words1 = set(context1.split())
    words2 = set(context2.split())

    # Remove common words that don't indicate content similarity
    common_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'of', 'for',
                    'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
    words1 = words1 - common_words
    words2 = words2 - common_words

    # Find common significant words
    common_words = words1.intersection(words2)

    # If they share any significant words, they're likely in the same section
    return len(common_words) > 0


def extract_numbers_with_local_units(text: str) -> List[Decimal]:
    """
    Extract all numbers from text, applying appropriate unit multipliers.
    Only applies multipliers to dollar amounts.

    Args:
        text (str): The text to process

    Returns:
        List[Decimal]: List of adjusted numbers
    """
    unit_hints = find_unit_hints(text)
    numbers = []
    processed_positions = set()  # Keep track of positions we've already processed

    for match in re.finditer(NUMBER_PATTERN, text):
        start_pos = match.start()
        end_pos = match.end()
        number_str = match.group()

        if start_pos in processed_positions:
            continue

        try:
            number, unit_multiplier = parse_number(number_str)
            if is_year(int(number)):
                continue

            # Get the context around this number (increased context window)
            number_context = get_number_context(text, start_pos)

            # Check if this is a count or quantity (don't apply multiplier)
            count_indicators = [
                'number of issues',
                'number of receipts',
                'number of requisitions',
                'items managed',
                'contracts executed',
                'purchase inflation',
                'supply item quantity requirements'
            ]

            if any(indicator in number_context.lower() for indicator in count_indicators):
                numbers.append(number)
                processed_positions.add(start_pos)
                continue

            # Check if this is a dollar amount (apply multiplier)
            dollar_indicators = [
                '$', 'dollars', 'funding', 'budget', 'cost', 'Cost', 'expense', 'revenue',
                'appropriation', 'allocation', 'expenditure', 'investment',
                'million', 'billion', 'thousand',  # These often indicate dollar amounts
                'total', 'sum', 'amount',  # Common in financial contexts
                'program', 'project', 'initiative'  # Often associated with funding
            ]

            # Apply multiplier if it's a dollar amount or has an explicit unit
            if ('$' in number_str or
                any(indicator in number_context.lower() for indicator in dollar_indicators) or
                    unit_multiplier > 1):  # If it has an explicit unit like "million"

                # Find the nearest preceding unit hint in the same context
                context_multiplier = Decimal('1')
                for hint_pos, hint_mult, hint_context in unit_hints:
                    if hint_pos <= start_pos and contexts_overlap(number_context, hint_context):
                        context_multiplier = Decimal(str(hint_mult))
                        break

                # If the number has an explicit unit (like "million" or "thousand"),
                # use that multiplier. Otherwise, use the context multiplier
                if unit_multiplier > 1:
                    multiplier = unit_multiplier
                else:
                    multiplier = context_multiplier

                # Apply the chosen multiplier
                final_number = number * multiplier
            else:
                # For non-dollar amounts, use the raw number
                final_number = number

            numbers.append(final_number)
            processed_positions.add(start_pos)

        except ValueError:
            continue

    return numbers


def find_max_number(numbers: List[Decimal]) -> Decimal:
    """
    Find the maximum number from a list of numbers.

    Args:
        numbers (List[Decimal]): List of numbers

    Returns:
        Decimal: The maximum number
    """
    if not numbers:
        return Decimal('0')
    return max(numbers)


def format_number(num: Decimal) -> str:
    # 1) Convert to a plain decimal string (no scientific notation)
    num_str = f"{num:f}"

    # 2) Only remove trailing zeros (and a possible trailing dot) if there was a decimal point
    if '.' in num_str:
        num_str = num_str.rstrip('0').rstrip('.')

    # 3) Insert commas into the integer part
    parts = num_str.split('.')
    parts[0] = f"{int(parts[0]):,}"

    # 4) Rejoin (if there was a fractional part) or return just the integer
    return '.'.join(parts)
