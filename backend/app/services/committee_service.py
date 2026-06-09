from app.config.society_config import (
    ASSIGNABLE_COMMITTEE_ROLES,
    COMMITTEE_ROLES,
)
from app.database.db import get_connection


def _get_assigned_roles(exclude_resident_id: int | None = None) -> set[str]:
    conn = get_connection()
    cursor = conn.cursor()

    if exclude_resident_id:
        cursor.execute(
            """
            SELECT CommitteeRole
            FROM Residents
            WHERE CommitteeRole IS NOT NULL
              AND CommitteeRole <> 'None'
              AND ResidentID <> ?
            """,
            exclude_resident_id
        )
    else:
        cursor.execute(
            """
            SELECT CommitteeRole
            FROM Residents
            WHERE CommitteeRole IS NOT NULL
              AND CommitteeRole <> 'None'
            """
        )

    assigned = {row[0] for row in cursor.fetchall()}
    conn.close()
    return assigned


def get_available_committee_roles(
    editing_resident_id: int | None = None
) -> list[dict]:
    assigned = _get_assigned_roles(editing_resident_id)

    current_role = None
    if editing_resident_id:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT CommitteeRole FROM Residents WHERE ResidentID = ?",
            editing_resident_id
        )
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            current_role = row[0]

    options = [
        {"value": "None", "label": "Resident"}
    ]

    for role in ASSIGNABLE_COMMITTEE_ROLES:
        if role not in assigned or role == current_role:
            options.append({"value": role, "label": role})

    return options


def validate_committee_role(role: str | None, exclude_resident_id: int | None = None):
    if not role or role == "None":
        return None

    if role == "Secretary":
        return (
            "Secretary is managed by Admin only. "
            "Residents cannot be assigned the Secretary role."
        )

    if role not in COMMITTEE_ROLES:
        return f"Invalid committee role: {role}"

    if role not in ASSIGNABLE_COMMITTEE_ROLES:
        return f"{role} cannot be assigned to residents"

    assigned = _get_assigned_roles(exclude_resident_id)

    if role in assigned:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ResidentID, FullName
            FROM Residents WHERE CommitteeRole = ?
            """,
            (role,)
        )
        existing = cursor.fetchone()
        conn.close()

        if existing:
            return (
                f"{role} is already assigned to "
                f"{existing[1]} (ID {existing[0]})"
            )

    return None
