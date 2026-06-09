import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException

from app.auth.auth_bearer import verify_token

load_dotenv()

ADMIN_ROLE = 1
RESIDENT_ROLE = 2
SECURITY_ROLE = 3
SECRETARY_ROLE = 4

MANAGEMENT_ROLES = (SECRETARY_ROLE,)
STAFF_ROLES = (SECRETARY_ROLE, SECURITY_ROLE)


def require_admin(user=Depends(verify_token)):
    if user.get("role_id") != ADMIN_ROLE:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user


def require_secretary(user=Depends(verify_token)):
    if user.get("role_id") != SECRETARY_ROLE:
        raise HTTPException(
            status_code=403,
            detail="Secretary access required"
        )
    return user


def require_management(user=Depends(verify_token)):
    if user.get("role_id") not in MANAGEMENT_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Secretary access required"
        )
    return user


def require_staff(user=Depends(verify_token)):
    if user.get("role_id") not in STAFF_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    return user


def require_resident(user=Depends(verify_token)):
    if user.get("role_id") != RESIDENT_ROLE:
        raise HTTPException(
            status_code=403,
            detail="Resident access required"
        )

    from app.services.resident_resolver import resolve_resident_id

    resident_id = resolve_resident_id(user)
    if not resident_id:
        raise HTTPException(
            status_code=403,
            detail="Resident account is not linked to a flat"
        )

    user["resident_id"] = resident_id
    return user


def require_admin_or_resident(user=Depends(verify_token)):
    role_id = user.get("role_id")
    if role_id not in (ADMIN_ROLE, RESIDENT_ROLE):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    return user
