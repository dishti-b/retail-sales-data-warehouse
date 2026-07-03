import os
import random

import pandas as pd


RAW_FILE_PATH = "data/raw/retail_sales_dataset.csv"
CLEANED_DATA_PATH = "data/cleaned"

random.seed(42)


def ensure_cleaned_folder():
    os.makedirs(CLEANED_DATA_PATH, exist_ok=True)


def clean_column_names(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def create_customers_table(df):
    customers = (
        df[["customer_id", "gender", "age"]]
        .drop_duplicates()
        .copy()
    )

    cities = ["Vancouver", "Surrey", "Burnaby", "Richmond", "Coquitlam", "Langley", "Delta"]

    customers["city"] = [random.choice(cities) for _ in range(len(customers))]
    customers["province"] = "BC"
    customers["loyalty_member"] = [random.choice([True, False]) for _ in range(len(customers))]

    return customers


def create_products_table(df):
    categories = sorted(df["product_category"].unique())

    products = []
    product_id = 1

    for category in categories:
        category_prices = df[df["product_category"] == category]["price_per_unit"]
        avg_price = round(category_prices.mean(), 2)

        products.append({
            "product_id": product_id,
            "product_category": category,
            "product_name": f"{category} Product",
            "unit_price": avg_price,
            "cost_price": round(avg_price * 0.55, 2)
        })

        product_id += 1

    return pd.DataFrame(products)


def create_stores_table():
    stores = [
        [1, "UrbanFit Vancouver", "Vancouver", "BC", "Mall"],
        [2, "UrbanFit Surrey", "Surrey", "BC", "Mall"],
        [3, "UrbanFit Burnaby", "Burnaby", "BC", "Mall"],
        [4, "UrbanFit Richmond", "Richmond", "BC", "Outlet"],
        [5, "UrbanFit Coquitlam", "Coquitlam", "BC", "Mall"],
        [6, "UrbanFit Online", "Online", "BC", "E-commerce"],
    ]

    return pd.DataFrame(
        stores,
        columns=["store_id", "store_name", "city", "province", "store_type"]
    )


def create_transactions_table(df):
    transactions = df[[
        "transaction_id",
        "date",
        "customer_id",
        "total_amount"
    ]].copy()

    transactions["transaction_date"] = pd.to_datetime(transactions["date"])
    transactions = transactions.drop(columns=["date"])

    store_ids = [1, 2, 3, 4, 5, 6]
    payment_methods = ["Credit Card", "Debit Card", "Gift Card", "Cash", "Mobile Payment"]

    transactions["store_id"] = [random.choice(store_ids) for _ in range(len(transactions))]
    transactions["payment_method"] = [random.choice(payment_methods) for _ in range(len(transactions))]

    return transactions[[
        "transaction_id",
        "customer_id",
        "store_id",
        "transaction_date",
        "payment_method",
        "total_amount"
    ]]


def create_transaction_items_table(df, products):
    category_to_product_id = dict(zip(products["product_category"], products["product_id"]))

    transaction_items = df[[
        "transaction_id",
        "product_category",
        "quantity",
        "price_per_unit",
        "total_amount"
    ]].copy()

    transaction_items.insert(0, "transaction_item_id", range(1, len(transaction_items) + 1))
    transaction_items["product_id"] = transaction_items["product_category"].map(category_to_product_id)
    transaction_items = transaction_items.rename(columns={
        "price_per_unit": "unit_price",
        "total_amount": "line_total"
    })

    return transaction_items[[
        "transaction_item_id",
        "transaction_id",
        "product_id",
        "quantity",
        "unit_price",
        "line_total"
    ]]


def create_inventory_table(stores, products):
    inventory = []
    inventory_id = 1

    for _, store in stores.iterrows():
        for _, product in products.iterrows():
            stock_quantity = random.randint(0, 150)
            reorder_level = random.randint(20, 50)

            inventory.append({
                "inventory_id": inventory_id,
                "store_id": store["store_id"],
                "product_id": product["product_id"],
                "stock_quantity": stock_quantity,
                "reorder_level": reorder_level,
            })

            inventory_id += 1

    return pd.DataFrame(inventory)


def save_table(df, file_name):
    output_path = os.path.join(CLEANED_DATA_PATH, file_name)
    df.to_csv(output_path, index=False)
    print(f"Saved {output_path} with {len(df)} rows")


def main():
    ensure_cleaned_folder()

    print("Reading raw Kaggle dataset...")
    df = pd.read_csv(RAW_FILE_PATH)

    print("Cleaning columns...")
    df = clean_column_names(df)

    print("Creating warehouse tables...")
    customers = create_customers_table(df)
    products = create_products_table(df)
    stores = create_stores_table()
    transactions = create_transactions_table(df)
    transaction_items = create_transaction_items_table(df, products)
    inventory = create_inventory_table(stores, products)

    print("Saving cleaned tables...")
    save_table(customers, "customers.csv")
    save_table(products, "products.csv")
    save_table(stores, "stores.csv")
    save_table(transactions, "transactions.csv")
    save_table(transaction_items, "transaction_items.csv")
    save_table(inventory, "inventory.csv")

    print("Kaggle data cleaning complete.")


if __name__ == "__main__":
    main()