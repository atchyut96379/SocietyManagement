import bcrypt

from app.config.society_config import generate_secretary_password
from app.database.db import get_connection


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def _phone_exists(phone_number: str, exclude_user_id: int = None) -> bool:

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


def _create_user(full_name, phone_number, password, role_id, email=None, resident_id=None):

    if _phone_exists(phone_number):
        return {
            "success": False,
            "message": "Mobile number already registered"
        }

    conn = get_connection()
    cursor = conn.cursor()

    password_hash = _hash_password(password)

    cursor.execute(
        """
        INSERT INTO Users
        (FullName, Email, PasswordHash, PhoneNumber, RoleID, ResidentID, FirstLoginCompleted)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """,
        (full_name, email, password_hash, phone_number, role_id, resident_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "User created successfully",
        "phone_number": phone_number,
        "password": password
    }


def create_admin(user):
    return _create_user(
        user.full_name,
        user.phone_number,
        user.password,
        1,
        user.email
    )


def create_security(user):
    return _create_user(
        user.full_name,
        user.phone_number,
        user.password,
        3,
        user.email
    )


def create_secretary(user):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Users WHERE RoleID = 4")
    if cursor.fetchone()[0] >= 1:
        conn.close()
        return {
            "success": False,
            "message": "A secretary account already exists. Only one is allowed."
        }

    conn.close()

    password = generate_secretary_password()

    result = _create_user(
        user.full_name,
        user.phone_number,
        password,
        4,
        user.email
    )

    if result.get("success"):
        result["message"] = "Secretary account created. Share mobile number and default password."
        result["default_password"] = password

    return result


def transfer_secretary(new_secretary_user_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID, RoleID FROM Users WHERE UserID = ?",
        (new_secretary_user_id,)
    )
    new_user = cursor.fetchone()

    if not new_user:
        conn.close()
        return {"success": False, "message": "User not found"}

    if new_user[1] == 4:
        conn.close()
        return {"success": False, "message": "User is already the secretary"}

    cursor.execute("SELECT UserID FROM Users WHERE RoleID = 4")
    current = cursor.fetchone()

    if current:
        cursor.execute(
            "UPDATE Users SET RoleID = 2 WHERE UserID = ?",
            (current[0],)
        )

    cursor.execute(
        "UPDATE Users SET RoleID = 4 WHERE UserID = ?",
        (new_secretary_user_id,)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Secretary role transferred successfully"
    }


def get_secretary_status():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT UserID, FullName, Email, PhoneNumber
        FROM Users
        WHERE RoleID = 4
        """
    )

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


def create_resident_account(user):

    from app.config.society_config import generate_resident_password
    from app.services.resident_service import get_resident_by_id

    resident = get_resident_by_id(user.resident_id)

    if resident.get("message") == "Resident not found":
        return {"success": False, "message": "Resident not found"}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID FROM Users WHERE ResidentID = ?",
        (user.resident_id,)
    )
    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "This resident already has a login account"
        }

    conn.close()

    phone = user.phone_number
    password = user.password or generate_resident_password(resident["flat_number"])

    return _create_user(
        resident["full_name"],
        phone,
        password,
        2,
        user.email,
        user.resident_id
    )


def create_resident_account_auto(resident_id: int):

    from app.services.resident_service import get_resident_login_details

    details = get_resident_login_details(resident_id)

    if not details:
        return {"success": False, "message": "Resident not found"}

    from app.schemas.user_schema import ResidentRegister

    return create_resident_account(
        ResidentRegister(
            resident_id=resident_id,
            phone_number=details["phone_number"],
            email=details.get("email"),
            password=details["password"]
        )
    )


def change_password(user_id: int, current_password: str, new_password: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT PasswordHash FROM Users WHERE UserID = ?",
        (user_id,)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "message": "User not found"}

    stored_hash = row[0]

    if not bcrypt.checkpw(
        current_password.encode("utf-8"),
        stored_hash.encode("utf-8")
    ):
        conn.close()
        return {"success": False, "message": "Current password is incorrect"}

    new_hash = _hash_password(new_password)

    cursor.execute(
        "UPDATE Users SET PasswordHash = ? WHERE UserID = ?",
        (new_hash, user_id)
    )

    conn.commit()
    conn.close()

    return {"success": True, "message": "Password changed successfully"}


def mark_first_login_complete(user_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE Users SET FirstLoginCompleted = 1 WHERE UserID = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def login_user(login_data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            u.UserID,
            u.FullName,
            u.Email,
            u.PasswordHash,
            u.RoleID,
            u.ResidentID,
            u.FirstLoginCompleted,
            ISNULL(r.ProfileCompleted, 0)
        FROM Users u
        LEFT JOIN Residents r ON u.ResidentID = r.ResidentID
        WHERE u.PhoneNumber = ?
        """,
        (login_data.phone_number.strip(),)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"success": False, "message": "Invalid mobile number or password"}

    stored_hash = user[3]

    if not bcrypt.checkpw(
        login_data.password.encode("utf-8"),
        stored_hash.encode("utf-8")
    ):
        return {"success": False, "message": "Invalid mobile number or password"}

    from app.auth.jwt_handler import create_access_token

    token_data = {
        "user_id": user[0],
        "phone_number": login_data.phone_number.strip(),
        "role_id": user[4]
    }

    if user[2]:
        token_data["email"] = user[2]

    if user[5]:
        token_data["resident_id"] = user[5]

    token = create_access_token(token_data)

    profile_required = False
    if user[4] == 2:
        profile_required = not bool(user[7])

    return {
        "success": True,
        "access_token": token,
        "user_name": user[1],
        "role_id": user[4],
        "resident_id": user[5],
        "first_login": not bool(user[6]),
        "profile_required": profile_required
    }
