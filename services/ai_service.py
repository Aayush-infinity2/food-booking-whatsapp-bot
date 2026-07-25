"""Gemini-backed intent extraction and conversational AI for WhatsApp food ordering."""
import json
import os
import re
import requests

from services.menu_service import search_items, find_matching_items


def _extract_json(text):
    """Extract clean JSON object from Gemini response text."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)


def _extract_local_intent(message):
    """Local fallback intent parser when Gemini API is unconfigured or unreachable."""
    msg = message.strip()

    # Pattern: "order 2 biryani from tripti" or "biryani from tripti"
    match_from = re.search(r"(?:order|get|buy|want|have)?\s*(?:(\d+)\s+)?(.*?)\s+from\s+(.*)", msg, re.I)
    if match_from:
        qty_str, item, rest = match_from.groups()
        # Clean extra slots or times if present
        slot_match = re.search(r"(10:00 AM|11:00 AM|12:00 PM|01:00 PM|02:00 PM)", rest, re.I)
        pickup_slot = slot_match.group(1).upper() if slot_match else None
        if slot_match:
            rest = re.sub(r"(?:at|slot)?\s*(10:00 AM|11:00 AM|12:00 PM|01:00 PM|02:00 PM)", "", rest, flags=re.I).strip()

        return {
            "intent": "ORDER",
            "item": item.strip() if item else None,
            "restaurant": rest.strip() if rest else None,
            "quantity": int(qty_str) if qty_str else None,
            "pickup_slot": pickup_slot,
            "max_price": None,
            "response_text": None,
        }

    # Pattern: "order 2 burgers" or "get pizza"
    match_order = re.search(r"^(?:order|get|buy|have|want)\s*(?:(\d+)\s+)?(.*)", msg, re.I)
    if match_order:
        qty_str, item = match_order.groups()
        return {
            "intent": "ORDER",
            "item": item.strip() if item else None,
            "restaurant": None,
            "quantity": int(qty_str) if qty_str else None,
            "pickup_slot": None,
            "max_price": None,
            "response_text": None,
        }

    return {
        "intent": "SEARCH",
        "item": msg,
        "restaurant": None,
        "quantity": None,
        "pickup_slot": None,
        "max_price": None,
        "response_text": None,
    }


def _get_llm_intent(message):
    """Query Gemini to analyze user intent and extract order details."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    prompt = f"""You are an AI assistant for a university campus food ordering bot (LPU Food Bot).
Analyze the following user message and classify the intent into one of:
- "ORDER": User explicitly wants to order/buy specific food items (e.g. "order a pizza from dominos", "get me 2 burgers").
- "SEARCH": User is asking to see menu, food options, recommendations, or items under a price (e.g. "what pizzas do you have?", "food under 150").
- "GENERAL_QA": User is asking general questions, greeting, or asking about help, status, hours.

Return ONLY a valid JSON object matching this exact schema:
{{
  "intent": "ORDER" | "SEARCH" | "GENERAL_QA",
  "item": "extracted food item name or short search terms, or null",
  "restaurant": "extracted restaurant name or null",
  "quantity": integer_quantity_or_null,
  "pickup_slot": "exact slot like '10:00 AM', '11:00 AM', '12:00 PM', '01:00 PM', '02:00 PM' or null",
  "max_price": number_or_null,
  "response_text": "friendly short direct reply if GENERAL_QA or null"
}}

User message: "{message}"
"""

    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 200},
            },
            timeout=12,
        )
        response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        intent_data = _extract_json(text)
        return intent_data
    except Exception:
        return None


def process_natural_language_message(session, message):
    """
    Processes free-form natural language messages.
    If order details are recognized, updates the session dictionary and state machine.
    Otherwise returns AI recommendations or friendly Q&A responses.
    """
    intent_data = _get_llm_intent(message)

    # Fallback to local intent extraction if Gemini API is absent or fails
    if not intent_data or not isinstance(intent_data, dict):
        intent_data = _extract_local_intent(message)

    intent = intent_data.get("intent", "SEARCH")
    item_query = intent_data.get("item")
    restaurant_query = intent_data.get("restaurant")
    quantity = intent_data.get("quantity")
    pickup_slot = intent_data.get("pickup_slot")
    max_price = intent_data.get("max_price")
    response_text = intent_data.get("response_text")

    # 1. Handle ORDER Intent
    if intent == "ORDER" and (item_query or restaurant_query):
        search_term = item_query if item_query else (restaurant_query or message)
        candidates = find_matching_items(search_term, restaurant_query)

        if candidates:
            # Sort candidates by price ascending (best price first)
            candidates = sorted(candidates, key=lambda x: float(x.get("Price", 0)))

            # If user explicitly specified restaurant OR there is only 1 candidate, pick it directly
            if restaurant_query or len(candidates) == 1:
                best = candidates[0]
                variant_str = f" ({best['Variant']})" if best.get("Variant") else ""

                if best.get("is_out_of_stock"):
                    return f"🚫 Sorry, *{best['Item']}{variant_str}* at *{best['Restaurant']}* is currently *OUT OF STOCK*.\n\n🍽️ Please try ordering another item or type *1* to browse available menu options."

                session["area"] = best["Area"]
                session["restaurant"] = best["Restaurant"]
                session["category"] = best["Category"]
                session["item"] = best["Item"]
                session["variant"] = best["Variant"]
                session["price"] = float(best["Price"])

                # Check if quantity was provided
                if quantity and isinstance(quantity, int) and quantity > 0:
                    session["quantity"] = quantity
                    session["total"] = session["price"] * quantity

                    # Check if pickup slot was also provided
                    valid_slots = {"10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM"}
                    if pickup_slot in valid_slots:
                        session["pickup_slot"] = pickup_slot
                        session["state"] = "ORDER_CONFIRMATION"

                        return f"""🧾 *Order Summary*

