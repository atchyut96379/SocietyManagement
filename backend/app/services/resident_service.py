from app.config.society_config import RESIDENT_TYPES
from app.database.db import get_connection
from app.services.committee_service import validate_committee_role
from app.services.flat_service import (
    get_flat_by_id,
    mark_flat_occupied,
    mark_flat_vacant,
)
from app.services.resident_resolver import normalize_phone
from app.services.user_service import create_resident_account


def _sync_user_resident_links():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ResidentID, PhoneNumber, FullName FROM Residents"
    )
    residents = cursor.fetchall()
    all_users = _load_all_users()

    for resident_id, resident_phone, resident_name in residents:
        best_user_id = None
        best_priority = 99

        for (
            user_id,
            user_resident_id,
            user_phone,
            user_name,
            role_name,
            role_id,
        ) in all_users:
            matched = False

            if normalize_phone(user_phone) == normalize_phone(resident_phone):
                matched = True
            elif (
                (user_name or "").strip().lower()
                == (resident_name or "").strip().lower()
            ):
                matched = True

            if not matched:
                continue

            priority = _role_id_priority(role_id)
            if priority < best_priority:
                best_priority = priority
                best_user_id = user_id

        if not best_user_id:
            continue

        cursor.execute(
            """
            UPDATE Users
            SET ResidentID = NULL
            WHERE ResidentID = ? AND UserID <> ?
            """,
            (resident_id, best_user_id)
        )
        cursor.execute(
            """
            UPDATE Users
            SET ResidentID = ?
            WHERE UserID = ?
            """,
            (resident_id, best_user_id)
        )

    conn.commit()
    conn.close()


SYSTEM_ROLES = frozenset({"Admin", "Secretary", "Security"})

ROLE_ID_PRIORITY = {
    1: 0,
    4: 1,
    3: 2,
    2: 3,
}

CANONICAL_ROLE_NAMES = {
    1: "Admin",
    4: "Secretary",
    3: "Security",
    2: "Resident",
}


def _role_id_priority(role_id: int | None) -> int:
    if not role_id:
        return 99
    return ROLE_ID_PRIORITY.get(int(role_id), 50)


def _canonical_role_name(role_id: int, role_name: str) -> str:
    return CANONICAL_ROLE_NAMES.get(int(role_id), role_name)


def _load_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            u.UserID,
            u.ResidentID,
            u.PhoneNumber,
            u.FullName,
            rl.RoleName,
            u.RoleID
        FROM Users u
        INNER JOIN Roles rl ON u.RoleID = rl.RoleID
        """
    )

    users = cursor.fetchall()
    conn.close()
    return users


def _resolve_login_role(
    resident_id: int,
    phone_number: str,
    full_name: str,
    all_users,
) -> str | None:
    resident_phone = normalize_phone(phone_number)
    resident_name = (full_name or "").strip().lower()

    best_role_id = None
    best_role_name = None
    best_priority = 99

    for (
        user_id,
        user_resident_id,
        user_phone,
        user_name,
        role_name,
        role_id,
    ) in all_users:
        matched = False

        if user_resident_id and int(user_resident_id) == resident_id:
            matched = True
        elif (
            resident_phone
            and normalize_phone(user_phone) == resident_phone
        ):
            matched = True
        elif (
            resident_name
            and (user_name or "").strip().lower() == resident_name
        ):
            matched = True

        if not matched:
            continue

        priority = _role_id_priority(role_id)
        if priority < best_priority:
            best_priority = priority
            best_role_id = role_id
            best_role_name = role_name

    if best_role_id is None:
        return None

    return _canonical_role_name(best_role_id, best_role_name)


def _display_role(
    login_role: str | None,
    committee_role: str | None,
) -> str:
    if login_role in SYSTEM_ROLES:
        return login_role

    if committee_role and committee_role not in (None, "None"):
        return committee_role

    if login_role:
        return login_role

    return "Resident"


def _normalize_committee_role(role):
    if not role or role == "None":
        return None
    return role


def _validate_resident_type(resident_type: str):
    if resident_type not in RESIDENT_TYPES:
        return f"Resident type must be one of: {', '.join(RESIDENT_TYPES)}"
    return None


def create_resident(resident):
    type_error = _validate_resident_type(resident.resident_type)
    if type_error:
        return {"success": False, "message": type_error}

    role_error = validate_committee_role(resident.committee_role)
    if role_error:
        return {"success": False, "message": role_error}

    flat = get_flat_by_id(resident.flat_id)
    if not flat:
        return {"success": False, "message": "Flat not found"}

    if flat["is_occupied"]:
        return {"success": False, "message": "Flat is already occupied"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO Residents
        (
            FullName,
            FlatNumber,
            PhoneNumber,
            Email,
            TowerName,
            IsOwner,
            CommitteeRole,
            FlatID,
            ResidentType,
            OwnerName
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            resident.full_name,
            flat["flat_number"],
            resident.phone_number,
            resident.email,
            flat["tower_name"],
            1 if resident.resident_type == "Owner" else 0,
            _normalize_committee_role(resident.committee_role),
            resident.flat_id,
            resident.resident_type,
            None,
        )
    )

    cursor.execute("SELECT @@IDENTITY")
    resident_id = int(cursor.fetchone()[0])

    conn.commit()
    conn.close()

    mark_flat_occupied(resident.flat_id, resident_id)

    return {
        "success": True,
        "message": "Resident created successfully",
        "resident_id": resident_id
    }


def create_resident_with_login(resident):
    result = create_resident(resident)
    if not result.get("success"):
        return result

    flat = get_flat_by_id(resident.flat_id)

    login_result = create_resident_account(
        resident_id=result["resident_id"],
        phone_number=resident.phone_number,
        email=resident.email,
        full_name=resident.full_name,
        committee_role=resident.committee_role,
        flat_number=flat["flat_number"],
    )

    if not login_result.get("success"):
        delete_resident(result["resident_id"])
        return login_result

    result.update(login_result)
    return result


def get_all_residents():
    _sync_user_resident_links()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.ResidentID,
            r.FullName,
            r.FlatNumber,
            r.PhoneNumber,
            r.Email,
            r.TowerName,
            r.IsOwner,
            r.CommitteeRole,
            r.FlatID,
            r.ResidentType,
            r.OwnerName,
            f.IsOccupied
        FROM Residents r
        LEFT JOIN Flats f ON r.FlatID = f.FlatID
        ORDER BY r.FlatNumber
    """)

    residents = cursor.fetchall()
    conn.close()

    all_users = _load_all_users()

    return [
        {
            "resident_id": row[0],
            "full_name": row[1],
            "flat_number": row[2],
            "phone_number": row[3],
            "email": row[4],
            "tower_name": row[5],
            "is_owner": bool(row[6]),
            "committee_role": row[7] or "None",
            "flat_id": row[8],
            "resident_type": row[9] or ("Owner" if row[6] else "Tenant"),
            "owner_name": row[10],
            "is_occupied": bool(row[11]) if row[11] is not None else True,
            "login_role": (
                login_role := _resolve_login_role(
                    row[0],
                    row[3],
                    row[1],
                    all_users,
                )
            ),
            "role": _display_role(
                login_role,
                row[7] or "None",
            ),
        }
        for row in residents
    ]


