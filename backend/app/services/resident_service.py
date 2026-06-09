import json

from app.config.society_config import generate_resident_password
from app.database.db import get_connection
from app.services.committee_service import validate_committee_role
from app.services.flat_service import get_flat_by_id, mark_flat_occupied


def _normalize_committee_role(role):
    if not role or role == "None":
        return None
    return role


def _parse_vehicles(raw):
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [raw] if raw else []


def _resident_row_to_dict(row):
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
        "owner_name": row[9],
        "vehicle_details": _parse_vehicles(row[10]),
        "profile_completed": bool(row[11])
    }


_RESIDENT_SELECT = """
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
        r.OwnerName,
        r.VehicleDetails,
        r.ProfileCompleted
    FROM Residents r
"""


def create_resident(resident):

    flat = get_flat_by_id(resident.flat_id)
    if not flat:
        return {"success": False, "message": "Flat not found"}

    if flat["is_occupied"]:
        return {"success": False, "message": "Flat is already occupied"}

    role_check = validate_committee_role(resident.committee_role)
    if not role_check["valid"]:
        return {"success": False, "message": role_check["message"]}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO Residents
        (FullName, FlatNumber, PhoneNumber, Email, TowerName, IsOwner, CommitteeRole, FlatID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            resident.full_name,
            flat["flat_number"],
            resident.phone_number,
            resident.email,
            flat["tower_name"],
            resident.is_owner,
            _normalize_committee_role(resident.committee_role),
            resident.flat_id
        )
    )

    conn.commit()
    conn.close()

    mark_flat_occupied(resident.flat_id, True)

    return {"success": True, "message": "Resident created successfully"}


def create_resident_with_login(data):

    result = create_resident(data)
    if not result.get("success"):
        return result

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT TOP 1 ResidentID FROM Residents
        WHERE FlatID = ? AND PhoneNumber = ?
        ORDER BY ResidentID DESC
        """,
        (data.flat_id, data.phone_number)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "Failed to create resident"}

    from app.services.user_service import create_resident_account_auto

    login_result = create_resident_account_auto(row[0])

    return {
        "success": login_result.get("success", False),
        "message": login_result.get("message", ""),
        "resident_id": row[0],
        "phone_number": login_result.get("phone_number"),
        "default_password": login_result.get("password"),
        "flat_number": get_flat_by_id(data.flat_id)["flat_number"]
    }


def get_all_residents():

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(_RESIDENT_SELECT + " ORDER BY r.ResidentID")
    residents = cursor.fetchall()
    conn.close()

    return [_resident_row_to_dict(row) for row in residents]


def get_resident_by_id(resident_id):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(_RESIDENT_SELECT + " WHERE r.ResidentID = ?", (resident_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"message": "Resident not found"}

    return _resident_row_to_dict(row)


def delete_resident(resident_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT FlatID FROM Residents WHERE ResidentID = ?",
        (resident_id,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "Resident not found"}

    flat_id = row[0]

    cursor.execute("DELETE FROM Users WHERE ResidentID = ?", (resident_id,))
    cursor.execute("DELETE FROM Residents WHERE ResidentID = ?", (resident_id,))

    conn.commit()
    conn.close()

    if flat_id:
        mark_flat_occupied(flat_id, False)

    return {"success": True, "message": "Resident deleted successfully"}


def update_resident(resident_id, resident):

    role_check = validate_committee_role(
        resident.committee_role,
        exclude_resident_id=resident_id
    )
    if not role_check["valid"]:
        return {"success": False, "message": role_check["message"]}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ResidentID FROM Residents WHERE ResidentID = ?",
        (resident_id,)
    )
    if not cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Resident not found"}

    cursor.execute(
        """
        UPDATE Residents
        SET
            FullName = ?,
            PhoneNumber = ?,
            Email = ?,
            IsOwner = ?,
            CommitteeRole = ?
        WHERE ResidentID = ?
        """,
        (
            resident.full_name,
            resident.phone_number,
            resident.email,
            resident.is_owner,
            _normalize_committee_role(resident.committee_role),
            resident_id
        )
    )

    conn.commit()
    conn.close()

    return {"success": True, "message": "Resident updated successfully"}


def update_committee_role(resident_id: int, committee_role: str):

    role_check = validate_committee_role(
        committee_role,
        exclude_resident_id=resident_id
    )
    if not role_check["valid"]:
        return {"success": False, "message": role_check["message"]}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Residents
        SET CommitteeRole = ?
        WHERE ResidentID = ?
        """,
        (_normalize_committee_role(committee_role), resident_id)
    )

    conn.commit()
    conn.close()

    return {"success": True, "message": f"Committee role updated to {committee_role}"}


def complete_profile(resident_id: int, is_owner: bool, owner_name, vehicle_details: list):

    if not is_owner and not owner_name:
        return {
            "success": False,
            "message": "Tenants must provide the owner name on first login"
        }

    if not vehicle_details:
        return {
            "success": False,
            "message": "At least one vehicle detail is required"
        }

    vehicles_json = json.dumps(vehicle_details)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Residents
        SET
            OwnerName = ?,
            VehicleDetails = ?,
            ProfileCompleted = 1
        WHERE ResidentID = ?
        """,
        (owner_name if not is_owner else None, vehicles_json, resident_id)
    )

    conn.commit()
    conn.close()

    return {"success": True, "message": "Profile completed successfully"}


def update_vehicles(resident_id: int, vehicle_details: list):

    if not vehicle_details:
        return {
            "success": False,
            "message": "At least one vehicle detail is required"
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ProfileCompleted FROM Residents WHERE ResidentID = ?",
        (resident_id,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "Resident not found"}

    if not row[0]:
        conn.close()
        return {
            "success": False,
            "message": "Complete your profile first before editing vehicles"
        }

    vehicles_json = json.dumps(vehicle_details)

    cursor.execute(
        "UPDATE Residents SET VehicleDetails = ? WHERE ResidentID = ?",
        (vehicles_json, resident_id)
    )

    conn.commit()
    conn.close()

    return {"success": True, "message": "Vehicle details updated"}


def get_resident_login_details(resident_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            r.ResidentID,
            r.FullName,
            r.Email,
            r.PhoneNumber,
            r.FlatNumber
        FROM Residents r
        WHERE r.ResidentID = ?
        """,
        (resident_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "resident_id": row[0],
        "full_name": row[1],
        "email": row[2],
        "phone_number": row[3],
        "flat_number": row[4],
        "password": generate_resident_password(row[4])
    }
