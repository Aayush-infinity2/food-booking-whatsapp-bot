import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    db_name = os.getenv("MYSQL_NAME") or os.getenv("DB_NAME") or "food_booking_bot"
    # Ensure connection points to food_booking_bot database where schema tables reside
    if db_name == "defaultdb":
        db_name = "food_booking_bot"

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST") or os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT") or os.getenv("DB_PORT", 3306)),
        user=os.getenv("MYSQL_USER") or os.getenv("DB_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD", ""),
        database=db_name,
        connect_timeout=10
    )