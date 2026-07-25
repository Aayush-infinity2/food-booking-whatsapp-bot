import re
import uuid
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from repositories.student_repository import StudentRepository
from services.menu_service import search_items
from services.order_service import OrderService

student_bp = Blueprint("student", __name__, url_prefix="/student")


def _logged_in():
    return bool(session.get("student_registration"))


@student_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        registration_number = request.form.get("registration_number", "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9-]{4,30}", registration_number):
            flash("Enter a valid registration number.", "danger")
            return render_template("student/login.html")

        student = StudentRepository.get_by_registration(registration_number)
        if not student:
            full_name = request.form.get("full_name", "").strip()
            phone = request.form.get("phone", "").strip()
            if not full_name or not re.fullmatch(r"\d{10,15}", phone):
                flash("New students need a name and a valid WhatsApp number.", "danger")
                return render_template("student/login.html")
            try:
                StudentRepository.create(registration_number, full_name, phone)
            except Exception:
                flash("This phone number is already linked to another student.", "danger")
                return render_template("student/login.html")
            student = StudentRepository.get_by_registration(registration_number)

        session["student_registration"] = student["registration_number"]
        session["student_name"] = student["full_name"]
        session["student_phone"] = student["phone"]
        session.setdefault("student_cart", [])
        return redirect(url_for("student.menu"))
    return render_template("student/login.html")


@student_bp.route("/")
def menu():
    if not _logged_in():
        return redirect(url_for("student.login"))
    query = request.args.get("q", "").strip()
    max_price = request.args.get("max_price", type=float)
    items = search_items(query, max_price) if query else []
    return render_template("student/menu.html", query=query, max_price=max_price, items=items,
                           cart=session.get("student_cart", []))


@student_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    if not _logged_in():
        return redirect(url_for("student.login"))
    item = {key: request.form.get(key, "").strip() for key in ("area", "restaurant", "category", "item", "variant")}
    try:
        item["price"] = float(request.form["price"])
        item["quantity"] = max(1, min(int(request.form.get("quantity", 1)), 20))
    except (KeyError, ValueError):
        flash("Invalid menu item.", "danger")
        return redirect(url_for("student.menu"))
    cart = session.get("student_cart", [])
    cart.append(item)
    session["student_cart"] = cart
    flash(f"{item['item']} added to cart.", "success")
    return redirect(request.referrer or url_for("student.menu"))


@student_bp.route("/cart/remove/<int:index>", methods=["POST"])
def remove_from_cart(index):
    cart = session.get("student_cart", [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session["student_cart"] = cart
    return redirect(url_for("student.cart"))


@student_bp.route("/cart")
def cart():
    if not _logged_in():
        return redirect(url_for("student.login"))
    cart_items = session.get("student_cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    return render_template("student/cart.html", cart=cart_items, total=total)


@student_bp.route("/checkout", methods=["POST"])
def checkout():
    if not _logged_in():
        return redirect(url_for("student.login"))
    cart_items = session.get("student_cart", [])
    pickup_slot = request.form.get("pickup_slot", "")
    if not cart_items or pickup_slot not in {"10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM"}:
        flash("Choose a pickup slot and add at least one item.", "danger")
        return redirect(url_for("student.cart"))
    reference = str(uuid.uuid4())
    for item in cart_items:
        OrderService.save_order({**item, "total": item["price"] * item["quantity"], "pickup_slot": pickup_slot,
                                 "booking_reference": reference}, session["student_phone"])
    session["student_cart"] = []
    flash("Order placed successfully.", "success")
    return redirect(url_for("student.orders"))


@student_bp.route("/orders")
def orders():
    if not _logged_in():
        return redirect(url_for("student.login"))
    return render_template("student/orders.html", orders=OrderService.get_orders_for_customer(session["student_phone"]))


@student_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    if not _logged_in():
        return redirect(url_for("student.login"))
    success, message = OrderService.cancel_order(order_id, session["student_phone"])
    flash(message, "success" if success else "danger")
    return redirect(url_for("student.orders"))


@student_bp.route("/logout")
def logout():
    for key in ("student_registration", "student_name", "student_phone", "student_cart"):
        session.pop(key, None)
    return redirect(url_for("student.login"))
