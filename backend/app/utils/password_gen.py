import os

from dotenv import load_dotenv

load_dotenv()


def generate_resident_password(flat_number: str) -> str:
    """
    Default resident password:
    first 4 characters of apartment/society name + flat number
    Example: ATCHYUT + 408 -> ATCH408
    """
    apartment_name = os.getenv(
        "SOCIETY_NAME",
        "Society"
    ).strip()

    prefix = apartment_name[:4]
    flat = flat_number.strip()

    return f"{prefix}{flat}"
