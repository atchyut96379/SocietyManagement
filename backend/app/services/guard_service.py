import bcrypt

from app.database.db import get_connection


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def get_guard_profile(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            FullName,
            PhoneNumber,
            Email,
            IdentityCardType,
            IdentityCardNumber,
            MustChangePassword,
            ProfileCompleted
        FROM Users
        WHERE UserID = ? AND RoleID = 3
        """,
        user_id
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "Guard account not found"}

    return {
        "success": True,
        "full_name": row[0],
        "phone_number": row[1],
        "email": row[2],
        "identity_card_type": row[3],
        "identity_card_number": row[4],
        "must_change_password": bool(row[5]),
        "profile_completed": bool(row[6]),
    }


def complete_guard_profile(user_id: int, data) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT PasswordHash, RoleID FROM Users WHERE UserID = ?",
        user_id
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "Guard account not found"}

    if row[1] != 3:
        conn.close()
        return {"success": False, "message": "Not a guard account"}

    stored_hash = row[0]

    if not bcrypt.checkpw(
        data.current_password.encode("utf-8"),
        stored_hash.encode("utf-8")
    ):
        conn.close()
        return {
            "success": False,
            "message": "Current password is incorrect"
        }

    cursor.execute(
        """
        SELECT UserID FROM Users
        WHERE PhoneNumber = ? AND UserID <> ?
        """,
        (data.phone_number, user_id)
    )

    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "Mobile number already registered"
        }

    identity_number = data.identity_card_number.strip()
    if len(identity_number) < 4:
        conn.close()
        return {
            "success": False,
            "message": "Enter a valid identity card number"
        }

    new_hash = _hash_password(data.new_password)

    cursor.execute(
        """
        UPDATE Users
        SET
            FullName = ?,
            PhoneNumber = ?,
            Email = ?,
            IdentityCardType = ?,
            IdentityCardNumber = ?,
            PasswordHash = ?,
            MustChangePassword = 0,
            ProfileCompleted = 1
        WHERE UserID = ?
        """,
        (
            data.full_name.strip(),
            data.phone_number.strip(),
            data.email,
            data.identity_card_type,
            identity_number,
            new_hash,
            user_id,
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Profile updated. Use your new password from next login."
    }
