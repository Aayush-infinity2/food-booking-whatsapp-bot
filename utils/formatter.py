from datetime import datetime


def format_currency(amount):
    return f"₹{float(amount):,.2f}"


def format_datetime(value):

    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    return value.strftime("%d %b %Y | %I:%M %p")


def mask_phone(phone):
    return f"+91 {phone[:5]}*****"