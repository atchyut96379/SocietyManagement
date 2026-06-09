from app.database.db import get_connection
from app.services.user_service import _hash_password


def get_full_profile(resident_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.ResidentID, r.FullName, r.FlatNumber, r.PhoneNumber,
            r.Email, r.TowerName, r.ResidentType, r.OwnerName,
            r.CommitteeRole, u.MustChangePassword, u.ProfileCompleted,
            v.CarNumber, v.BikeNumber
        FROM Residents r
        INNER JOIN Users u ON u.ResidentID = r.ResidentID
        LEFT JOIN Vehicles v ON v.ResidentID = r.ResidentID
        WHERE r.ResidentID = ? AND u.UserID = ?
    """, (resident_id, user_id))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "resident_id": row[0],
        "full_name": row[1],
        "flat_number": row[2],
        "phone_number": row[3],
        "email": row[4],
        "tower_name": row[5],
        "resident_type": row[6],
        "owner_name": row[7],
        "committee_role": row[8] or "None",
        "must_change_password": bool(row[9]),
        "profile_completed": bool(row[10]),
        "car_number": row[11],
        "bike_number": row[12],
    }


def complete_profile(
    resident_id: int,
    user_id: int,
    owner_name: str | None,
    phone_number: str | None,
    car_number: str | None,
    bike_number: str | None,
    new_password: str,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.ResidentType, u.ProfileCompleted
        FROM Residents r
        INNER JOIN Users u ON u.ResidentID = r.ResidentID
        WHERE r.ResidentID = ? AND u.UserID = ?
    """, (resident_id, user_id))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "Profile not found"}

    resident_type, profile_completed = row[0], row[1]

    if profile_completed:
        conn.close()
        return {"success": False, "message": "Profile is already completed"}

    if resident_type == "Tenant":
        if not owner_name or not owner_name.strip():
            conn.close()
            return {
                "success": False,
                "message": "Owner name is required for tenants"
            }
        if not phone_number or not phone_number.strip():
            conn.close()
            return {
                "success": False,
                "message": "Phone number is required for tenants on first login"
            }

    cursor.execute(
        """
        UPDATE Residents
        SET OwnerName = ?, PhoneNumber = COALESCE(?, PhoneNumber)
        WHERE ResidentID = ?
        """,
        (owner_name, phone_number, resident_id)
    )

    cursor.execute(
        "SELECT VehicleID FROM Vehicles WHERE ResidentID = ?",
        resident_id
    )

    if cursor.fetchone():
        cursor.execute(
            """
            UPDATE Vehicles
            SET CarNumber = ?, BikeNumber = ?, UpdatedDate = GETDATE()
            WHERE ResidentID = ?
            """,
            (car_number, bike_number, resident_id)
        )
    else:
        cursor.execute(
            """
            INSERT INTO Vehicles (ResidentID, CarNumber, BikeNumber)
            VALUES (?, ?, ?)
            """,
            (resident_id, car_number, bike_number)
        )

    password_hash = _hash_password(new_password)

    cursor.execute(
        """
        UPDATE Users
        SET PasswordHash = ?, MustChangePassword = 0, ProfileCompleted = 1
        WHERE UserID = ?
        """,
        (password_hash, user_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Profile completed successfully"
    }


def update_vehicles(resident_id: int, user_id: int, car_number: str | None, bike_number: str | None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ProfileCompleted
        FROM Users
        WHERE UserID = ? AND ResidentID = ?
    """, (user_id, resident_id))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "User not found"}

    if not row[0]:
        conn.close()
        return {
            "success": False,
            "message": "Complete your profile first before editing vehicles"
        }

    cursor.execute(
        "SELECT VehicleID FROM Vehicles WHERE ResidentID = ?",
        resident_id
    )

    if cursor.fetchone():
        cursor.execute(
            """
            UPDATE Vehicles
            SET CarNumber = ?, BikeNumber = ?, UpdatedDate = GETDATE()
            WHERE ResidentID = ?
            """,
            (car_number, bike_number, resident_id)
        )
    else:
        cursor.execute(
            """
            INSERT INTO Vehicles (ResidentID, CarNumber, BikeNumber)
            VALUES (?, ?, ?)
            """,
            (resident_id, car_number, bike_number)
        )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Vehicle details updated successfully"
    }
