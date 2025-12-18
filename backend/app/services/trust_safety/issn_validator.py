"""
ISSN Validation Utilities.

ISSN (International Standard Serial Number) format: ####-####
- First 7 digits are the identifier
- Last digit is a check digit (0-9 or X)
- Check digit calculated using modulo 11
"""

import re
from typing import Optional


def validate_issn_format(issn: Optional[str]) -> bool:
    """
    Validate ISSN format (####-####).

    Args:
        issn: ISSN string to validate

    Returns:
        True if format is valid, False otherwise

    Examples:
        >>> validate_issn_format("0028-0836")  # Nature
        True
        >>> validate_issn_format("1234-567X")  # With X check digit
        True
        >>> validate_issn_format("invalid")
        False
    """
    if not issn:
        return False

    # Remove any whitespace
    issn = issn.strip()

    # ISSN format: ####-#### where last digit can be X
    pattern = r"^\d{4}-\d{3}[\dX]$"
    return bool(re.match(pattern, issn, re.IGNORECASE))


def validate_issn_checksum(issn: Optional[str]) -> bool:
    """
    Validate ISSN check digit using modulo 11 algorithm.

    The check digit is calculated by:
    1. Multiply each of the first 7 digits by weights 8,7,6,5,4,3,2
    2. Sum the products
    3. Remainder of sum / 11 determines check digit
    4. If remainder is 0, check digit is 0
    5. If remainder is 1, check digit is X (represents 10)
    6. Otherwise, check digit is (11 - remainder)

    Args:
        issn: ISSN string to validate

    Returns:
        True if check digit is valid, False otherwise

    Examples:
        >>> validate_issn_checksum("0028-0836")  # Nature - valid
        True
        >>> validate_issn_checksum("0000-0001")  # Invalid checksum
        False
    """
    if not validate_issn_format(issn):
        return False

    # Remove hyphen and convert to uppercase (for X)
    digits = issn.replace("-", "").upper()

    # Calculate weighted sum of first 7 digits
    weights = [8, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(digits[:7], weights))

    # Calculate expected check digit
    remainder = total % 11
    if remainder == 0:
        expected_check = "0"
    elif remainder == 1:
        expected_check = "X"
    else:
        expected_check = str(11 - remainder)

    # Compare with actual check digit
    actual_check = digits[7]

    return actual_check == expected_check


def normalize_issn(issn: Optional[str]) -> Optional[str]:
    """
    Normalize ISSN to standard format (####-####).

    Args:
        issn: ISSN string in any format

    Returns:
        Normalized ISSN or None if invalid

    Examples:
        >>> normalize_issn("00280836")
        "0028-0836"
        >>> normalize_issn("0028-0836")
        "0028-0836"
        >>> normalize_issn("0028 0836")
        "0028-0836"
    """
    if not issn:
        return None

    # Remove all non-alphanumeric characters
    cleaned = re.sub(r"[^0-9Xx]", "", issn.upper())

    if len(cleaned) != 8:
        return None

    # Format as ####-####
    return f"{cleaned[:4]}-{cleaned[4:]}"


def extract_issns_from_list(issn_list: Optional[list]) -> list[str]:
    """
    Extract and validate ISSNs from a list (e.g., from OpenAlex).

    Args:
        issn_list: List of ISSN strings

    Returns:
        List of valid, normalized ISSNs

    Examples:
        >>> extract_issns_from_list(["0028-0836", "invalid", "1234-567X"])
        ["0028-0836", "1234-567X"]
    """
    if not issn_list:
        return []

    valid_issns = []
    for issn in issn_list:
        normalized = normalize_issn(issn)
        if normalized and validate_issn_format(normalized):
            valid_issns.append(normalized)

    return valid_issns
