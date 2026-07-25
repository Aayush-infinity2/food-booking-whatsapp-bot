from flask import Blueprint, render_template, redirect, request, url_for, flash, session

from services.order_service import OrderService

from services.order_service import OrderService

orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/admin/orders"
)
@orders_bp.route("/")
def index():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    try:
        orders = OrderService.get_all_orders()
        restaurants = OrderService.get_all_restaurants()
        stats = OrderService.get_dashboard_stats()
    except Exception as e:
        print(f"Error loading orders data: {e}")
        orders = []
        restaurants = []
        stats = {"total_orders": 0, "pending_orders": 0, "preparing_orders": 0, "today_revenue": 0}
        flash("Could not connect to MySQL database. Please verify your Aiven credentials on Render or run python init_db.py.", "warning")

    return render_template(
        "admin/orders.html",
        orders=orders,
        restaurants=restaurants,
        stats=stats
)
@orders_bp.route("/status/<int:order_id>", methods=["POST"])
def update_status(order_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    status = request.form.get("status")

    if OrderService.update_order_status(order_id, status):
        flash("Order updated successfully", "success")
    else:
        flash("Invalid Status", "danger")

    return redirect(url_for("orders.index"))
@orders_bp.route("/delete/<int:order_id>", methods=["POST"])
def delete(order_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    OrderService.delete_order(order_id)

    flash("Order Deleted", "success")

    return redirect(url_for("orders.index"))
