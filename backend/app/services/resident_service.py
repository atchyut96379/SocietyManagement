from app.database.db import get_connection
from app.config.society_config import generate_resident_password


def _normalize_committee_role(role):
    if not role or role == "None":
        return None
    return role


def create_resident(resident):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Residents
        (
            FullName,
            FlatNumber,
            PhoneNumber,
            Email,
            TowerName,
            IsOwner,
            CommitteeRole
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        resident.full_name,
        resident.flat_number,
        resident.phone_number,
        resident.email,
        resident.tower_name,
        resident.is_owner,
        _normalize_committee_role(resident.committee_role)
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Resident created successfully"
    }


def get_all_residents():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ResidentID,
            FullName,
            FlatNumber,
            PhoneNumber,
            Email,
            TowerName,
            IsOwner,
            CommitteeRole
        FROM Residents
        ORDER BY ResidentID
    """)

    residents = cursor.fetchall()

    conn.close()

    result = []

    for row in residents:
        result.append({
            "resident_id": row[0],
            "full_name": row[1],
            "flat_number": row[2],
            "phone_number": row[3],
            "email": row[4],
            "tower_name": row[5],
            "is_owner": bool(row[6]),
            "committee_role": row[7] or "None"
        })

    return result


def get_resident_by_id(resident_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ResidentID,
            FullName,
            FlatNumber,
            PhoneNumber,
            Email,
            TowerName,
            IsOwner,
            CommitteeRole
        FROM Residents
        WHERE ResidentID = ?
    """, resident_id)

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {"message": "Resident not found"}

    return {
        "resident_id": row[0],
        "full_name": row[1],
        "flat_number": row[2],
        "phone_number": row[3],
        "email": row[4],
        "tower_name": row[5],
        "is_owner": bool(row[6]),
        "committee_role": row[7] or "None"
    }


def delete_resident(resident_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Residents WHERE ResidentID = ?",
        resident_id
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Resident deleted successfully"
    }


def update_resident(resident_id, resident):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ResidentID FROM Residents WHERE ResidentID = ?",
        resident_id
    )

    if not cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "Resident not found"
        }

    cursor.execute("""
        UPDATE Residents
        SET
            FullName = ?,
            FlatNumber = ?,
            PhoneNumber = ?,
            Email = ?,
            TowerName = ?,
            IsOwner = ?,
            CommitteeRole = ?
        WHERE ResidentID = ?
    """,
    (
        resident.full_name,
        resident.flat_number,
        resident.phone_number,
        resident.email,
        resident.tower_name,
        resident.is_owner,
        _normalize_committee_role(resident.committee_role),
        resident_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Resident updated successfully"
    }


def get_resident_login_details(resident_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ResidentID,
            FullName,
            Email,
            PhoneNumber,
            FlatNumber
        FROM Residents
        WHERE ResidentID = ?
    """, resident_id)

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
