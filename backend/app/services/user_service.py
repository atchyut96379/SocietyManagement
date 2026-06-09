import bcrypt

from app.config.society_config import generate_guard_password, generate_password
from app.database.db import get_connection


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def _phone_exists(phone_number: str, exclude_user_id: int | None = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    if exclude_user_id:
        cursor.execute(
            "SELECT UserID FROM Users WHERE PhoneNumber = ? AND UserID <> ?",
            (phone_number, exclude_user_id)
        )
    else:
        cursor.execute(
            "SELECT UserID FROM Users WHERE PhoneNumber = ?",
            (phone_number,)
        )

    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def create_secretary(user):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Users WHERE RoleID = 4")
    if cursor.fetchone()[0] >= 1:
        conn.close()
        return {
            "success": False,
            "message": "A secretary account already exists. Delete the current secretary first."
        }

    conn.close()

    if _phone_exists(user.phone_number):
        return {
            "success": False,
            "message": "Mobile number already registered"
        }

    password = generate_password(is_secretary_account=True)
    password_hash = _hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO Users
        (FullName, Email, PasswordHash, PhoneNumber, RoleID, MustChangePassword)
        VALUES (?, ?, ?, ?, 4, 1)
        """,
        (
            user.full_name,
            user.email,
            password_hash,
            user.phone_number,
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Secretary account created successfully",
        "phone_number": user.phone_number,
        "password": password
    }


def delete_secretary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID FROM Users WHERE RoleID = 4"
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {
            "success": False,
            "message": "No secretary account exists"
        }

    user_id = row[0]

    cursor.execute("DELETE FROM Users WHERE UserID = ?", user_id)
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Secretary account deleted. Admin can create a new secretary."
    }


def create_security(user):
    if _phone_exists(user.phone_number):
        return {
            "success": False,
            "message": "Mobile number already registered"
        }

    password = generate_guard_password()
    password_hash = _hash_password(password)
    email = user.email or f"{user.phone_number}@guard.local"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO Users
        (
            FullName,
            Email,
            PasswordHash,
            PhoneNumber,
            RoleID,
            MustChangePassword,
            ProfileCompleted
        )
        VALUES (?, ?, ?, ?, 3, 1, 0)
        """,
        (
            user.full_name,
            email,
            password_hash,
            user.phone_number,
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Guard account created successfully",
        "phone_number": user.phone_number,
        "password": password,
    }


def list_security_guards():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            UserID,
            FullName,
            PhoneNumber,
            Email,
            IdentityCardType,
            IdentityCardNumber,
            ProfileCompleted
        FROM Users
        WHERE RoleID = 3
        ORDER BY FullName
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "user_id": row[0],
            "full_name": row[1],
            "phone_number": row[2],
            "email": row[3],
            "identity_card_type": row[4],
            "identity_card_number": row[5],
            "profile_completed": bool(row[6]),
        }
        for row in rows
    ]


def get_secretary_status():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UserID, FullName, Email, PhoneNumber
        FROM Users
        WHERE RoleID = 4
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"exists": False}

    return {
        "exists": True,
        "user_id": row[0],
        "full_name": row[1],
        "email": row[2],
        "phone_number": row[3]
    }


def create_resident_account(
    resident_id: int,
    phone_number: str,
    email: str | None,
    full_name: str,
    committee_role: str | None,
    flat_number: str,
):
    if _phone_exists(phone_number):
        return {
            "success": False,
            "message": "Mobile number already registered"
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID FROM Users WHERE ResidentID = ?",
        resident_id
    )

    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "This resident already has a login account"
        }

    password = generate_password(
        committee_role=committee_role if committee_role != "None" else None,
        flat_number=flat_number
    )
    password_hash = _hash_password(password)

    cursor.execute(
        """
        INSERT INTO Users
        (
            FullName,
            Email,
            PasswordHash,
            PhoneNumber,
            RoleID,
            ResidentID,
            MustChangePassword,
            ProfileCompleted
        )
        VALUES (?, ?, ?, ?, 2, ?, 1, 0)
        """,
        (
            full_name,
            email,
            password_hash,
            phone_number,
            resident_id,
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Resident login created successfully",
        "phone_number": phone_number,
        "password": password
    }


def change_password(user_id: int, current_password: str, new_password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT PasswordHash FROM Users WHERE UserID = ?",
        user_id
    )

    row = cursor.fetchone()

    if not row:
        conn.close()
        return {
            "success": False,
            "message": "User not found"
        }

    stored_hash = row[0]

    if not bcrypt.checkpw(
        current_password.encode("utf-8"),
        stored_hash.encode("utf-8")
    ):
        conn.close()
        return {
            "success": False,
            "message": "Current password is incorrect"
        }

    new_hash = _hash_password(new_password)

    cursor.execute(
        """
        UPDATE Users
        SET PasswordHash = ?, MustChangePassword = 0, ProfileCompleted = 1
        WHERE UserID = ?
        """,
        (new_hash, user_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Password changed successfully"
    }


def login_user(login_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            UserID,
            FullName,
            Email,
            PasswordHash,
            RoleID,
            ResidentID,
            MustChangePassword,
            ProfileCompleted
        FROM Users
        WHERE PhoneNumber = ?
    """, login_data.phone_number)

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {
            "success": False,
            "message": "Invalid mobile number or password"
        }

    stored_hash = user[3]

    if not bcrypt.checkpw(
        login_data.password.encode("utf-8"),
        stored_hash.encode("utf-8")
    ):
        return {
            "success": False,
            "message": "Invalid mobile number or password"
        }

    from app.auth.jwt_handler import create_access_token

    from app.services.resident_resolver import resolve_resident_id

    token_data = {
        "user_id": user[0],
        "phone_number": login_data.phone_number,
        "role_id": user[4]
    }

    if user[2]:
        token_data["email"] = user[2]

    resident_id = user[5]
    if not resident_id:
        resident_id = resolve_resident_id({
            "user_id": user[0],
            "phone_number": login_data.phone_number,
        })

    if resident_id:
        token_data["resident_id"] = resident_id

    token = create_access_token(token_data)

    return {
        "success": True,
        "access_token": token,
        "user_name": user[1],
        "role_id": user[4],
        "resident_id": resident_id,
        "must_change_password": bool(user[6]),
        "profile_completed": bool(user[7])
    }
