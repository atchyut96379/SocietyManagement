"""
Initialize the SocietyManagement database schema and default admin user.

Usage (from backend folder):
    python setup_db.py
"""

import os
import re

import bcrypt
from dotenv import load_dotenv

load_dotenv()

DEFAULT_ADMIN = {
    "full_name": "Society Admin",
    "email": "admin@society.com",
    "password": "Admin@123",
    "phone_number": "9999999999",
}


def get_master_connection():
    import pyodbc

    return pyodbc.connect(
        f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


def get_app_connection():
    from app.database.db import get_connection

    return get_connection()


def run_schema():
    schema_path = os.path.join(
        os.path.dirname(__file__),
        "database",
        "schema.sql"
    )

    with open(schema_path, "r", encoding="utf-8") as file:
        content = file.read()

    batches = [batch.strip() for batch in re.split(r"\bGO\b", content) if batch.strip()]

    conn = get_master_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    for batch in batches:
        cursor.execute(batch)

    cursor.close()
    conn.close()


def seed_admin():
    conn = get_app_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID FROM Users WHERE Email = ?",
        DEFAULT_ADMIN["email"]
    )

    if cursor.fetchone():
        print(f"Admin already exists: {DEFAULT_ADMIN['email']}")
        conn.close()
        return

    password_hash = bcrypt.hashpw(
        DEFAULT_ADMIN["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        """
        INSERT INTO Users
        (FullName, Email, PasswordHash, PhoneNumber, RoleID)
        VALUES (?, ?, ?, ?, 1)
        """,
        (
            DEFAULT_ADMIN["full_name"],
            DEFAULT_ADMIN["email"],
            password_hash,
            DEFAULT_ADMIN["phone_number"],
        )
    )

    conn.commit()
    conn.close()

    print("Default admin created:")
    print(f"  Email:    {DEFAULT_ADMIN['email']}")
    print(f"  Password: {DEFAULT_ADMIN['password']}")


DEFAULT_SECURITY = {
    "full_name": "Gate Security",
    "email": "security@society.com",
    "password": "Security@123",
    "phone_number": "8888888888",
}


def seed_security():
    conn = get_app_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID FROM Users WHERE Email = ?",
        DEFAULT_SECURITY["email"]
    )

    if cursor.fetchone():
        print(f"Security user already exists: {DEFAULT_SECURITY['email']}")
        conn.close()
        return

    password_hash = bcrypt.hashpw(
        DEFAULT_SECURITY["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        """
        INSERT INTO Users
        (FullName, Email, PasswordHash, PhoneNumber, RoleID)
        VALUES (?, ?, ?, ?, 3)
        """,
        (
            DEFAULT_SECURITY["full_name"],
            DEFAULT_SECURITY["email"],
            password_hash,
            DEFAULT_SECURITY["phone_number"],
        )
    )

    conn.commit()
    conn.close()

    print("Default security user created:")
    print(f"  Email:    {DEFAULT_SECURITY['email']}")
    print(f"  Password: {DEFAULT_SECURITY['password']}")


def run_migrations():
    migration_files = [
        "migrate_resident_portal.sql",
        "migrate_committee_role.sql",
        "migrate_secretary_role.sql",
    ]

    conn = get_app_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    for filename in migration_files:
        migration_path = os.path.join(
            os.path.dirname(__file__),
            "database",
            filename
        )

        with open(migration_path, "r", encoding="utf-8") as file:
            content = file.read()

        batches = [
            batch.strip()
            for batch in re.split(r"\bGO\b", content)
            if batch.strip()
        ]

        for batch in batches:
            cursor.execute(batch)

    cursor.close()
    conn.close()


def seed_resident_login():
    conn = get_app_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT TOP 1 ResidentID, FullName, Email, PhoneNumber "
        "FROM Residents ORDER BY ResidentID"
    )

    resident = cursor.fetchone()

    if not resident:
        conn.close()
        return

    resident_id, full_name, email, phone = resident

    cursor.execute(
        "SELECT UserID FROM Users WHERE Email = ? OR ResidentID = ?",
        email, resident_id
    )

    if cursor.fetchone():
        print(f"Resident login already exists for: {email}")
        conn.close()
        return

    password_hash = bcrypt.hashpw(
        "Resident@123".encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        """
        INSERT INTO Users
        (FullName, Email, PasswordHash, PhoneNumber, RoleID, ResidentID)
        VALUES (?, ?, ?, ?, 2, ?)
        """,
        (full_name, email, password_hash, phone, resident_id)
    )

    conn.commit()
    conn.close()

    print("Default resident login created:")
    print(f"  Email:    {email}")
    print(f"  Password: Resident@123")


def seed_sample_data():
    conn = get_app_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Residents")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    cursor.execute(
        """
        INSERT INTO Residents
        (FullName, FlatNumber, PhoneNumber, Email, TowerName, IsOwner)
        VALUES
        ('Ramesh Kumar', 'A-101', '9876543210', 'ramesh@example.com', 'Tower A', 1),
        ('Priya Sharma', 'B-202', '9876543211', 'priya@example.com', 'Tower B', 1),
        ('Amit Patel', 'C-303', '9876543212', 'amit@example.com', 'Tower C', 0)
        """
    )

    cursor.execute(
        """
        INSERT INTO Notices (Title, Description, CreatedBy)
        SELECT
            'Welcome to Society Management',
            'Use this portal to manage residents, visitors, complaints, and finances.',
            UserID
        FROM Users
        WHERE Email = ?
        """,
        DEFAULT_ADMIN["email"]
    )

    conn.commit()
    conn.close()
    print("Sample residents and welcome notice added.")


if __name__ == "__main__":
    print("Setting up SocietyManagement database...")
    run_schema()
    run_migrations()
    seed_admin()
    seed_security()
    seed_sample_data()
    seed_resident_login()
    print("Database setup complete.")
