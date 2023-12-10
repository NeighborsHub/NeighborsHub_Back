import random


def create_mobile_otp(length: int = 5) -> str:
    valid_characters = '0123456789'
    random_string = ''.join(random.choice(valid_characters) for _ in range(length))
    return random_string
