import sqlite3
from datetime import datetime
import os

# Construct the absolute path to the project root directory
# __file__ is database/db_handler.py -> os.path.dirname(__file__) is database/
# -> os.path.join(..., '..') is personal_finance_bot/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE = os.path.join(PROJECT_ROOT, "finance_data.db")

def init_db():
    """Initializes the database and creates the expenses table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            value REAL NOT NULL,
            description TEXT,
            category TEXT,
            timestamp DATETIME NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_expense(user_id: int, value: float, description: str, category: str):
    """Adds a new expense to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now()
    cursor.execute("""
        INSERT INTO expenses (user_id, value, description, category, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, value, description, category, timestamp))
    conn.commit()
    conn.close()

def get_expenses_by_category_for_month(user_id: int, month: int, year: int) -> list[tuple[str, float]]:
    """
    Retrieves expenses for a given user, month, and year, grouped by category.
    Month should be 1-12.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Ensure month is formatted with a leading zero if needed for strftime
    month_str = f"{month:02d}"
    year_str = str(year)
    cursor.execute("""
        SELECT category, SUM(value)
        FROM expenses
        WHERE user_id = ? AND strftime('%m', timestamp) = ? AND strftime('%Y', timestamp) = ?
        GROUP BY category
    """, (user_id, month_str, year_str))
    results = cursor.fetchall()
    conn.close()
    return results

def get_expenses_for_month(user_id: int, month: int, year: int) -> list[tuple]:
    """
    Retrieves all expenses for a given user, month, and year.
    Month should be 1-12.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Ensure month is formatted with a leading zero if needed for strftime
    month_str = f"{month:02d}"
    year_str = str(year)
    cursor.execute("""
        SELECT id, user_id, value, description, category, timestamp
        FROM expenses
        WHERE user_id = ? AND strftime('%m', timestamp) = ? AND strftime('%Y', timestamp) = ?
    """, (user_id, month_str, year_str))
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    init_db()
    # Add some dummy data
    add_expense(1, 50.0, "Groceries", "Food")
    add_expense(1, 25.5, "Movie ticket", "Entertainment")
    add_expense(1, 15.0, "Lunch", "Food") # Same month as groceries
    add_expense(2, 70.0, "Concert", "Entertainment")

    # Test retrieval for user 1, current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    print(f"--- Expenses for User 1, Month {current_month}, Year {current_year} ---")
    user1_expenses = get_expenses_for_month(1, current_month, current_year)
    for expense in user1_expenses:
        print(expense)

    print(f"\n--- Expenses by Category for User 1, Month {current_month}, Year {current_year} ---")
    user1_expenses_by_cat = get_expenses_by_category_for_month(1, current_month, current_year)
    for cat_total in user1_expenses_by_cat:
        print(cat_total)

    # Test with a different month/year or user if needed
    # Example: add expense for a different month
    # from datetime import timedelta
    # past_date = datetime.now() - timedelta(days=40)
    # conn = sqlite3.connect(DB_FILE)
    # cursor = conn.cursor()
    # cursor.execute("""
    #     INSERT INTO expenses (user_id, value, description, category, timestamp)
    #     VALUES (?, ?, ?, ?, ?)
    # """, (1, 100.0, "Old bill", "Utilities", past_date))
    # conn.commit()
    # conn.close()
    # print(f"\n--- Expenses by Category for User 1, Month {past_date.month}, Year {past_date.year} ---")
    # user1_past_expenses = get_expenses_by_category_for_month(1, past_date.month, past_date.year)
    # for cat_total in user1_past_expenses:
    #       print(cat_total)
