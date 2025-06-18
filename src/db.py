import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("goal_planner.db", check_same_thread=False)
cursor = conn.cursor()

# Enforce foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON")

# Table to store user information
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    prolific_code TEXT,
    has_completed_training BOOLEAN DEFAULT 0,
    group_assignment TEXT CHECK(group_assignment IN ('1','2')) DEFAULT '2'
)
""")

# Ensure group_assignment column exists (safe fallback)
try:
    cursor.execute("ALTER TABLE users ADD COLUMN group_assignment TEXT CHECK(group_assignment IN ('1','2')) DEFAULT '2'")
except sqlite3.OperationalError:
    pass  # Column already exists

# Table to store chat history
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    sender TEXT NOT NULL CHECK(sender IN ('user', 'bot')),
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# Table to store SMART goals
cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    goal_text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
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
    FOREIGN KEY (goal_id) REFERENCES goals(id)
)
""")

# Table to store weekly reflections per goal
cursor.execute("""
CREATE TABLE IF NOT EXISTS reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    goal_id INTEGER,
    reflection_text TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (goal_id) REFERENCES goals(id)
)
""")

# Performance indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_goal_id ON tasks(goal_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_reflections_user_goal ON reflections(user_id, goal_id)")

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

def get_user_info(user_id):
    cursor.execute("SELECT prolific_code, has_completed_training, group_assignment FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

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

def get_last_reflection(user_id, goal_id):
    cursor.execute("""
        SELECT reflection_text, week_number FROM reflections
        WHERE user_id = ? AND goal_id = ?
        ORDER BY week_number DESC LIMIT 1
    """, (user_id, goal_id))
    return cursor.fetchone()


def get_next_week_number(user_id, goal_id):
    cursor.execute("""
        SELECT MAX(week_number) FROM reflections
        WHERE user_id = ? AND goal_id = ?
    """, (user_id, goal_id))
    row = cursor.fetchone()
    return (row[0] or 0) + 1