from repositories.order_repository import OrderRepository


class OrderService:
    """
    Contains business logic for Orders.
    No SQL queries should be written here.
    """

    @staticmethod
    def save_order(session, phone):
        """
        Save a new order.
        """

        order_data = {
            "customer_phone": phone,
            "area": session["area"],
            "restaurant": session["restaurant"],
            "category": session["category"],
            "item": session["item"],
            "variant": session.get("variant"),
            "quantity": session["quantity"],
            "total": session["total"],
            "pickup_slot": session["pickup_slot"],
            "booking_reference": session.get("booking_reference"),
        }

        return OrderRepository.insert_order(order_data)

    @staticmethod
    def get_latest_order(phone):
        """
        Fetch the latest order for a customer.
        """
        return OrderRepository.get_latest_order(phone)

    @staticmethod
    def get_all_orders():
        """
        Fetch all orders.
        """
        return OrderRepository.get_all_orders()

    @staticmethod
    def get_orders_for_customer(phone):
        return OrderRepository.get_orders_for_customer(phone)
    @staticmethod
    def get_all_restaurants():

        return OrderRepository.get_all_restaurants()
    @staticmethod
    def get_order(order_id):
        """
        Fetch a single order.
        """
        return OrderRepository.get_order_by_id(order_id)

    @staticmethod
    def update_order_status(order_id, status):
        """
        Update order status after validation.
        """

        allowed_status = [
            "Pending",
            "Preparing",
            "Ready",
            "Completed",
            "Cancelled"
        ]

        if status not in allowed_status:
            return False

        OrderRepository.update_status(order_id, status)
        return True

    @staticmethod
    def cancel_order(order_id, phone):
        order = OrderRepository.get_order_by_id(order_id)
        if not order or order["customer_phone"] != phone:
            return False, "Order not found."
        if order["status"] not in ("Pending", "Preparing"):
            return False, "This order can no longer be cancelled."
        OrderRepository.update_status(order_id, "Cancelled")
        return True, "Order cancelled successfully."

    @staticmethod
    def delete_order(order_id):
        """
        Delete an order.
        """
        OrderRepository.delete_order(order_id)

    @staticmethod
    def search_orders(keyword):
        """
        Search orders.
        """
        return OrderRepository.search_orders(keyword)

    @staticmethod
    def filter_orders(status=None, restaurant=None):
        """
        Filter orders.
        """
        return OrderRepository.filter_orders(status, restaurant)

    @staticmethod
    def get_dashboard_stats():
        """
        Dashboard statistics.
        """

        return {
            "total_orders": OrderRepository.count_orders(),
            "pending_orders": OrderRepository.count_pending(),
            "preparing_orders": OrderRepository.count_preparing(),
            "today_revenue": OrderRepository.today_revenue()
        }
