import random, string


def get_random_alphanumeric_string(length) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    result_str = "".join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


def get_random_number(length) -> int:
    smallest_number = 10 ** (length - 1)
    largest_number = (10**length) - 1
    random_numbers = random.randint(smallest_number, largest_number)
    return random_numbers
