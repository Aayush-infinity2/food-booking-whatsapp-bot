from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from services.analytics_service import (
    get_orders_last_7_days,
    get_order_status_distribution,
    get_top_selling_items,
)
import os
from dotenv import load_dotenv
from services.order_service import OrderService
from repositories.student_repository import StudentRepository
from data.menu_loader import df, toggle_out_of_stock, is_out_of_stock

load_dotenv()

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin_bp.route("/")
def admin_root():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("admin.login"))


@admin_bp.route("/login", methods=["GET", "POST"])
@admin_bp.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username == os.getenv("ADMIN_USERNAME")
            and password == os.getenv("ADMIN_PASSWORD")
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))

        flash("Invalid Username or Password")

    return render_template("admin/login.html")



@admin_bp.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    try:
        orders = OrderService.get_all_orders()
        stats = OrderService.get_dashboard_stats()
    except Exception as e:
        print(f"Error loading dashboard data: {e}")
        orders = []
        stats = {"total_orders": 0, "pending_orders": 0, "preparing_orders": 0, "today_revenue": 0}
        flash("Could not connect to MySQL database. Please verify your Aiven credentials on Render or run python init_db.py.", "warning")

    return render_template(
        "admin/dashboard.html",
        orders=orders,
        stats=stats
    )



@admin_bp.route("/analytics")
def analytics():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    try:
        stats = OrderService.get_dashboard_stats()
        orders_chart = get_orders_last_7_days()
        status_chart = get_order_status_distribution()
        top_items = get_top_selling_items()
    except Exception as e:
        print(f"Error loading analytics data: {e}")
        stats = {"total_orders": 0, "pending_orders": 0, "preparing_orders": 0, "today_revenue": 0}
        orders_chart = []
        status_chart = []
        top_items = []
        flash("Could not connect to MySQL database. Please verify your Aiven credentials on Render or run python init_db.py.", "warning")

    return render_template(
        "admin/analytics.html",
        stats=stats,
        orders_chart=orders_chart,
        status_chart=status_chart,
        top_items=top_items
    )


@admin_bp.route("/menu")
def menu():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    menu_items = df.to_dict(orient="records")
    return render_template("admin/menu.html", menu_items=menu_items)


@admin_bp.route("/students")
def students():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    try:
        students_list = StudentRepository.get_all()
    except Exception as e:
        print(f"Error loading students directory: {e}")
        students_list = []
        flash("Could not connect to MySQL database. Please verify your Aiven credentials on Render or run python init_db.py.", "warning")

    return render_template("admin/students.html", students=students_list)



@admin_bp.route("/update-status/<int:order_id>", methods=["POST"])
def update_status(order_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    status = request.form.get("status")
    OrderService.update_order_status(order_id, status)

    return redirect(request.referrer or url_for("admin.dashboard"))


@admin_bp.route("/menu/toggle-stock", methods=["POST"])
def toggle_stock():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    restaurant = request.form.get("restaurant", "")
    item = request.form.get("item", "")
    variant = request.form.get("variant", "")

    is_out = toggle_out_of_stock(restaurant, item, variant)
    status_str = "OUT OF STOCK" if is_out else "IN STOCK"
    flash(f"Marked '{item}' at '{restaurant}' as {status_str}.", "warning" if is_out else "success")
    return redirect(request.referrer or url_for("admin.menu"))


@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))