Area: {session['area']}
Restaurant: {session['restaurant']}
Category: {session['category']}
Item: {session['item']}{variant_str}
Quantity: {session['quantity']}
Pickup Slot: {session['pickup_slot']}
Total: ₹{session['total']:.0f}

----------------------
Reply *YES* to confirm or *NO* to cancel."""
                    else:
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

            else:
                # Multiple options across restaurants, present candidate options sorted by price
                top_candidates = candidates[:5]
                session["menu_candidates"] = top_candidates
                session["state"] = "CANDIDATE_SELECTION"
                if quantity and isinstance(quantity, int) and quantity > 0:
                    session["quantity"] = quantity

                lines = [f"🍔 Here are the best *{search_term.title()}* options across campus (sorted by price):", ""]
                for i, item in enumerate(top_candidates, start=1):
                    variant = f" ({item['Variant']})" if item.get("Variant") else ""
                    stock = " 🚫 *(OUT OF STOCK)*" if item.get("is_out_of_stock") else ""
                    lines.append(f"{i}️⃣ *{item['Item']}{variant}*{stock} — ₹{item['Price']:.0f}")
                    lines.append(f"   🏪 {item['Restaurant']} · {item['Area']}\n")

                lines.append("Reply with option number (e.g. 1, 2...) to select.")
                return "\n".join(lines)


        else:
            # Item not found at the specific restaurant
            alt_items = search_items(search_term)[:5] if search_term else []
            rest_items = search_items(restaurant_query)[:3] if restaurant_query else []

            lines = []
            if restaurant_query and item_query:
                lines.append(f"❌ *{restaurant_query.title()}* does not have *'{item_query.title()}'* on their menu.\n")

            if alt_items:
                lines.append(f"🍽️ Here are *{search_term.title()}* options at other restaurants:")
                for item in alt_items:
                    var = f" ({item['Variant']})" if item.get("Variant") else ""
                    lines.append(f"• {item['Item']}{var} — ₹{item['Price']:.0f} ({item['Restaurant']})")

            if rest_items:
                lines.append(f"\n💡 Popular items at *{restaurant_query.title()}*:")
                for item in rest_items:
                    var = f" ({item['Variant']})" if item.get("Variant") else ""
                    lines.append(f"• {item['Item']}{var} — ₹{item['Price']:.0f}")

            if not lines:
                return f"❌ Sorry, I couldn't find '{search_term}' on the menu.\n\nType *1* to view all restaurants or search again."

            lines.append("\nType the item name to order or type *1* to browse.")
            return "\n".join(lines)


    # 2. Handle GENERAL_QA
    if intent == "GENERAL_QA" and response_text:
        return response_text

    # 3. Handle SEARCH / Recommendation Intent
    search_term = item_query or message
    results = search_items(search_term, max_price)[:5]
    if not results:
        return "I couldn't find an exact match for your request. Type *1* to browse the full menu."

    lines = ["🍽️ I found these options:", ""]
    for item in results:
        variant = f" ({item['Variant']})" if item.get("Variant") else ""
        lines.append(f"• {item['Item']}{variant} — ₹{item['Price']:.0f}")
        lines.append(f"  {item['Restaurant']} · {item['Area']}")
    lines.extend(["", "Type the item name to order or type *1* to browse."])
    return "\n".join(lines)


def food_recommendations(message):
    """Return a WhatsApp-ready recommendation, with a local search fallback."""
    results = search_items(message)[:5]
    if not results:
        return "I couldn't find an exact match. Type *1* to browse the full menu."

    lines = ["🍽️ I found these options:", ""]
    for item in results:
        variant = f" ({item['Variant']})" if item.get("Variant") else ""
        lines.append(f"• {item['Item']}{variant} — ₹{item['Price']:.0f}")
        lines.append(f"  {item['Restaurant']} · {item['Area']}")
    lines.extend(["", "Type *1* to browse and place an order."])
    return "\n".join(lines)


