import pandas as pd

# Load CSV only once when application starts
df = pd.read_csv("data/menu.csv")

# Clean data
df.columns = df.columns.str.strip()
df.fillna("", inplace=True)
for col in df.columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

# Some source rows contain formatted values such as "₹60". Store prices as numbers
# so filtering, totals, and checkout logic are reliable.
df["Price"] = pd.to_numeric(
    df["Price"].str.replace(r"[^0-9.]", "", regex=True), errors="coerce"
)

# Remove completely empty rows
df = df[(df["Area"] != "") & df["Price"].notna()]

# Remove duplicate rows
df = df.drop_duplicates()

# --------------------------------------------------------------------------
# Out-of-Stock Management State
# --------------------------------------------------------------------------
out_of_stock_keys = set()


def make_item_key(restaurant, item, variant=""):
    return (str(restaurant).strip().lower(), str(item).strip().lower(), str(variant or "").strip().lower())


def is_out_of_stock(restaurant, item, variant=""):
    return make_item_key(restaurant, item, variant) in out_of_stock_keys


def toggle_out_of_stock(restaurant, item, variant=""):
    key = make_item_key(restaurant, item, variant)
    if key in out_of_stock_keys:
        out_of_stock_keys.remove(key)
        return False
    else:
        out_of_stock_keys.add(key)
        return True


def get_areas():
    areas = (
        df["Area"]
        .dropna()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
    )
    return sorted(areas)


def get_restaurants(area):
    filtered = df[df["Area"] == area]
    return sorted(filtered["Restaurant"].unique())


def get_categories(area, restaurant):
    filtered = df[
        (df["Area"] == area)
        & (df["Restaurant"] == restaurant)
    ]
    return sorted(filtered["Category"].unique())


def get_items(area, restaurant, category):
    filtered = df[
        (df["Area"] == area)
        & (df["Restaurant"] == restaurant)
        & (df["Category"] == category)
    ]
    records = filtered[["Item", "Variant", "Price"]].to_dict(orient="records")
    for r in records:
        r["is_out_of_stock"] = is_out_of_stock(restaurant, r["Item"], r.get("Variant", ""))
    return records


def search_menu(query, limit=60):
    terms = [term for term in query.lower().split() if term]
    filtered = df.copy()
    searchable = (
        filtered["Area"] + " " + filtered["Restaurant"] + " " + filtered["Category"] + " "
        + filtered["Item"] + " " + filtered["Variant"]
    ).str.lower()
    for term in terms:
        filtered = filtered[searchable.loc[filtered.index].str.contains(term, regex=False)]
    records = filtered[["Area", "Restaurant", "Category", "Item", "Variant", "Price"]].head(limit).to_dict(orient="records")
    for r in records:
        r["is_out_of_stock"] = is_out_of_stock(r["Restaurant"], r["Item"], r.get("Variant", ""))
    return records
