from app.config.society_config import (
    FLOOR_COUNT,
    TOWER_NAME,
    get_all_flat_numbers,
    get_floor_flat_numbers,
)
from app.database.db import get_connection


def seed_flats():

    conn = get_connection()
    cursor = conn.cursor()

    for floor in range(1, FLOOR_COUNT + 1):
        for flat_number in get_floor_flat_numbers(floor):
            cursor.execute(
                "SELECT FlatID FROM Flats WHERE FlatNumber = ?",
                flat_number
            )
            if cursor.fetchone():
                continue

            cursor.execute(
                """
                INSERT INTO Flats (FlatNumber, FloorNumber, TowerName)
                VALUES (?, ?, ?)
                """,
                (flat_number, floor, TOWER_NAME)
            )

    conn.commit()
    conn.close()


def get_all_flats(available_only: bool = False):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            f.FlatID,
            f.FlatNumber,
            f.FloorNumber,
            f.TowerName,
            f.IsOccupied,
            f.ResidentID,
            r.FullName
        FROM Flats f
        LEFT JOIN Residents r
            ON f.ResidentID = r.ResidentID
    """

    if available_only:
        query += " WHERE f.IsOccupied = 0"

    query += " ORDER BY f.FloorNumber, f.FlatNumber"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "flat_id": row[0],
            "flat_number": row[1],
            "floor_number": row[2],
            "tower_name": row[3],
            "is_occupied": bool(row[4]),
            "resident_id": row[5],
            "resident_name": row[6],
        }
        for row in rows
    ]


def get_flat_by_id(flat_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT FlatID, FlatNumber, FloorNumber, TowerName, IsOccupied, ResidentID
        FROM Flats WHERE FlatID = ?
        """,
        flat_id
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "flat_id": row[0],
        "flat_number": row[1],
        "floor_number": row[2],
        "tower_name": row[3],
        "is_occupied": bool(row[4]),
        "resident_id": row[5],
    }


def mark_flat_occupied(flat_id: int, resident_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Flats
        SET IsOccupied = 1, ResidentID = ?
        WHERE FlatID = ?
        """,
        (resident_id, flat_id)
    )

    conn.commit()
    conn.close()


def mark_flat_vacant(flat_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE Flats
        SET IsOccupied = 0, ResidentID = NULL
        WHERE FlatID = ?
        """,
        flat_id
    )

    conn.commit()
    conn.close()


def get_flat_count():
    return len(get_all_flat_numbers())
