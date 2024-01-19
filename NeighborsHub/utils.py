import random
import string


def create_mobile_otp(length: int = 5) -> str:
    valid_characters = '0123456789'
    random_string = ''.join(random.choice(valid_characters) for _ in range(length))
    return random_string


def create_random_chars(length: int = 13) -> str:
    valid_characters = string.ascii_lowercase + string.ascii_uppercase
    random_string = ''.join(random.choice(valid_characters) for _ in range(length))
    return random_string
