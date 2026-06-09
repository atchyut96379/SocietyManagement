from fastapi import APIRouter

from app.config.society_config import (
    COMMITTEE_ROLES,
    RESIDENT_TYPES,
    ROLE_PASSWORD_SUFFIX,
    FLOOR_COUNT,
    get_apartment_name,
    get_apartment_prefix,
)

router = APIRouter(
    prefix="/config",
    tags=["Config"]
)


@router.get("/society")
def society_config():
    return {
        "apartment_name": get_apartment_name(),
        "apartment_prefix": get_apartment_prefix(),
        "committee_roles": COMMITTEE_ROLES,
        "resident_types": RESIDENT_TYPES,
        "role_password_hints": ROLE_PASSWORD_SUFFIX,
        "floor_count": FLOOR_COUNT,
        "flats_per_floor": 18,
    }
