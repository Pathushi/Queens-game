import sqlite3

DB_NAME = "queens.db"

def get_connection():
    """Provides a connection with row factory for easier data handling."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema with necessary tables and constraints."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Stores distinct solutions found by anyone (The 'Flag' table)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        board_state TEXT UNIQUE
    )""")
    
    # Stores player names and their specific correct responses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        solution TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Stores performance metrics for Sequential vs Threaded comparison
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT CHECK(type IN ('Sequential', 'Threaded')),
        solution_count INTEGER,
        time_taken REAL
    )""")
    
    conn.commit()
    conn.close()

def save_solution(board_state):
    """
    Attempts to save a new unique solution. 
    Returns True if saved, False if it already exists (the 'recognized' flag).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO solutions (board_state) VALUES (?)", (board_state,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This solution is already in the database
        return False
    finally:
        conn.close()

def save_player(name, solution):
    """Saves a player's successful identification of a solution."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO players (name, solution) VALUES (?, ?)", (name, solution))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def save_performance(method_type, count, time_taken):
    """Records the time taken and solutions found by the algorithms."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO performance (type, solution_count, time_taken) 
        VALUES (?, ?, ?)
    """, (method_type, count, time_taken))
    conn.commit()
    conn.close()

def get_found_count():
    """Returns the current number of unique solutions found by players."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM solutions").fetchone()[0]
    conn.close()
    return count

def clear_solution_flags():
    """
    Clears the unique solutions table so future players can 
    provide the same answers again.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM solutions")
    conn.commit()
    conn.close()
    print("System: Maximum solutions reached. Solutions table has been cleared.")

# Initialize the DB when this module is imported
init_db()