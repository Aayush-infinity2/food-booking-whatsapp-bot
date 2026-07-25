import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST") or os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT") or os.getenv("DB_PORT", 3306)),
        user=os.getenv("MYSQL_USER") or os.getenv("DB_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD", ""),
        database=os.getenv("MYSQL_NAME") or os.getenv("DB_NAME", "food_booking_bot"),
        connect_timeout=10
    )
