def format_number(num):
    suffixes = ["", "K", "M", "B"]
    if num == 0:
        return "0"

    index = 0
    while num >= 1000 ** (index + 1) and index < len(suffixes) - 1:
        index += 1

    divisor = 1000**index
    quotient = num // divisor
    remainder = num % divisor

    if remainder == 0:
        return f"{quotient}{suffixes[index]}"
    else:
        decimal_part = (remainder * 10) // divisor
        if decimal_part == 0:
            return f"{quotient}{suffixes[index]}"
        else:
            return f"{quotient}.{decimal_part}{suffixes[index]}"
