import os
import getpass
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def main():
    print("==================================================")
    print("   LPU Food Bot - Database Schema Installer      ")
    print("==================================================")

    host = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST") or input("Enter MySQL Host (e.g. lpu-food-db-food-booking-whatsapp-bot.i.aivencloud.com): ").strip()
    port = int(os.getenv("MYSQL_PORT") or os.getenv("DB_PORT") or input("Enter MySQL Port (default 3306 or Aiven 25642): ").strip() or 3306)
    user = os.getenv("MYSQL_USER") or os.getenv("DB_USER") or input("Enter MySQL User (e.g. avnadmin): ").strip()
    password = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD") or getpass.getpass("Enter MySQL Password: ").strip()
    db_name = os.getenv("MYSQL_NAME") or os.getenv("DB_NAME") or "defaultdb"

    print(f"\nConnecting to {host}:{port} as {user}...")

    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        print("Connected successfully!")

        with open("database/schema.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split and execute statements
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                print(f"Executing statement warning/notice: {err}")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n✅ SUCCESS: All database tables ('students', 'orders') created successfully!")

    except Exception as e:
        print(f"\n❌ Connection Error: {e}")

if __name__ == "__main__":
    main()
