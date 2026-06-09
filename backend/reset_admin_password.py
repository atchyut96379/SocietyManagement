"""
Reset default admin password.

Usage (from backend folder):
    python reset_admin_password.py
"""

import bcrypt
from dotenv import load_dotenv

load_dotenv()

ADMIN_PHONE = "9999999999"
ADMIN_PASSWORD = "Admin@123"


def main():
    from app.database.db import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(
        ADMIN_PASSWORD.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        """
        UPDATE Users
        SET PasswordHash = ?, MustChangePassword = 0, ProfileCompleted = 1
        WHERE PhoneNumber = ?
        """,
        (password_hash, ADMIN_PHONE)
    )

    if cursor.rowcount == 0:
        print(f"No user found with mobile: {ADMIN_PHONE}")
    else:
        conn.commit()
        print("Admin password reset successfully:")
        print(f"  Mobile:   {ADMIN_PHONE}")
        print(f"  Password: {ADMIN_PASSWORD}")

    conn.close()


if __name__ == "__main__":
    main()
