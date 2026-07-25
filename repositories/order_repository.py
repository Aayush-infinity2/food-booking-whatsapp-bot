from database.db import get_connection


class OrderRepository:
    """
    Repository responsible ONLY for database operations.
    No business logic should be written here.
    """

    # ----------------------------
    # Create Order
    # ----------------------------
    @staticmethod
    def insert_order(order_data):

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO orders
        (
            customer_phone,
            area,
            restaurant,
            category,
            item,
            variant,
            quantity,
            total,
            pickup_slot,
            booking_reference
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            order_data["customer_phone"],
            order_data["area"],
            order_data["restaurant"],
            order_data["category"],
            order_data["item"],
            order_data.get("variant"),
            order_data["quantity"],
            order_data["total"],
            order_data["pickup_slot"],
            order_data.get("booking_reference")
        )

        cursor.execute(query, values)
        conn.commit()

        order_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return order_id

    # ----------------------------
    # Get All Orders
    # ----------------------------
    @staticmethod
    def get_all_orders():

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM orders
            ORDER BY created_at DESC
        """)

        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return orders

    # ----------------------------
    # Get Order By ID
    # ----------------------------
    @staticmethod
    def get_order_by_id(order_id):

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM orders
            WHERE id=%s
        """, (order_id,))

        order = cursor.fetchone()

        cursor.close()
        conn.close()

        return order

    # ----------------------------
    # Latest Order By Phone
    # ----------------------------
    @staticmethod
    def get_latest_order(phone):

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM orders
            WHERE customer_phone=%s
            ORDER BY id DESC
            LIMIT 1
        """, (phone,))

        order = cursor.fetchone()

        cursor.close()
        conn.close()

        return order

    @staticmethod
    def get_orders_for_customer(phone):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM orders WHERE customer_phone=%s ORDER BY created_at DESC
        """, (phone,))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return orders

    # ----------------------------
    # Update Status
    # ----------------------------
    @staticmethod
    def update_status(order_id, status):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE orders
            SET status=%s
            WHERE id=%s
        """, (status, order_id))

        conn.commit()

        cursor.close()
        conn.close()

    # ----------------------------
    # Delete Order
    # ----------------------------
    @staticmethod
    def delete_order(order_id):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM orders
            WHERE id=%s
        """, (order_id,))

        conn.commit()

        cursor.close()
        conn.close()

    # ----------------------------
    # Search Orders
    # ----------------------------
    @staticmethod
    def search_orders(keyword):

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        keyword = f"%{keyword}%"

        cursor.execute("""
            SELECT *
            FROM orders
            WHERE
                customer_phone LIKE %s
                OR restaurant LIKE %s
                OR item LIKE %s
                OR category LIKE %s
            ORDER BY created_at DESC
        """, (
            keyword,
            keyword,
            keyword,
            keyword
        ))

        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return orders

    # ----------------------------
    # Filter Orders
    # ----------------------------
    @staticmethod
    def filter_orders(status=None, restaurant=None):

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM orders WHERE 1=1"
        params = []

        if status:
            query += " AND status=%s"
            params.append(status)

        if restaurant:
            query += " AND restaurant=%s"
            params.append(restaurant)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, tuple(params))

        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return orders

    # ----------------------------
    # Orders Between Dates
    # ----------------------------
    @staticmethod
    def get_orders_between(start_date, end_date):

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM orders
            WHERE DATE(created_at)
            BETWEEN %s AND %s
            ORDER BY created_at DESC
        """, (start_date, end_date))

        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return orders

    # ----------------------------
    # Dashboard Statistics
    # ----------------------------
    @staticmethod
    def count_orders():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM orders")

        total = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return total

    @staticmethod
    def count_pending():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE status='Pending'
        """)

        total = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return total

    @staticmethod
    def count_preparing():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE status='Preparing'
        """)

        total = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return total

    @staticmethod
    def today_revenue():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(total),0)
            FROM orders
            WHERE DATE(created_at)=CURDATE()
        """)

        revenue = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return revenue

    # ----------------------------
    # Get Restaurants
    # ----------------------------
    @staticmethod
    def get_all_restaurants():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT restaurant
            FROM orders
            ORDER BY restaurant
        """)

        restaurants = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return restaurants
