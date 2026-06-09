import re

from app.database.db import get_connection


def normalize_phone(phone: str | None) -> str:
    if not phone:
        return ""

    digits = re.sub(r"\D", "", phone.strip())

    if len(digits) > 10:
        digits = digits[-10:]

    return digits


def _auto_link_user(user_id: int, resident_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Users
        SET ResidentID = ?
        WHERE UserID = ? AND (ResidentID IS NULL OR ResidentID = ?)
        """,
        (resident_id, user_id, resident_id)
    )

    conn.commit()
    conn.close()


def resolve_resident_id(user: dict) -> int | None:
    if user.get("resident_id"):
        return int(user["resident_id"])

    user_id = user.get("user_id")
    if not user_id:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT PhoneNumber, FullName, ResidentID
        FROM Users WHERE UserID = ?
        """,
        user_id
    )

    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        return None

    phone, full_name, linked_resident_id = user_row

    if linked_resident_id:
        conn.close()
        return int(linked_resident_id)

    login_phone = normalize_phone(user.get("phone_number") or phone)

    cursor.execute(
        "SELECT ResidentID, PhoneNumber, FullName FROM Residents"
    )

    residents = cursor.fetchall()
    conn.close()

    for resident_id, resident_phone, resident_name in residents:
        if normalize_phone(resident_phone) == login_phone:
            _auto_link_user(user_id, resident_id)
            return int(resident_id)

    if full_name:
        for resident_id, resident_phone, resident_name in residents:
            if resident_name.strip().lower() == full_name.strip().lower():
                _auto_link_user(user_id, resident_id)
                return int(resident_id)

    return None


def link_user_by_flat_number(
    user_id: int,
    flat_number: str,
    full_name: str | None = None,
) -> dict:
    flat_number = flat_number.strip()

    if not flat_number:
        return {"success": False, "message": "Flat number is required"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ResidentID, FullName, PhoneNumber, FlatNumber
        FROM Residents
        WHERE FlatNumber = ?
        """,
        flat_number
    )

    row = cursor.fetchone()

    if not row:
        cursor.execute(
            """
            SELECT r.ResidentID, r.FullName, r.PhoneNumber, r.FlatNumber
            FROM Residents r
            INNER JOIN Flats f ON r.FlatID = f.FlatID
            WHERE f.FlatNumber = ?
            """,
            flat_number
        )
        row = cursor.fetchone()

    conn.close()

    if not row:
        return {
            "success": False,
            "message": (
                f"No resident found for flat {flat_number}. "
                "Contact secretary to register your flat first."
            )
        }

    resident_id, resident_name, resident_phone, resident_flat = row

    if full_name and full_name.strip().lower() != resident_name.strip().lower():
        return {
            "success": False,
            "message": (
                f"Name does not match flat {resident_flat} "
                f"(registered: {resident_name})"
            )
        }

    result = link_user_to_resident(user_id, resident_id)

    if result.get("success"):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT PhoneNumber FROM Users WHERE UserID = ?",
            user_id
        )
        user_phone = cursor.fetchone()

        if user_phone and user_phone[0]:
            cursor.execute(
                """
                UPDATE Residents
                SET PhoneNumber = ?
                WHERE ResidentID = ?
                """,
                (user_phone[0], resident_id)
            )
            conn.commit()

        conn.close()

        result.update({
            "flat_number": resident_flat,
            "full_name": resident_name,
            "resident_id": resident_id,
        })

    return result


def link_user_to_resident(user_id: int, resident_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ResidentID FROM Residents WHERE ResidentID = ?",
        resident_id
    )

    if not cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Resident not found"}

    cursor.execute(
        """
        SELECT UserID FROM Users
        WHERE ResidentID = ? AND UserID <> ?
        """,
        (resident_id, user_id)
    )

    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "This flat is already linked to another login"
        }

    cursor.execute(
        "UPDATE Users SET ResidentID = ? WHERE UserID = ?",
        (resident_id, user_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Flat linked successfully",
        "resident_id": resident_id
    }
