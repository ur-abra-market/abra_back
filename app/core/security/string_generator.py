import secrets
import string


def generate_random_password(length: int = 12):
    """Generates a password from random characters. Uses letters,
    numbers and punctuation marks.

    Args:
        length (int, optional): Password length. Defaults to 12.

    Returns:
        str: Generated password
    """

    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    return password
