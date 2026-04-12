import sqlite3

conn = sqlite3.connect("queens.db")
cursor = conn.cursor()

# Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solution TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    solution TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    time REAL
)
""")

conn.commit()


# Save solution
def save_solution(solution):
    try:
        cursor.execute("INSERT INTO solutions (solution) VALUES (?)", (solution,))
        conn.commit()
        return True
    except:
        return False


def save_player(name, solution):
    cursor.execute("INSERT INTO players (name, solution) VALUES (?,?)", (name, solution))
    conn.commit()


def save_performance(type_, time_):
    cursor.execute("INSERT INTO performance (type, time) VALUES (?,?)", (type_, time_))
    conn.commit()