from app.config.society_config import (
    generate_flat_numbers_for_floor,
    get_floors_count,
    get_towers,
)
from app.database.db import get_connection


def seed_all_flats():

    conn = get_connection()
    cursor = conn.cursor()

    towers = get_towers()
    floors = get_floors_count()
    created = 0

    for tower in towers:
        for floor in range(1, floors + 1):
            for flat_number in generate_flat_numbers_for_floor(floor):
                cursor.execute(
                    """
                    SELECT FlatID FROM Flats
                    WHERE TowerName = ? AND FlatNumber = ?
                    """,
                    (tower, flat_number)
                )
                if cursor.fetchone():
                    continue

                cursor.execute(
                    """
                    INSERT INTO Flats (TowerName, FlatNumber, FloorNumber)
                    VALUES (?, ?, ?)
                    """,
                    (tower, flat_number, floor)
                )
                created += 1

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Flats seeded: {created} new units",
        "created": created
    }


def get_available_flats(tower_name: str = None):

    conn = get_connection()
    cursor = conn.cursor()

    if tower_name:
        cursor.execute(
            """
            SELECT FlatID, TowerName, FlatNumber, FloorNumber, IsOccupied
            FROM Flats
            WHERE TowerName = ? AND IsOccupied = 0
            ORDER BY FloorNumber, FlatNumber
            """,
            (tower_name,)
        )
    else:
        cursor.execute(
            """
            SELECT FlatID, TowerName, FlatNumber, FloorNumber, IsOccupied
            FROM Flats
            WHERE IsOccupied = 0
            ORDER BY TowerName, FloorNumber, FlatNumber
            """
        )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "flat_id": row[0],
            "tower_name": row[1],
            "flat_number": row[2],
            "floor_number": row[3],
            "is_occupied": bool(row[4])
        }
        for row in rows
    ]


def get_all_flats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            f.FlatID,
            f.TowerName,
            f.FlatNumber,
            f.FloorNumber,
            f.IsOccupied,
            r.ResidentID,
            r.FullName
        FROM Flats f
        LEFT JOIN Residents r ON r.FlatID = f.FlatID
        ORDER BY f.TowerName, f.FloorNumber, f.FlatNumber
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "flat_id": row[0],
            "tower_name": row[1],
            "flat_number": row[2],
            "floor_number": row[3],
            "is_occupied": bool(row[4]),
            "resident_id": row[5],
            "resident_name": row[6]
        }
        for row in rows
    ]


def get_flat_by_id(flat_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT FlatID, TowerName, FlatNumber, FloorNumber, IsOccupied
        FROM Flats
        WHERE FlatID = ?
        """,
        (flat_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "flat_id": row[0],
        "tower_name": row[1],
        "flat_number": row[2],
        "floor_number": row[3],
        "is_occupied": bool(row[4])
    }


def mark_flat_occupied(flat_id: int, occupied: bool = True):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE Flats SET IsOccupied = ? WHERE FlatID = ?",
        (1 if occupied else 0, flat_id)
    )

    conn.commit()
    conn.close()
