import bcrypt
from app.database.db import get_connection


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def _create_user(user, role_id: int, resident_id=None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID FROM Users WHERE Email = ?",
        user.email
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        return {
            "success": False,
            "message": "Email already exists"
        }

    password_hash = _hash_password(user.password)

    cursor.execute("""
        INSERT INTO Users
        (
            FullName,
            Email,
            PasswordHash,
            PhoneNumber,
            RoleID,
            ResidentID
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        user.full_name,
        user.email,
        password_hash,
        user.phone_number,
        role_id,
        resident_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "User created successfully"
    }


def create_admin(user):
    return _create_user(user, 1)


def create_security(user):
    return _create_user(user, 3)


def create_secretary(user):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM Users WHERE RoleID = 4"
    )

    if cursor.fetchone()[0] >= 1:
        conn.close()
        return {
            "success": False,
            "message": "A secretary account already exists. Only one is allowed."
        }

    conn.close()
    return _create_user(user, 4)


def get_secretary_status():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UserID, FullName, Email
        FROM Users
        WHERE RoleID = 4
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "exists": False
        }

    return {
        "exists": True,
        "user_id": row[0],
        "full_name": row[1],
        "email": row[2]
    }


def create_resident_account(user):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ResidentID,
            FullName,
            PhoneNumber,
            Email,
            FlatNumber
        FROM Residents
        WHERE ResidentID = ?
    """, user.resident_id)

    resident = cursor.fetchone()

    if not resident:
        conn.close()
        return {
            "success": False,
            "message": "Resident not found"
        }

    email = user.email or resident[3]
    password = user.password

    cursor.execute(
        "SELECT UserID FROM Users WHERE Email = ?",
        email
    )

    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "Email already exists"
        }

    cursor.execute(
        "SELECT UserID FROM Users WHERE ResidentID = ?",
        user.resident_id
    )

    if cursor.fetchone():
        conn.close()
        return {
            "success": False,
            "message": "This resident already has a login account"
        }

    password_hash = _hash_password(password)

    cursor.execute("""
        INSERT INTO Users
        (
            FullName,
            Email,
            PasswordHash,
            PhoneNumber,
            RoleID,
            ResidentID
        )
        VALUES (?, ?, ?, ?, 2, ?)
    """,
    (
        resident[1],
        email,
        password_hash,
        resident[2],
        user.resident_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Resident login created successfully",
        "email": email,
        "password": password
    }


def create_resident_account_auto(resident_id: int):

    from app.services.resident_service import get_resident_login_details

    details = get_resident_login_details(resident_id)

    if not details:
        return {
            "success": False,
            "message": "Resident not found"
        }

    from app.schemas.user_schema import ResidentRegister

    return create_resident_account(
        ResidentRegister(
            resident_id=resident_id,
            email=details["email"],
            password=details["password"]
        )
    )


def change_password(user_id: int, current_password: str, new_password: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT PasswordHash
        FROM Users
        WHERE UserID = ?
    """, user_id)

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

    cursor.execute("""
        UPDATE Users
        SET PasswordHash = ?
        WHERE UserID = ?
    """, (new_hash, user_id))

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
            ResidentID
        FROM Users
        WHERE Email = ?
    """, login_data.email)

    user = cursor.fetchone()

    conn.close()

    if not user:
        return {
            "success": False,
            "message": "Invalid email or password"
        }

    stored_hash = user[3]

    if not bcrypt.checkpw(
        login_data.password.encode("utf-8"),
        stored_hash.encode("utf-8")
    ):
        return {
            "success": False,
            "message": "Invalid email or password"
        }

    from app.auth.jwt_handler import create_access_token

    token_data = {
        "user_id": user[0],
        "email": user[2],
        "role_id": user[4]
    }

    if user[5]:
        token_data["resident_id"] = user[5]

    token = create_access_token(token_data)

    return {
        "success": True,
        "access_token": token,
        "user_name": user[1],
        "role_id": user[4],
        "resident_id": user[5]
    }
