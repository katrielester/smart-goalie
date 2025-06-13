import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("goal_planner.db", check_same_thread=False)
cursor = conn.cursor()

# Table to store user information
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    prolific_code TEXT,
    has_completed_training BOOLEAN DEFAULT 0,
    group_assignment TEXT
)
""")# Add group_assignment column if it doesn't exist
try:
    cursor.execute("ALTER TABLE users ADD COLUMN group_assignment TEXT DEFAULT '2'")
except sqlite3.OperationalError:
    pass  # Column already exists, no action needed

# Table to store chat history
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Table to store SMART goals
cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    goal_text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Table to store subtasks for each goal
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    task_text TEXT NOT NULL,
    completed BOOLEAN DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals (id)
)
""")

# Table to store weekly reflections per goal
cursor.execute("""
CREATE TABLE IF NOT EXISTS reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    goal_id INTEGER,
    reflection_text TEXT NOT NULL,
    week_number INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals (id)
)
""")

conn.commit()

# -------------------------------
# Helper functions
# -------------------------------

def create_user(user_id, prolific_code=None, group="2"):
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, prolific_code, group_assignment)
        VALUES (?, ?, ?)
    """, (user_id, prolific_code, group))
    conn.commit()

def mark_training_completed(user_id):
    cursor.execute("UPDATE users SET has_completed_training = 1 WHERE user_id = ?", (user_id,))
    conn.commit()

def user_completed_training(user_id):
    cursor.execute("SELECT has_completed_training FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row is not None and row[0] == 1

def save_message_to_db(user_id, sender, message):
    cursor.execute(
        "INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)",
        (user_id, sender, message)
    )
    conn.commit()

def get_chat_history(user_id):
    cursor.execute(
        "SELECT sender, message FROM chat_history WHERE user_id = ? ORDER BY id",
        (user_id,)
    )
    return cursor.fetchall()

def save_goal(user_id, goal_text):
    cursor.execute(
        "INSERT INTO goals (user_id, goal_text) VALUES (?, ?)",
        (user_id, goal_text)
    )
    conn.commit()
    return cursor.lastrowid

def get_goals(user_id):
    cursor.execute("SELECT id, goal_text FROM goals WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def save_task(goal_id, task_text):
    cursor.execute(
        "INSERT INTO tasks (goal_id, task_text) VALUES (?, ?)",
        (goal_id, task_text)
    )
    conn.commit()

def get_tasks(goal_id):
    cursor.execute("SELECT id, task_text, completed FROM tasks WHERE goal_id = ?", (goal_id,))
    return cursor.fetchall()

def update_task_completion(task_id, completed):
    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
    conn.commit()

def save_reflection(user_id, goal_id, reflection_text, week_number):
    cursor.execute(
        "INSERT INTO reflections (user_id, goal_id, reflection_text, week_number) VALUES (?, ?, ?, ?)",
        (user_id, goal_id, reflection_text, week_number)
    )
    conn.commit()

def get_reflections(user_id):
    cursor.execute("SELECT goal_id, reflection_text, week_number FROM reflections WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def user_goals_exist(user_id):
    cursor.execute("SELECT COUNT(*) FROM goals WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0] > 0