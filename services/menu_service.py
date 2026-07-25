from data.menu_loader import (
    get_areas,
    get_restaurants,
    get_categories,
    get_items,
    search_menu,
)
import re


def show_areas():

    areas = get_areas()

    message = "📍 Select an Area\n\n"

    for i, area in enumerate(areas, start=1):
        message += f"{i}. {area}\n"

    return message


def show_restaurants(area):

    restaurants = get_restaurants(area)

    message = f"🍽 Restaurants in {area}\n\n"

    for i, restaurant in enumerate(restaurants, start=1):
        message += f"{i}. {restaurant}\n"

    return message


def show_categories(area, restaurant):

    categories = get_categories(area, restaurant)

    message = f"📋 Categories in {restaurant}\n\n"

    for i, category in enumerate(categories, start=1):
        message += f"{i}. {category}\n"

    return message


def show_items(area, restaurant, category):

    items = get_items(area, restaurant, category)

    message = (
        f"🍽 {restaurant}\n"
        f"📂 {category}\n\n"
    )

    for i, item in enumerate(items, start=1):

        variant = item["Variant"]

        if variant:
            name = f"{item['Item']} ({variant})"
        else:
            name = item["Item"]

        stock_status = " 🚫 *(OUT OF STOCK)*" if item.get("is_out_of_stock") else ""

        message += (
            f"{i}. {name}{stock_status}\n"
            f"💰 ₹{item['Price']:.0f}\n\n"
        )

    return message



def get_area_by_index(index):

    areas = get_areas()

    if 1 <= index <= len(areas):
        return areas[index - 1]

    return None


def get_restaurant_by_index(area, index):

    restaurants = get_restaurants(area)

    if 1 <= index <= len(restaurants):
        return restaurants[index - 1]

    return None


def get_category_by_index(area, restaurant, index):

    categories = get_categories(area, restaurant)

    if 1 <= index <= len(categories):
        return categories[index - 1]

    return None


def get_item_by_index(area, restaurant, category, index):

    items = get_items(area, restaurant, category)

    if 1 <= index <= len(items):
        return items[index - 1]

    return None


def search_items(query, max_price=None):
    match = re.search(r"(?:under|below|less than)\s*(?:₹|rs\.?\s*)?(\d+(?:\.\d+)?)", query, re.I)
    if match and max_price is None:
        max_price = float(match.group(1))
    cleaned_query = re.sub(r"(?:under|below|less than)\s*(?:₹|rs\.?\s*)?\d+(?:\.\d+)?", "", query, flags=re.I)
    stop_words = {
        "i", "want", "something", "show", "me", "a", "an", "the", "with", "food",
        "please", "order", "can", "have", "from", "for", "at", "in", "get", "give",
        "bring", "buy", "buying", "need", "like", "to", "some", "suggest"
    }
    words = [word for word in cleaned_query.split() if word.lower() not in stop_words]
    # Simple plural stemming (e.g., 'burgers' -> 'burger', 'pizzas' -> 'pizza')
    stemmed = []
    for w in words:
        if len(w) > 3 and w.lower().endswith("s") and not w.lower().endswith("ss"):
            stemmed.append(w[:-1])
        else:
            stemmed.append(w)

    cleaned_query = " ".join(stemmed)
    if not cleaned_query.strip():
        cleaned_query = query

    items = search_menu(cleaned_query)
    # If no results with stemmed query, try original words
    if not items and words:
        items = search_menu(" ".join(words))

    if max_price is not None:
        items = [item for item in items if float(item["Price"]) <= max_price]
    return items




def find_matching_items(item_query, restaurant_query=None, limit=20):
    results = search_items(item_query)
    if restaurant_query:
        rest_lower = restaurant_query.lower()
        return [r for r in results if rest_lower in r["Restaurant"].lower()][:limit]
    return results[:limit]

