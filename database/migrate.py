"""Apply additive schema updates to an existing food_booking_bot database."""
from database.db import get_connection


STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS students (
        registration_number VARCHAR(30) PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    "ALTER TABLE orders ADD COLUMN booking_reference VARCHAR(36) NULL",
    "CREATE INDEX idx_orders_booking_reference ON orders (booking_reference)",
]


def main():
    conn = get_connection()
    cursor = conn.cursor()
    for statement in STATEMENTS:
        try:
            cursor.execute(statement)
        except Exception as error:
            # Existing columns/indexes are safe to leave untouched.
            if "Duplicate column" not in str(error) and "Duplicate key" not in str(error):
                raise
    conn.commit()
    cursor.close()
    conn.close()
    print("Database migration completed.")


if __name__ == "__main__":
    main()
