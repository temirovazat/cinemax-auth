import json
import string
from secrets import choice


def generate_random_string(length: int) -> str:
    """Generate a random string.

    Args:
        length: The size of the string.

    Returns:
        str: A string with random letters and digits.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(choice(alphabet) for _ in range(length))


def generate_random_email(length: int, domain: str = 'yandex') -> str:
    """Generate a random email address.

    Args:
        length: The size of the mailbox name.
        domain: The domain name.

    Returns:
        str: An email address composed of a random string and a domain name.
    """
    random_str = generate_random_string(length)
    return '{random_str}@{domain}.com'.format(random_str=random_str, domain=domain)


def decode_json(payload: bytes) -> object:
    """Decode JSON content into an object.

    Args:
        payload: JSON content in bytes.

    Returns:
        object: An object.
    """
    return json.loads(payload.decode('utf-8'))
