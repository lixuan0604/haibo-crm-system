import pymysql


def list_categories(cursor):
    cursor.execute("SELECT name FROM monthly_categories ORDER BY sort_order ASC, id ASC")
    return [row["name"] for row in cursor.fetchall()]


def fetch_cells(cursor, year):
    cursor.execute(
        """
        SELECT c.name AS category, m.`month` AS month_no, m.amount AS amount
        FROM monthly_expenses m
        JOIN monthly_categories c ON c.id = m.category_id
        WHERE m.`year` = %s
        ORDER BY m.`month` ASC, c.sort_order ASC
        """,
        (year,),
    )
    return cursor.fetchall()


def list_years(cursor):
    cursor.execute("SELECT DISTINCT `year` AS year_no FROM monthly_expenses ORDER BY `year`")
    return [row["year_no"] for row in cursor.fetchall()]


def find_category(cursor, name):
    cursor.execute("SELECT id FROM monthly_categories WHERE name = %s", (name,))
    return cursor.fetchone()


def category_map(cursor):
    cursor.execute("SELECT id, name FROM monthly_categories")
    return {row["name"]: row["id"] for row in cursor.fetchall()}


def next_sort_order(cursor):
    cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_sort FROM monthly_categories")
    return cursor.fetchone()["next_sort"]


def insert_category(cursor, name, sort_order):
    cursor.execute(
        "INSERT INTO monthly_categories (name, sort_order) VALUES (%s, %s)",
        (name, sort_order),
    )
    return cursor.lastrowid


def insert_category_ignore(cursor, name, sort_order):
    cursor.execute(
        "INSERT IGNORE INTO monthly_categories (name, sort_order) VALUES (%s, %s)",
        (name, sort_order),
    )


def delete_cell(cursor, year, month, category_id):
    cursor.execute(
        "DELETE FROM monthly_expenses WHERE `year` = %s AND `month` = %s AND category_id = %s",
        (year, month, category_id),
    )


def upsert_cell(cursor, year, month, category_id, amount):
    cursor.execute(
        """
        INSERT INTO monthly_expenses (`year`, `month`, category_id, amount)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE amount = VALUES(amount)
        """,
        (year, month, category_id, amount),
    )


def delete_year(cursor, year):
    cursor.execute("DELETE FROM monthly_expenses WHERE `year` = %s", (year,))


def is_duplicate(error):
    return isinstance(error, pymysql.err.IntegrityError)