def get_resident_by_id(resident_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ResidentID, FullName, FlatNumber, PhoneNumber, Email,
            TowerName, IsOwner, CommitteeRole, FlatID, ResidentType, OwnerName
        FROM Residents
        WHERE ResidentID = ?
    """, resident_id)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"message": "Resident not found"}

    all_users = _load_all_users()
    login_role = _resolve_login_role(
        row[0],
        row[3],
        row[1],
        all_users,
    )

    return {
        "resident_id": row[0],
        "full_name": row[1],
        "flat_number": row[2],
        "phone_number": row[3],
        "email": row[4],
        "tower_name": row[5],
        "is_owner": bool(row[6]),
        "committee_role": row[7] or "None",
        "flat_id": row[8],
        "resident_type": row[9] or ("Owner" if row[6] else "Tenant"),
        "owner_name": row[10],
        "login_role": login_role,
        "role": _display_role(login_role, row[7] or "None"),
    }


def delete_resident(resident_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT FlatID FROM Residents WHERE ResidentID = ?",
        resident_id
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "Resident not found"}

    flat_id = row[0]

    cursor.execute("DELETE FROM Users WHERE ResidentID = ?", resident_id)
    cursor.execute("DELETE FROM Vehicles WHERE ResidentID = ?", resident_id)
    cursor.execute("DELETE FROM Residents WHERE ResidentID = ?", resident_id)

    conn.commit()
    conn.close()

    if flat_id:
        mark_flat_vacant(flat_id)

    return {
        "success": True,
        "message": "Resident deleted successfully"
    }


def update_resident(resident_id, resident):
    type_error = _validate_resident_type(resident.resident_type)
    if type_error:
        return {"success": False, "message": type_error}

    role_error = validate_committee_role(
        resident.committee_role,
        exclude_resident_id=resident_id
    )
    if role_error:
        return {"success": False, "message": role_error}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ResidentID, FlatID FROM Residents WHERE ResidentID = ?",
        resident_id
    )

    if not cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Resident not found"}

    cursor.execute("""
        UPDATE Residents
        SET
            FullName = ?,
            PhoneNumber = ?,
            Email = ?,
            IsOwner = ?,
            CommitteeRole = ?,
            ResidentType = ?
        WHERE ResidentID = ?
    """,
    (
        resident.full_name,
        resident.phone_number,
        resident.email,
        1 if resident.resident_type == "Owner" else 0,
        _normalize_committee_role(resident.committee_role),
        resident.resident_type,
        resident_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Resident updated successfully"
    }


def transfer_committee_role(resident_id: int, committee_role: str):
    role_error = validate_committee_role(
        committee_role,
        exclude_resident_id=resident_id
    )
    if role_error:
        return {"success": False, "message": role_error}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ResidentID FROM Residents WHERE ResidentID = ?",
        resident_id
    )

    if not cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Resident not found"}

    if committee_role and committee_role != "None":
        cursor.execute(
            """
            UPDATE Residents
            SET CommitteeRole = NULL
            WHERE CommitteeRole = ? AND ResidentID <> ?
            """,
            (committee_role, resident_id)
        )

    cursor.execute(
        """
        UPDATE Residents
        SET CommitteeRole = ?
        WHERE ResidentID = ?
        """,
        (
            _normalize_committee_role(committee_role),
            resident_id
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Committee role updated to {committee_role}"
    }
