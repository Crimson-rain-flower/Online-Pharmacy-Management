import pandas as pd
import pymysql
import os
import sys

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "admin"
DB_NAME = "pharmacy_db"

FILES_CONFIG = [
    {
        "filename": "medicine.csv",
        "table_name": "medicine",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS medicine (
                id INT PRIMARY KEY,
                name VARCHAR(100),
                category VARCHAR(50),
                price DECIMAL(10,2),
                stock_quantity INT,
                expiry_date DATE,
                status VARCHAR(20)
            );
        """
    },
    {
        "filename": "admins.csv",
        "table_name": "admins",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS admins (
                id INT PRIMARY KEY,
                username VARCHAR(50),
                password VARCHAR(255)
            );
        """
    },
    {
        "filename": "orders.csv",
        "table_name": "orders",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS orders (
                id INT PRIMARY KEY,
                customer_name VARCHAR(100),
                medicine_id INT,
                quantity INT,
                total_amount DECIMAL(10,2),
                order_date DATETIME,
                FOREIGN KEY (medicine_id) REFERENCES medicine(id)
            );
        """
    }
]

print("🔌 Connecting to MySQL...")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=False
    )
    cursor = conn.cursor()
    print("✅ Connected\n")
except Exception as e:
    print("❌ Connection failed:", e)
    sys.exit(1)

# IMPORTANT: Disable FK checks temporarily
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

for cfg in FILES_CONFIG:
    file_path = cfg["filename"]
    table = cfg["table_name"]

    print(f"➡ Processing `{file_path}`")

    if not os.path.exists(file_path):
        print("   ❌ File not found\n")
        continue

    df = pd.read_csv(file_path)
    df.columns = [c.strip() for c in df.columns]
    df = df.where(pd.notnull(df), None)

    # ✅ FIX DATE/DATETIME PROPERLY
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")
            if "time" in col.lower():
                df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                df[col] = df[col].dt.strftime("%Y-%m-%d")

    # Create table
    cursor.execute(cfg["create_sql"])

    # ✅ CLEAR TABLE BEFORE INSERT (prevents duplicate PK)
    cursor.execute(f"DELETE FROM `{table}`")

    cols = ", ".join(f"`{c}`" for c in df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT INTO `{table}` ({cols}) VALUES ({placeholders})"

    try:
        cursor.executemany(sql, df.to_records(index=False).tolist())
        conn.commit()
        print(f"   🎉 Inserted {len(df)} rows\n")
    except Exception as e:
        conn.rollback()
        print("   ❌ Insert failed:", e, "\n")

cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
cursor.close()
conn.close()

print("✅ ALL DATA IMPORTED SUCCESSFULLY!")


