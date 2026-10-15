import duckdb
import os

DB_PATH = "data/sample_sales.duckdb"

def init_sample_db():
    """Creates a local DuckDB file and populates a sample e-commerce table for testing."""
    os.makedirs("data", exist_ok=True)
    con = duckdb.connect(DB_PATH)
    
    # Create a sample orders & products table
    con.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            order_id INTEGER,
            order_date DATE,
            customer_name VARCHAR,
            product_category VARCHAR,
            item_name VARCHAR,
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            total_revenue DECIMAL(10,2),
            region VARCHAR
        );
    """)
    
    # Check if table is empty; if so, insert mock data
    count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    if count == 0:
        con.execute("""
            INSERT INTO sales VALUES
            (1, '2026-01-10', 'Rahul Sharma', 'Electronics', 'Wireless Mouse', 2, 25.00, 50.00, 'North'),
            (2, '2026-01-12', 'Priya Patel', 'Apparel', 'Cotton Hoodie', 1, 45.00, 45.00, 'West'),
            (3, '2026-01-15', 'Amit Kumar', 'Electronics', 'Mechanical Keyboard', 1, 80.00, 80.00, 'South'),
            (4, '2026-01-20', 'Ananya Roy', 'Home & Kitchen', 'Air Fryer', 1, 120.00, 120.00, 'East'),
            (5, '2026-02-02', 'Rahul Sharma', 'Apparel', 'Running Shoes', 1, 60.00, 60.00, 'North'),
            (6, '2026-02-10', 'Vikram Singh', 'Electronics', 'Noise-Canceling Headphones', 1, 150.00, 150.00, 'North'),
            (7, '2026-02-14', 'Priya Patel', 'Home & Kitchen', 'Electric Kettle', 2, 35.00, 70.00, 'West'),
            (8, '2026-02-20', 'Neha Gupta', 'Electronics', 'Wireless Mouse', 3, 25.00, 75.00, 'South'),
            (9, '2026-03-01', 'Amit Kumar', 'Apparel', 'Cotton Hoodie', 2, 45.00, 90.00, 'South'),
            (10, '2026-03-05', 'Ananya Roy', 'Electronics', 'Mechanical Keyboard', 1, 80.00, 80.00, 'East');
        """)
    con.close()

def get_db_connection():
    return duckdb.connect(DB_PATH, read_only=True)

def get_table_schema() -> str:
    """Returns compact table schema metadata to pass into LLM prompts (low token count)."""
    con = get_db_connection()
    schema_info = con.execute("DESCRIBE sales;").fetchall()
    con.close()
    
    schema_str = "Table: sales\nColumns:\n"
    for row in schema_info:
        schema_str += f"- {row[0]} ({row[1]})\n"
    return schema_str
