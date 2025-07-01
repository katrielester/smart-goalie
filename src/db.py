# db.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cursor = conn.cursor()

# -------------------------------
# Helper functions
# -------------------------------

def create_user(user_id, prolific_code=None, group="2"):
    cursor.execute("""
        INSERT INTO users (user_id, prolific_code, group_assignment)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, prolific_code, group))
    conn.commit()

def get_user_info(user_id):
    cursor.execute("SELECT prolific_code, has_completed_training, group_assignment FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

def get_user_group(user_id):
    cursor.execute("SELECT group_assignment FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    return row["group_assignment"] if row else None

def mark_training_completed(user_id):
    cursor.execute("UPDATE users SET has_completed_training = TRUE WHERE user_id = %s", (user_id,))
    conn.commit()
    update_user_phase(user_id,1)

def user_completed_training(user_id):
    cursor.execute("SELECT has_completed_training FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    if row is None or "has_completed_training" not in row:
        return False
    return row["has_completed_training"]

def get_user_phase(user_id):
    cursor.execute("SELECT phase FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    return row["phase"]

def update_user_phase(user_id, new_phase):
    cursor.execute("UPDATE users SET phase = %s WHERE user_id = %s", (new_phase, user_id))
    conn.commit()

# 0 = registered but not done onboarding
# 1 = training done
# 2 = initial goal and task entered (onboarding done)
# 3 = first reflection done
# 4 = second reflection done

def save_message_to_db(user_id, sender, message):
    cursor.execute(
        "INSERT INTO chat_history (user_id, sender, message) VALUES (%s, %s, %s)",
        (user_id, sender, message)
    )
    conn.commit()

def get_chat_history(user_id):
    cursor.execute(
        "SELECT sender, message FROM chat_history WHERE user_id = %s ORDER BY id",
        (user_id,)
    )
    return cursor.fetchall()

def save_goal(user_id, goal_text):
    cursor.execute(
        "INSERT INTO goals (user_id, goal_text) VALUES (%s, %s) RETURNING id",
        (user_id, goal_text)
    )
    conn.commit()
    return cursor.fetchone()["id"]

def get_goals(user_id):
    cursor.execute("SELECT id, goal_text FROM goals WHERE user_id = %s", (user_id,))
    return cursor.fetchall()

def save_task(goal_id, task_text):
    cursor.execute(
        "INSERT INTO tasks (goal_id, task_text) VALUES (%s, %s)",
        (goal_id, task_text)
    )
    conn.commit()

def get_tasks(goal_id):
    try:
        goal_id = int(goal_id)
    except ValueError:
        return []

    cursor.execute("SELECT id, task_text, completed FROM tasks WHERE goal_id = %s", (goal_id,))
    return cursor.fetchall()

def update_task_completion(task_id, completed):
    cursor.execute("UPDATE tasks SET completed = %s WHERE id = %s", (completed, task_id))
    conn.commit()

def save_reflection(user_id, goal_id, content, week_number, session_id="a"):
    cursor.execute("""
        INSERT INTO reflections (user_id, goal_id, reflection_text, week_number, session_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, goal_id, content, week_number, session_id))
    conn.commit()

def get_reflections(user_id):
    cursor.execute("SELECT goal_id, reflection_text, week_number FROM reflections WHERE user_id = %s", (user_id,))
    return cursor.fetchall()

def user_goals_exist(user_id):
    cursor.execute("SELECT COUNT(*) FROM goals WHERE user_id = %s", (user_id,))
    return cursor.fetchone()["count"] > 0

def get_last_reflection(user_id, goal_id):
    cursor.execute("""
        SELECT reflection_text, week_number FROM reflections
        WHERE user_id = %s AND goal_id = %s
        ORDER BY week_number DESC LIMIT 1
    """, (user_id, goal_id))
    return cursor.fetchone()

def get_next_week_number(user_id, goal_id):
    cursor.execute("""
        SELECT MAX(week_number) FROM reflections
        WHERE user_id = %s AND goal_id = %s
    """, (user_id, goal_id))
    row = cursor.fetchone()
    return (row["max"] or 0) + 1

def reflection_exists(user_id, goal_id, week_number, session_id):
    cursor.execute("""
        SELECT 1 FROM reflections
        WHERE user_id = %s AND goal_id = %s AND week_number = %s AND session_id = %s
        LIMIT 1
    """, (user_id, goal_id, week_number, session_id))
    return cursor.fetchone() is not None

def get_goals_with_task_counts(user_id):
    cursor.execute("""
        SELECT g.id, g.goal_text, COUNT(t.id) AS task_count
        FROM goals g
        LEFT JOIN tasks t ON g.id = t.goal_id
        WHERE g.user_id = %s
        GROUP BY g.id, g.goal_text
    """, (user_id,))
    return cursor.fetchall()