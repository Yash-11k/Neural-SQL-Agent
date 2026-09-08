import sqlite3
import pandas as pd

# File name for local database
DB_NAME = "ecommerce.db"

def make_database():
    # Connect to SQLite (it creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Drop tables if we are re-running this script
    cursor.execute("DROP TABLE IF EXISTS orders;")
    cursor.execute("DROP TABLE IF EXISTS products;")
    cursor.execute("DROP TABLE IF EXISTS customers;")

    # 1. Create Customers Table
    cursor.execute("""
        CREATE TABLE customers (
            cust_id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT
        );
    """)

    # 2. Create Products Table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            item_name TEXT,
            category TEXT,
            price REAL
        );
    """)

    # 3. Create Orders Table
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            cust_id INTEGER,
            product_id INTEGER,
            amount REAL
        );
    """)

    # Adding sample customers
    customers_list = [
        (1, "Yash Kagra", "Rohtak"),
        (2, "Aaman Sharma", "Delhi"),
        (3, "Rohan Verma", "Mumbai"),
        (4, "Priya Singh", "Bangalore")
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers_list)

    # Adding sample products
    products_list = [
        (101, "Laptop", "Electronics", 60000),
        (102, "Phone", "Electronics", 25000),
        (103, "Shoes", "Fashion", 3000),
        (104, "Chair", "Furniture", 5000)
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products_list)

    # Adding sample orders
    orders_list = [
        (1, 1, 101, 60000), # Yash bought Laptop
        (2, 1, 103, 3000),  # Yash bought Shoes
        (3, 2, 102, 25000), # Aaman bought Phone
        (4, 3, 104, 5000)   # Rohan bought Chair
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders_list)

    # Save changes and close
    conn.commit()
    conn.close()
    print("Database built successfully!")

# Simple function to return schema details to the LLM
# Kept as-is: used as a fallback if the dynamic schema check ever fails.
def get_schema():
    return """
    Table 1: customers (cust_id, name, city)
    Table 2: products (product_id, item_name, category, price)
    Table 3: orders (order_id, cust_id, product_id, amount)
    """


def load_csv_to_db(file, table_name="user_data"):
    """
    Reads an uploaded CSV and loads it into SQLite as a table.
    - `file` can be a path string OR a file-like object (e.g. Streamlit's
      st.file_uploader result, which pandas can read directly).
    - if_exists="replace" means a fresh upload overwrites the old
      user_data table instead of stacking duplicate rows.
    Returns the table name and its column list so the caller can confirm
    to the user what was loaded.
    """
    df = pd.read_csv(file)

    # Clean column names a bit: spaces/special chars break SQL queries
    df.columns = [
        str(col).strip().lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    ]

    conn = sqlite3.connect(DB_NAME)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

    return table_name, list(df.columns)


def get_dynamic_schema():
    """
    Instead of a hardcoded string, this looks at whatever tables ACTUALLY
    exist in the SQLite file right now (sample e-commerce tables, or a
    freshly uploaded CSV table, or both) and builds the schema text from
    that. This is what makes the agent CSV-agnostic.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # sqlite_master is SQLite's internal catalog of tables/indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        conn.close()
        return get_schema()  # nothing exists yet, fall back to static sample

    schema_text = ""
    for table in tables:
        # PRAGMA table_info returns column metadata: (cid, name, type, ...)
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]
        schema_text += f"Table: {table} ({', '.join(columns)})\n"

    conn.close()
    return schema_text


if __name__ == "__main__":
    make_database()