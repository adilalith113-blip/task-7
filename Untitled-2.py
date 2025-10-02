#!/usr/bin/env python3
"""
Basic Sales Summary
Creates a tiny SQLite database (sales_data.db) with a 'sales' table,
inserts sample data (only if table is empty), runs simple SQL queries,
prints results and plots a bar chart of revenue by product.

Run: python Basic_Sales_Summary.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_FILE = "sales_data.db"


def create_db_and_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)
    conn.commit()


def insert_sample_data_if_empty(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sales")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"Database already has {count} rows — skipping sample insert.")
        return
    sample_data = [
        ("2025-09-01","Widget A", 5, 9.99),
        ("2025-09-01","Widget B", 3, 14.50),
        ("2025-09-02","Widget A", 2, 9.99),
        ("2025-09-03","Gadget C", 10, 4.75),
        ("2025-09-03","Widget B", 1, 14.50),
        ("2025-09-04","Gadget C", 4, 4.75),
        ("2025-09-05","Widget A", 7, 9.99),
        ("2025-09-05","Gadget C", 2, 4.75),
    ]
    cur.executemany("INSERT INTO sales (sale_date, product, quantity, price) VALUES (?, ?, ?, ?)", sample_data)
    conn.commit()
    print(f"Inserted {len(sample_data)} sample rows into sales table.")


def run_queries_and_plot(conn):
    query = """
    SELECT product, SUM(quantity) AS total_qty, SUM(quantity * price) AS revenue
    FROM sales
    GROUP BY product
    ORDER BY revenue DESC
    """
    df = pd.read_sql_query(query, conn)
    print("\nSales summary by product:")
    print(df.to_string(index=False))

    # Totals
    totals_query = "SELECT SUM(quantity) AS total_quantity, SUM(quantity * price) AS total_revenue FROM sales"
    totals = pd.read_sql_query(totals_query, conn)
    print("\nOverall totals:")
    print(totals.to_string(index=False))

    # Top-selling product by quantity
    if not df.empty:
        top_qty = df.loc[df['total_qty'].idxmax()]
        print(f"\nTop-selling product by quantity: {top_qty['product']} (qty {int(top_qty['total_qty'])})")

    # Bar chart of revenue by product
    if not df.empty:
        ax = df.plot(kind='bar', x='product', y='revenue', legend=False)
        ax.set_xlabel("Product")
        ax.set_ylabel("Revenue")
        ax.set_title("Revenue by Product")
        plt.tight_layout()
        chart_file = "sales_chart.png"
        plt.savefig(chart_file)
        print(f"\nSaved bar chart to: {os.path.abspath(chart_file)}")
        plt.show()
    else:
        print("No data to plot.")


def main():
    conn = sqlite3.connect(DB_FILE)
    create_db_and_table(conn)
    insert_sample_data_if_empty(conn)
    run_queries_and_plot(conn)
    conn.close()


if __name__ == "__main__":
    main()
