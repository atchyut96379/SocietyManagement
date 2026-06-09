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
    "Member 1",
    "Member 2",
    "Member 3",
    "Member 4",
    "Member 5",
]

# Secretary is created by Admin as system user — not assignable to residents
ASSIGNABLE_COMMITTEE_ROLES = [
    "President",
    "Vice President",
    "Joint Secretary",
    "Treasurer",
    "Member 1",
    "Member 2",
    "Member 3",
    "Member 4",
    "Member 5",
]

ROLE_PASSWORD_SUFFIX = {
    "Secretary": "Sec",
    "President": "Pre",
    "Vice President": "VIC",
    "Joint Secretary": "JOI",
    "Treasurer": "TRE",
    "Member 1": "ME1",
    "Member 2": "ME2",
    "Member 3": "ME3",
    "Member 4": "ME4",
    "Member 5": "ME5",
}

RESIDENT_TYPES = ["Owner", "Tenant"]

FLOOR_COUNT = 5
TOWER_NAME = "Tower A"


def get_apartment_prefix() -> str:
    name = os.getenv("APARTMENT_NAME", "Society").strip()
    prefix = name[:4]
    if len(prefix) < 4:
        prefix = prefix.ljust(4, "0")
    return prefix


def get_apartment_name() -> str:
    return os.getenv("APARTMENT_NAME", "Society").strip()


def get_society_registration_number() -> str:
    return os.getenv("SOCIETY_REG_NO", "").strip()


def get_society_address() -> str:
    return os.getenv("SOCIETY_ADDRESS", "").strip()


def get_floor_flat_numbers(floor: int) -> list[str]:
    base = floor * 100
    flats = [str(base + i) for i in range(1, 9)]
    flats.append(f"{base + 9}/{base + 10}")
    flats.extend(str(base + i) for i in range(11, 20))
    return flats


def get_all_flat_numbers() -> list[str]:
    result = []
    for floor in range(1, FLOOR_COUNT + 1):
        result.extend(get_floor_flat_numbers(floor))
    return result


def flat_password_part(flat_number: str) -> str:
    return re.sub(r"\D", "", flat_number.split("/")[0])


def generate_password(
    committee_role: str | None = None,
    flat_number: str | None = None,
    is_secretary_account: bool = False,
) -> str:
    prefix = get_apartment_prefix()

    if is_secretary_account:
        return f"{prefix}Sec"

    if committee_role and committee_role in ROLE_PASSWORD_SUFFIX:
        return f"{prefix}{ROLE_PASSWORD_SUFFIX[committee_role]}"

    if flat_number:
        return f"{prefix}{flat_password_part(flat_number)}"

    return f"{prefix}0000"


def generate_resident_password(flat_number: str) -> str:
    return generate_password(flat_number=flat_number)


def generate_guard_password() -> str:
    return f"{get_apartment_prefix()}GUA"
