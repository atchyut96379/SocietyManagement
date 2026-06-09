import os
import re

from dotenv import load_dotenv

load_dotenv()

COMMITTEE_ROLES = [
    "None",
    "President",
    "Vice President",
    "Secretary",
    "Joint Secretary",
    "Treasurer",
]


def get_apartment_name() -> str:
    return os.getenv(
        "APARTMENT_NAME",
        "Society"
    ).strip()


def generate_resident_password(flat_number: str) -> str:
    apartment = get_apartment_name()
    prefix = apartment[:4]

    if len(prefix) < 4:
        prefix = prefix.ljust(4, "0")

    flat = re.sub(r"\s+", "", flat_number.strip())

    return f"{prefix}{flat}"
