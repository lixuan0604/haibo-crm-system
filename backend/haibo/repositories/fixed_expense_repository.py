from haibo.db.schema import require_tables


def ensure_ready(cursor):
    require_tables(cursor)


def fetch_expense_rows(cursor):
    cursor.execute(
        """
        SELECT e.id, e.parent_id, e.name, e.note, e.period_text, e.annual_amount, e.sort_order,
               COALESCE(p.paid_amount, 0) AS paid_amount
        FROM fixed_expenses e
        LEFT JOIN (
          SELECT expense_id, SUM(amount) AS paid_amount
          FROM payments
          GROUP BY expense_id
        ) p ON p.expense_id = e.id
        ORDER BY e.sort_order ASC, e.id ASC
        """
    )
    return cursor.fetchall()


def fetch_payment_rows(cursor):
    cursor.execute(
        """
        SELECT id, expense_id, seq_no, amount, paid_on, remark
        FROM payments
        ORDER BY expense_id ASC, seq_no ASC, id ASC
        """
    )
    return cursor.fetchall()


def next_sort_order(cursor):
    cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_sort FROM fixed_expenses")
    return cursor.fetchone()["next_sort"]


def find_expense(cursor, expense_id):
    cursor.execute("SELECT id, parent_id FROM fixed_expenses WHERE id = %s", (expense_id,))
    return cursor.fetchone()


def count_children(cursor, expense_id):
    cursor.execute("SELECT COUNT(*) AS child_count FROM fixed_expenses WHERE parent_id = %s", (expense_id,))
    return cursor.fetchone()["child_count"]


def insert_expense(cursor, parent_id, name, note, period_text, annual_amount, sort_order, source_row=None):
    cursor.execute(
        """
        INSERT INTO fixed_expenses
          (parent_id, name, note, period_text, annual_amount, sort_order, source_row)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (parent_id, name, note, period_text, annual_amount, sort_order, source_row),
    )
    return cursor.lastrowid


def update_expense(cursor, expense_id, parent_id, name, note, period_text, annual_amount):
    cursor.execute(
        """
        UPDATE fixed_expenses
        SET parent_id = %s, name = %s, note = %s, period_text = %s, annual_amount = %s
        WHERE id = %s
        """,
        (parent_id, name, note, period_text, annual_amount, expense_id),
    )


def delete_payments(cursor, expense_id):
    cursor.execute("DELETE FROM payments WHERE expense_id = %s", (expense_id,))


def insert_payment(cursor, expense_id, seq_no, amount, paid_on, remark):
    cursor.execute(
        """
        INSERT INTO payments (expense_id, seq_no, amount, paid_on, remark)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (expense_id, seq_no, amount, paid_on, remark),
    )


def delete_expense(cursor, expense_id):
    cursor.execute("UPDATE fixed_expenses SET parent_id = NULL WHERE parent_id = %s", (expense_id,))
    cursor.execute("DELETE FROM fixed_expenses WHERE id = %s", (expense_id,))


def clear_all(cursor):
    cursor.execute("UPDATE fixed_expenses SET parent_id = NULL")
    cursor.execute("DELETE FROM fixed_expenses")
