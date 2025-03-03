def format_number(n: int) -> str:
    """
    Format a number to a human-readable format.

    Args
    ----
    n : int
        The number to format.

    Returns
    -------
    str
        The formatted number as a string.
    """

    suffixes = ["", "K", "M", "B"]
    if n == 0:
        return "0"

    index = 0
    while n >= 1000 ** (index + 1) and index < len(suffixes) - 1:
        index += 1

    divisor = 1000**index
    quotient = n // divisor
    remainder = n % divisor

    if remainder == 0:
        return f"{quotient}{suffixes[index]}"
    else:
        decimal_part = (remainder * 10) // divisor
        if decimal_part == 0:
            return f"{quotient}{suffixes[index]}"
        else:
            return f"{quotient}.{decimal_part}{suffixes[index]}"
