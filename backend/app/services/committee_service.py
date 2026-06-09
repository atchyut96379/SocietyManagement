from app.config.society_config import COMMITTEE_ROLES, UNIQUE_COMMITTEE_ROLES
from app.database.db import get_connection


def validate_committee_role(role: str, exclude_resident_id: int = None):

    if role not in COMMITTEE_ROLES:
        return {
            "valid": False,
            "message": f"Invalid committee role. Allowed: {', '.join(COMMITTEE_ROLES)}"
        }

    if role in ("None", None, ""):
        return {"valid": True}

    if role not in UNIQUE_COMMITTEE_ROLES:
        return {"valid": True}

    conn = get_connection()
    cursor = conn.cursor()

    if exclude_resident_id:
        cursor.execute(
            """
            SELECT ResidentID, FullName
            FROM Residents
            WHERE CommitteeRole = ? AND ResidentID <> ?
            """,
            (role, exclude_resident_id)
        )
    else:
        cursor.execute(
            """
            SELECT ResidentID, FullName
            FROM Residents
            WHERE CommitteeRole = ?
            """,
            (role,)
        )

    existing = cursor.fetchone()
    conn.close()

    if existing:
        return {
            "valid": False,
            "message": (
                f"{role} is already assigned to {existing[1]}. "
                "Only one person can hold each designation."
            )
        }

    return {"valid": True}
