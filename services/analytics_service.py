from database.db import get_connection


def get_orders_last_7_days():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        DATE(created_at) AS order_date,
        COUNT(*) AS total_orders
    FROM orders
    WHERE created_at >= CURDATE() - INTERVAL 6 DAY
    GROUP BY DATE(created_at)
    ORDER BY order_date;
    """

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data

def get_order_status_distribution():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM orders
        GROUP BY status
    """)

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data

def get_top_selling_items(limit=5):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            item,
            SUM(quantity) AS total_quantity
        FROM orders
        GROUP BY item
        ORDER BY total_quantity DESC
        LIMIT %s
    """, (limit,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data