from database.db import get_connection


class StudentRepository:
    @staticmethod
    def get_by_registration(registration_number):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM students WHERE registration_number=%s",
            (registration_number,),
        )
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        return student

    @staticmethod
    def create(registration_number, full_name, phone):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (registration_number, full_name, phone) VALUES (%s, %s, %s)",
            (registration_number, full_name, phone),
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return students

