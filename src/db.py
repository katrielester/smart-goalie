# db.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def execute_query(query, params=(), fetch="one", commit=False):
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "all":
                return cursor.fetchall()
            else:
                return None
    except Exception as e:
        print("Database error:", e)
        conn.rollback()
        return None if fetch == "one" else []


# -------------------------------
# Helper functions
# -------------------------------

def create_user(user_id, prolific_code=None, group="2"):
    execute_query("""
        INSERT INTO users (user_id, prolific_code, group_assignment)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, prolific_code, group), commit=True)


def get_user_info(user_id):
    return execute_query("""
        SELECT prolific_code, has_completed_training, group_assignment
        FROM users WHERE user_id = %s
    """, (user_id,), fetch="one")


def get_user_group(user_id):
    row = execute_query("SELECT group_assignment FROM users WHERE user_id = %s", (user_id,))
    return row["group_assignment"] if row else None


def mark_training_completed(user_id):
    execute_query(
        "UPDATE users SET has_completed_training = TRUE WHERE user_id = %s",
        (user_id,), commit=True
    )
    update_user_phase(user_id, 1)


def user_completed_training(user_id):
    row = execute_query(
        "SELECT has_completed_training FROM users WHERE user_id = %s",
        (user_id,)
    )
    return row and row.get("has_completed_training", False)


def get_user_phase(user_id):
    row = execute_query("SELECT phase FROM users WHERE user_id = %s", (user_id,))
    return row["phase"] if row else None


def update_user_phase(user_id, new_phase):
    execute_query(
        "UPDATE users SET phase = %s WHERE user_id = %s",
        (new_phase, user_id), commit=True
    )


def save_message_to_db(user_id, sender, message):
    execute_query("""
        INSERT INTO chat_history (user_id, sender, message)
        VALUES (%s, %s, %s)
    """, (user_id, sender, message), commit=True)


def get_chat_history(user_id):
    return execute_query("""
        SELECT sender, message FROM chat_history
        WHERE user_id = %s ORDER BY id
    """, (user_id,), fetch="all")


def save_goal(user_id, goal_text):
    row = execute_query("""
        INSERT INTO goals (user_id, goal_text)
        VALUES (%s, %s)
        RETURNING id
    """, (user_id, goal_text), commit=True)
    return row["id"] if row else None


def get_goals(user_id):
    return execute_query(
        "SELECT id, goal_text FROM goals WHERE user_id = %s",
        (user_id,), fetch="all"
    )


def save_task(goal_id, task_text):
    execute_query("""
        INSERT INTO tasks (goal_id, task_text)
        VALUES (%s, %s)
    """, (goal_id, task_text), commit=True)

def get_tasks(goal_id, active_only=True):
    ...
    query = """
        SELECT id, task_text, completed FROM tasks
        WHERE goal_id = %s
    """
    if active_only:
        query += " AND status = 'active'"
    return execute_query(query, (goal_id,), fetch="all")


def update_task_completion(task_id, completed):
    execute_query("""
        UPDATE tasks SET completed = %s WHERE id = %s
    """, (completed, task_id), commit=True)


def save_reflection(user_id, goal_id, content, week_number, session_id="a"):
    execute_query("""
        INSERT INTO reflections (user_id, goal_id, reflection_text, week_number, session_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, goal_id, content, week_number, session_id), commit=True)


def get_reflections(user_id):
    return execute_query("""
        SELECT goal_id, reflection_text, week_number FROM reflections
        WHERE user_id = %s
    """, (user_id,), fetch="all")


def user_goals_exist(user_id):
    row = execute_query("SELECT COUNT(*) FROM goals WHERE user_id = %s", (user_id,))
    return row and row["count"] > 0


def get_last_reflection(user_id, goal_id):
    return execute_query("""
        SELECT reflection_text, week_number FROM reflections
        WHERE user_id = %s AND goal_id = %s
        ORDER BY week_number DESC LIMIT 1
    """, (user_id, goal_id), fetch="one")


def get_next_week_number(user_id, goal_id):
    row = execute_query("""
        SELECT MAX(week_number) FROM reflections
        WHERE user_id = %s AND goal_id = %s
    """, (user_id, goal_id), fetch="one")
    return (row["max"] or 0) + 1 if row else 1


def reflection_exists(user_id, goal_id, week_number, session_id):
    row = execute_query("""
        SELECT 1 FROM reflections
        WHERE user_id = %s AND goal_id = %s AND week_number = %s AND session_id = %s
        LIMIT 1
    """, (user_id, goal_id, week_number, session_id))
    return row is not None

# count only active tasks
def get_goals_with_task_counts(user_id):
    return execute_query("""
        SELECT g.id, g.goal_text, COUNT(t.id) AS task_count
        FROM goals g
        LEFT JOIN tasks t ON g.id = t.goal_id AND t.status = 'active'
        WHERE g.user_id = %s
        GROUP BY g.id, g.goal_text
    """, (user_id,), fetch="all")

def archive_task(task_id, replaced_by_task_id=None, reason=None):
    execute_query("""
        UPDATE tasks
        SET status = 'archived',
            replaced_by_task_id = %s,
            replacement_reason = %s
        WHERE id = %s
    """, (replaced_by_task_id, reason, task_id), commit=True)

def replace_or_modify_task(goal_id, old_task_id, new_task_text, reason="Replaced"):
    # Insert new task
    execute_query("""
        INSERT INTO tasks (goal_id, task_text)
        VALUES (%s, %s)
    """, (goal_id, new_task_text), commit=True)

    # Get new task ID
    new_task_row = execute_query("""
        SELECT id FROM tasks
        WHERE goal_id = %s AND task_text = %s
        ORDER BY id DESC LIMIT 1
    """, (goal_id, new_task_text), fetch="one")

    new_task_id = new_task_row["id"] if new_task_row else None

    # Archive old task
    execute_query("""
        UPDATE tasks
        SET status = 'archived',
            replaced_by_task_id = %s,
            replacement_reason = %s
        WHERE id = %s
    """, (new_task_id, reason, old_task_id), commit=True)

    return new_task_id


# PHASES
# 0 = registered but not done onboarding
# 1 = training done
# 2 = initial goal and task entered (onboarding done)
# 3 = first reflection done
# 4 = second reflection done