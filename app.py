from flask import Flask, jsonify
import pymysql
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "pharmacy_db",
    "cursorclass": pymysql.cursors.DictCursor
}


def get_db_connection():
    return pymysql.connect(**db_config)


@app.route("/api/dashboard")
def dashboard_data():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # KPIs
            cursor.execute("SELECT COUNT(*) AS count FROM medicine")
            products = cursor.fetchone()["count"]
           
            cursor.execute("SELECT COALESCE(SUM(total_amount),0) AS revenue FROM orders")
            revenue = cursor.fetchone()["revenue"]


            cursor.execute("SELECT SUM(stock_quantity) AS total_stock FROM medicine")
            stock_volume = cursor.fetchone()["total_stock"] or 0


            cursor.execute("SELECT COUNT(*) AS count FROM medicine WHERE stock_quantity = 0")
            oos = cursor.fetchone()["count"]


            # Charts & Tables
            cursor.execute("SELECT name, expiry_date, stock_quantity FROM medicine ORDER BY expiry_date ASC LIMIT 10")
            expiring = cursor.fetchall()


            cursor.execute("SELECT customer_name, total_amount FROM orders ORDER BY order_date DESC LIMIT 10")
            recent_orders = cursor.fetchall()


            cursor.execute("""
                SELECT MONTHNAME(order_date) as month, SUM(total_amount) as amount
                FROM orders GROUP BY MONTH(order_date), month ORDER BY MONTH(order_date)
            """)
            monthly_sales = cursor.fetchall()


            # Doughnut Chart: Stock by Category
            cursor.execute("SELECT category, SUM(stock_quantity) as value FROM medicine GROUP BY category")
            category_data = cursor.fetchall()


            return jsonify({
                "products": products,
                "revenue": float(revenue),
                "stock": stock_volume,
                "oos": oos,
                "expiring": expiring,
                "recent_orders": recent_orders,
                "monthly_sales": monthly_sales,
                "category_dist": category_data
            })
    finally:
        conn.close()


@app.route("/api/products")
def get_products():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, category, price, stock_quantity, status FROM medicine")
            return jsonify(cursor.fetchall())
    finally:
        conn.close()


@app.route("/api/purchases")
def get_purchases():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT o.id, o.customer_name, m.name as medicine, o.quantity, o.total_amount, o.order_date
                FROM orders o
                JOIN medicine m ON o.medicine_id = m.id
                ORDER BY o.order_date DESC
            """)
            return jsonify(cursor.fetchall())
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)



