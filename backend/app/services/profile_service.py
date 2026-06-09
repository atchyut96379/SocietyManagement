from app.database.db import get_connection
from app.services.user_service import _hash_password


def _needs_email(resident_email: str | None, user_email: str | None) -> bool:
    if resident_email is not None and str(resident_email).strip():
        return False
    if user_email and user_email.strip() and not user_email.endswith("@resident.local"):
        return False
    return True


def get_full_profile(resident_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            r.ResidentID, r.FullName, r.FlatNumber, r.PhoneNumber,
            r.Email, u.Email, r.TowerName, r.ResidentType, r.OwnerName,
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

    resident_email = row[4]
    user_email = row[5]
    display_email = resident_email
    if not display_email and user_email and not user_email.endswith("@resident.local"):
        display_email = user_email

    return {
        "resident_id": row[0],
        "full_name": row[1],
        "flat_number": row[2],
        "phone_number": row[3],
        "email": display_email,
        "tower_name": row[6],
        "resident_type": row[7],
        "owner_name": row[8],
        "committee_role": row[9] or "None",
        "must_change_password": bool(row[10]),
        "profile_completed": bool(row[11]),
        "car_number": row[12],
        "bike_number": row[13],
        "needs_email": _needs_email(resident_email, user_email),
    }


def complete_profile(
    resident_id: int,
    user_id: int,
    owner_name: str | None,
    phone_number: str | None,
    email: str | None,
    car_number: str | None,
    bike_number: str | None,
    new_password: str,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.ResidentType, u.ProfileCompleted, r.Email, u.Email
        FROM Residents r
        INNER JOIN Users u ON u.ResidentID = r.ResidentID
        WHERE r.ResidentID = ? AND u.UserID = ?
    """, (resident_id, user_id))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "Profile not found"}

    resident_type, profile_completed, resident_email, user_email = row[0], row[1], row[2], row[3]

    if profile_completed:
        conn.close()
        return {"success": False, "message": "Profile is already completed"}

    if _needs_email(resident_email, user_email):
        if not email or not str(email).strip():
            conn.close()
            return {
                "success": False,
                "message": "Email is required on first login"
            }

        normalized_email = str(email).strip().lower()

        cursor.execute(
            """
            SELECT UserID FROM Users
            WHERE LOWER(Email) = ? AND UserID <> ?
            """,
            (normalized_email, user_id)
        )

        if cursor.fetchone():
            conn.close()
            return {
                "success": False,
                "message": "This email is already registered"
            }

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

    if _needs_email(resident_email, user_email):
        cursor.execute(
            """
            UPDATE Residents
            SET OwnerName = ?, PhoneNumber = COALESCE(?, PhoneNumber), Email = ?
            WHERE ResidentID = ?
            """,
            (owner_name, phone_number, str(email).strip(), resident_id)
        )
        cursor.execute(
            """
            UPDATE Users
            SET Email = ?
            WHERE UserID = ?
            """,
            (str(email).strip(), user_id)
        )
    else:
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
