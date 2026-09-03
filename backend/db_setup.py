import sqlite3

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
        (5, "Kamal", "Pune")
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers_list)

    # Adding sample products
    products_list = [
        (101, "Laptop", "Electronics", 60000),
        (102, "Phone", "Electronics", 25000),
        (103, "Shoes", "Fashion", 3000),
        (104, "Chair", "Furniture", 5000),
        (105, "Table", "Furniture", 7000)
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products_list)

    # Adding sample orders
    orders_list = [
        (1, 1, 101, 60000), # Yash bought Laptop
        (2, 1, 103, 3000),  # Yash bought Shoes
        (3, 2, 102, 25000), # Aaman bought Phone
        (4, 3, 104, 5000)   # Rohan bought Chair
        (5,1,105, 7000) # Kamal Bought Table
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders_list)

    # Save changes and close
    conn.commit()
    conn.close()
    print("Database built successfully!")

# Simple function to return schema details to the LLM
def get_schema():
    return """
    Table 1: customers (cust_id, name, city)
    Table 2: products (product_id, item_name, category, price)
    Table 3: orders (order_id, cust_id, product_id, amount)
    """

if __name__ == "__main__":
    make_database()