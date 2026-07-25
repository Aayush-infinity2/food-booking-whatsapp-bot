from services.menu_service import (
    show_areas,
    show_restaurants,
    show_categories,
    show_items,
    get_area_by_index,
    get_restaurant_by_index,
    get_category_by_index,
    get_item_by_index,
)
from services.order_service import OrderService
from services.ai_service import process_natural_language_message, food_recommendations

# Stores conversation data for each user
user_sessions = {}
pickup_slots = {
    "1": "10:00 AM",
    "2": "11:00 AM",
    "3": "12:00 PM",
    "4": "01:00 PM",
    "5": "02:00 PM",
}


def get_main_menu():
    return """
🍔 *Welcome to LPU Food Booking Bot* 🍔

Please choose an option:

1️⃣ View Menu
2️⃣ Pre Book Food
3️⃣ Track Order
4️⃣ Help

(Type the option number)
"""


def _try_natural_language_override(session, message, default_error):
    if message.isdigit() or len(message) <= 2:
        return default_error

    session["state"] = "MAIN_MENU"
    return process_natural_language_message(session, message)


def process_message(sender, message):

    message = message.strip().lower()

    # Create session for new users
    if sender not in user_sessions:
        user_sessions[sender] = {
            "state": "MAIN_MENU",
            "area": None,
            "restaurant": None,
            "category": None,
            "item": None,
            "variant": None,
            "price": 0,
            "quantity": 1,
            "pickup_slot": None,
            "total": 0,
        }

    session = user_sessions[sender]
    state = session["state"]

    # ----------------------------------------
    # User can return to main menu anytime
    # ----------------------------------------
    if message in ["hi", "hello", "hey", "start", "menu", "home", "cancel", "stop", "reset", "back", "exit"]:

        session["state"] = "MAIN_MENU"

        return get_main_menu()

    # ----------------------------------------
    # MAIN MENU
    # ----------------------------------------
    if state == "MAIN_MENU":

        if message == "1":

            session["state"] = "AREA_SELECTION"

            return show_areas()

        elif message == "2":

            return "🚧 Pre Booking feature is under development."

        elif message == "3":

            order = OrderService.get_latest_order(sender)

            if order is None:
                return """
📦 Track Order

You haven't placed any orders yet.

Type 1 to view the menu.
"""

            return f"""
📦 Latest Order

🆔 Order ID: #{order['id']}

🏪 Restaurant:
{order['restaurant']}

🍽 Item:
{order['item']}

🔢 Quantity:
{order['quantity']}

💰 Total:
₹{order['total']}

🕒 Pickup:
{order['pickup_slot']}

📌 Status:
{order['status']}
"""

        elif message == "4":

            return """
❓ Help

Type:

1 → View Menu

2 → Pre Book Food

3 → Track Order

Type 'menu' anytime to return to the main menu.
"""

        else:
            return process_natural_language_message(session, message)

    # ----------------------------------------
    # AREA SELECTION
    # ----------------------------------------
    elif state == "AREA_SELECTION":

        if not message.isdigit():
            return _try_natural_language_override(session, message, "❌ Please enter a valid area number.")

        area = get_area_by_index(int(message))

        if area is None:
            return "❌ Invalid Area.\nPlease choose a valid number."

        session["area"] = area
        session["state"] = "RESTAURANT_SELECTION"

        return show_restaurants(area)

    # ----------------------------------------
    # RESTAURANT SELECTION
    # ----------------------------------------
    elif state == "RESTAURANT_SELECTION":

        if not message.isdigit():
            return _try_natural_language_override(session, message, "❌ Please enter a valid restaurant number.")

        restaurant = get_restaurant_by_index(
            session["area"],
            int(message)
        )

        if restaurant is None:
            return "❌ Invalid restaurant.\nPlease choose a valid number."

        session["restaurant"] = restaurant
        session["state"] = "CATEGORY_SELECTION"

        return show_categories(
            session["area"],
            restaurant
        )

    # ----------------------------------------
    # CATEGORY SELECTION
    # ----------------------------------------
    elif state == "CATEGORY_SELECTION":
        if not message.isdigit():
            return _try_natural_language_override(session, message, "❌ Please enter a valid category number.")

        category = get_category_by_index(
            session["area"],
            session["restaurant"],
            int(message)
        )

        if category is None:
            return "❌ Invalid category."

        session["category"] = category
        session["state"] = "ITEM_SELECTION"

        return show_items(
            session["area"],
            session["restaurant"],
            category
        )

    # ----------------------------------------
    # ITEM SELECTION
    # ----------------------------------------
    elif state == "ITEM_SELECTION":

        if not message.isdigit():
            return _try_natural_language_override(session, message, "❌ Please enter a valid item number.")

        item = get_item_by_index(
            session["area"],
            session["restaurant"],
            session["category"],
            int(message)
        )

        if item is None:
            return "❌ Invalid Item."

        session["item"] = item["Item"]
        session["variant"] = item["Variant"]
        session["price"] = float(item["Price"])

        session["state"] = "QUANTITY_SELECTION"

        return f"""
🍽 Selected Item

{session['item']}

Variant : {session['variant']}

Price : ₹{session['price']}

-------------------------

Enter Quantity
(Example : 1,2,3...)
"""

    # ----------------------------------------
    # CANDIDATE SELECTION
    # ----------------------------------------
    elif state == "CANDIDATE_SELECTION":
        candidates = session.get("menu_candidates", [])
        if message.isdigit():
            idx = int(message)
            if 1 <= idx <= len(candidates):
                best = candidates[idx - 1]
                variant_str = f" ({best['Variant']})" if best.get("Variant") else ""

                if best.get("is_out_of_stock"):
                    return f"🚫 Sorry, *{best['Item']}{variant_str}* at *{best['Restaurant']}* is currently *OUT OF STOCK*.\n\n🍽️ Please select another option number or type *menu* to return to the main menu."

                session["area"] = best["Area"]
                session["restaurant"] = best["Restaurant"]
                session["category"] = best["Category"]
                session["item"] = best["Item"]
                session["variant"] = best["Variant"]
                session["price"] = float(best["Price"])
                session.pop("menu_candidates", None)

                quantity = session.get("quantity", 1)
                if quantity > 1:
                    session["total"] = session["price"] * quantity
                    session["state"] = "PICKUP_SELECTION"
                    return f"""🍽 Selected Item: *{session['item']}{variant_str}*
🏪 Restaurant: {session['restaurant']}
🔢 Quantity: {session['quantity']}
💰 Total Amount: ₹{session['total']:.0f}

Choose Pickup Slot:
1️⃣ 10:00 AM
2️⃣ 11:00 AM
3️⃣ 12:00 PM
4️⃣ 01:00 PM
5️⃣ 02:00 PM"""
                else:
                    session["state"] = "QUANTITY_SELECTION"
                    return f"""🍽 Selected Item: *{session['item']}{variant_str}*
🏪 Restaurant: {session['restaurant']}
💰 Price: ₹{session['price']:.0f}

-------------------------
Enter Quantity (e.g. 1, 2, 3...)"""


        return _try_natural_language_override(session, message, "❌ Please reply with a valid option number (e.g. 1, 2...).")

    # ----------------------------------------
    # QUANTITY
    # ----------------------------------------

    elif state == "QUANTITY_SELECTION":

        if not message.isdigit():
            return _try_natural_language_override(session, message, "❌ Quantity should be a number.")

        quantity = int(message)

        if quantity <= 0:
            return "❌ Quantity should be greater than zero."

        session["quantity"] = quantity
        session["total"] = quantity * session["price"]
        session["state"] = "PICKUP_SELECTION"

        return f"""
📦 Quantity Selected : {quantity}

Total Amount

₹{session['total']}

Choose Pickup Slot

1️⃣ 10:00 AM
2️⃣ 11:00 AM
3️⃣ 12:00 PM
4️⃣ 01:00 PM
5️⃣ 02:00 PM
"""

    # ----------------------------------------
    # PICKUP
    # ----------------------------------------
    elif state == "PICKUP_SELECTION":

        if message not in pickup_slots:
            return _try_natural_language_override(session, message, "❌ Select a valid slot.")

        session["pickup_slot"] = pickup_slots[message]
        session["state"] = "ORDER_CONFIRMATION"

        return f"""
🧾 Order Summary

Area :
{session['area']}

Restaurant :
{session['restaurant']}

Category :
{session['category']}

Item :
{session['item']}

Variant :
{session['variant']}

Quantity :
{session['quantity']}

Pickup :
{session['pickup_slot']}

Total :
₹{session['total']}

----------------------

Reply

YES

to Confirm

or

NO

to Cancel
"""

    # ----------------------------------------
    # CONFIRM
    # ----------------------------------------
    elif state == "ORDER_CONFIRMATION":

        if message.lower() == "yes":

            try:
                order_id = OrderService.save_order(session, sender)
                session["state"] = "ORDER_PLACED"

                return f"""
🎉 Order Confirmed

Thank you for ordering.

Your order has been placed successfully.

🆔 Order ID: #{order_id}

Pickup Time:
{session['pickup_slot']}

We'll notify you once it is ready.
"""

            except Exception as e:
                return f"❌ Failed to save order.\n{str(e)}"

        elif message.lower() == "no":

            user_sessions[sender]["state"] = "MAIN_MENU"
            return get_main_menu()

        return _try_natural_language_override(session, message, "Reply YES to confirm or NO to cancel.")

    # ----------------------------------------
    # FALLBACK
    # ----------------------------------------
    return "Something went wrong. Type 'menu' to restart."
