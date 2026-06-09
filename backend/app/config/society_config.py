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
    "Member1",
    "Member2",
    "Member3",
    "Member4",
    "Member5",
]

UNIQUE_COMMITTEE_ROLES = [
    "President",
    "Vice President",
    "Secretary",
    "Joint Secretary",
    "Treasurer",
    "Member1",
    "Member2",
    "Member3",
    "Member4",
    "Member5",
]


def get_apartment_name() -> str:
    return os.getenv(
        "APARTMENT_NAME",
        os.getenv("SOCIETY_NAME", "Society")
    ).strip()


def get_apartment_prefix() -> str:
    apartment = get_apartment_name()
    prefix = apartment[:4]
    if len(prefix) < 4:
        prefix = prefix.ljust(4, "0")
    return prefix


def generate_secretary_password() -> str:
    return f"{get_apartment_prefix()}Sec"


def generate_resident_password(flat_number: str) -> str:
    prefix = get_apartment_prefix()
    flat = re.sub(r"\s+", "", flat_number.strip())
    return f"{prefix}{flat}"


def get_towers() -> list[str]:
    raw = os.getenv("TOWERS", "Tower A")
    return [t.strip() for t in raw.split(",") if t.strip()]


def get_floors_count() -> int:
    return int(os.getenv("FLOORS_COUNT", "10"))


def generate_flat_numbers_for_floor(floor: int) -> list[str]:
    """Floor 1 -> 101..119, floor 2 -> 201..219, etc."""
    return [f"{floor}{unit:02d}" for unit in range(1, 20)]


def get_upload_dir() -> str:
    return os.getenv(
        "UPLOAD_DIR",
        os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    )
