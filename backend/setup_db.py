"""
Initialize the SocietyManagement database schema and default admin user.

Usage (from backend folder):
    python setup_db.py
"""

import os
import re

import bcrypt
from dotenv import load_dotenv

from app.database.connection import build_connection_string, uses_sql_authentication

load_dotenv()

DEFAULT_ADMIN = {
    "full_name": "Society Admin",
    "phone_number": "9999999999",
    "email": "admin@society.com",
    "password": "Admin@123",
}


def get_master_connection():
    import pyodbc

    return pyodbc.connect(build_connection_string("master"))


def get_app_connection():
    from app.database.db import get_connection

    return get_connection()


def _schema_batches():
    schema_path = os.path.join(
        os.path.dirname(__file__),
        "database",
        "schema.sql"
    )

    with open(schema_path, "r", encoding="utf-8") as file:
        content = file.read()

    batches = [
        batch.strip()
        for batch in re.split(r"\bGO\b", content)
        if batch.strip()
    ]

    if uses_sql_authentication():
        return [
            batch for batch in batches
            if "CREATE DATABASE" not in batch.upper()
            and not batch.strip().upper().startswith("USE ")
        ]

    return batches


def run_schema():
    batches = _schema_batches()

    if uses_sql_authentication():
        conn = get_app_connection()
    else:
        conn = get_master_connection()

    conn.autocommit = True
    cursor = conn.cursor()

    for batch in batches:
        try:
            cursor.execute(batch)
        except Exception as ex:
            print(f"Schema note: {ex}")

    cursor.close()
    conn.close()


def run_migrations():
    migration_files = [
        "migrate_resident_portal.sql",
        "migrate_committee_role.sql",
        "migrate_secretary_role.sql",
        "migrate_v2_enhancements.sql",
        "migrate_visitor_entry_code.sql",
        "migrate_guard_profile.sql",
        "migrate_expense_proof.sql",
        "migrate_dual_accounts.sql",
        "migrate_monthly_report_settings.sql",
        "migrate_resident_optional_email.sql",
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
            and not batch.strip().upper().startswith("USE ")
        ]

        for batch in batches:
            try:
                cursor.execute(batch)
            except Exception as ex:
                print(f"Migration note ({filename}): {ex}")

    cursor.close()
    conn.close()


def seed_admin():
    conn = get_app_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT UserID FROM Users WHERE PhoneNumber = ?",
        DEFAULT_ADMIN["phone_number"]
    )

    if cursor.fetchone():
        print(f"Admin already exists: {DEFAULT_ADMIN['phone_number']}")
        conn.close()
        return

    password_hash = bcrypt.hashpw(
        DEFAULT_ADMIN["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        """
        INSERT INTO Users
        (FullName, Email, PasswordHash, PhoneNumber, RoleID, MustChangePassword, ProfileCompleted)
        VALUES (?, ?, ?, ?, 1, 0, 1)
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
    print(f"  Mobile:   {DEFAULT_ADMIN['phone_number']}")
    print(f"  Password: {DEFAULT_ADMIN['password']}")
    print("  Admin can only create/delete Secretary accounts.")


def seed_flats():
    from app.services.flat_service import seed_flats

    seed_flats()
    print("All society flats seeded (5 floors x 18 units).")


def seed_sample_residents():
    conn = get_app_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Residents")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    samples = [
        ("Ramesh Kumar", "101", "9876543210", "ramesh@example.com", "Owner", "None"),
        ("Priya Sharma", "201", "9876543211", "priya@example.com", "Owner", "President"),
        ("Amit Patel", "301", "9876543212", "amit@example.com", "Tenant", "None"),
    ]

    for full_name, flat_number, phone, email, resident_type, committee_role in samples:
        cursor.execute(
            "SELECT FlatID FROM Flats WHERE FlatNumber = ?",
            flat_number
        )
        flat_row = cursor.fetchone()
        if not flat_row:
            continue

        flat_id = flat_row[0]
        committee = None if committee_role == "None" else committee_role

        cursor.execute(
            """
            INSERT INTO Residents
            (FullName, FlatNumber, PhoneNumber, Email, TowerName, IsOwner,
             CommitteeRole, FlatID, ResidentType)
            VALUES (?, ?, ?, ?, 'Tower A', ?, ?, ?, ?)
            """,
            (
                full_name,
                flat_number,
                phone,
                email,
                1 if resident_type == "Owner" else 0,
                committee,
                flat_id,
                resident_type,
            )
        )

        cursor.execute("SELECT @@IDENTITY")
        resident_id = int(cursor.fetchone()[0])

        cursor.execute(
            """
            UPDATE Flats SET IsOccupied = 1, ResidentID = ?
            WHERE FlatID = ?
            """,
            (resident_id, flat_id)
        )

    cursor.execute(
        """
        INSERT INTO Notices (Title, Description, CreatedBy)
        SELECT
            'Welcome to Society Management',
            'Secretary manages residents, visitors, complaints, and finances.',
            UserID
        FROM Users
        WHERE PhoneNumber = ?
        """,
        DEFAULT_ADMIN["phone_number"]
    )

    conn.commit()
    conn.close()
    print("Sample residents and welcome notice added.")


if __name__ == "__main__":
    print("Setting up SocietyManagement database...")
    run_schema()
    run_migrations()
    seed_flats()
    seed_admin()
    seed_sample_residents()
    print("Database setup complete.")
    print("")
    print("Next steps:")
    print("  1. Admin logs in with mobile number")
    print("  2. Admin creates Secretary via POST /admin/secretary")
    print("  3. Secretary manages all society operations")
