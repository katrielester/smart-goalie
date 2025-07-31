# db.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor

import json

DATABASE_URL = "postgresql://smart_goalie_db_user:C2FCtmsiG3XKlApXVBtDO73noloz72LR@dpg-d19rim95pdvs73a49kn0-a.frankfurt-postgres.render.com/smart_goalie_db"
# DATABASE_URL = os.environ.get("DATABASE_URL")

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

def create_user(user_id, prolific_code=None, group="0"):
    execute_query("""
        INSERT INTO users (user_id, prolific_code, group_assignment)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, prolific_code, group), commit=True)


def get_user_info(user_id):
    return execute_query("""
        SELECT prolific_code, has_completed_training, group_assignment, has_completed_presurvey, has_completed_postsurvey
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


def save_message_to_db(user_id, sender, message, timestamp, phase=None):
    execute_query(
        """
        INSERT INTO chat_history (user_id, sender, message, timestamp, phase)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, sender, message, timestamp, phase),
        fetch=None,
        commit=True
    )


def get_chat_history(user_id, phase):
    return execute_query("""
        SELECT sender,
               message,
               timestamp
          FROM chat_history
         WHERE user_id = %s
           AND phase = %s
      ORDER BY timestamp ASC;
    """, (user_id, phase), fetch="all")



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
        INSERT INTO tasks (goal_id, task_text, status)
        VALUES (%s, %s, 'active')
    """, (goal_id, task_text), commit=True)

def get_tasks(goal_id, active_only=True):
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
    row = execute_query("""
        INSERT INTO reflections (user_id, goal_id, reflection_text, week_number, session_id, completed)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        RETURNING id
    """, (user_id, goal_id, content, week_number, session_id), fetch="one", commit=True)
    
    return row["id"] if row else None

def save_reflection_response(reflection_id, task_id=None, progress_rating=None, update_type=None, updated_task_text=None, answer_key=None, answer_text=None):
    execute_query("""
        INSERT INTO reflection_responses (
            reflection_id, task_id, progress_rating, update_type, updated_task_text, answer_key, answer_text
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        reflection_id, task_id, progress_rating, update_type, updated_task_text, answer_key, answer_text
    ), commit=True)


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


def reflection_exists(user_id, goal_id, week_number, session_id="a"):
    result = execute_query("""
        SELECT 1 FROM reflections
        WHERE user_id = %s AND goal_id = %s AND week_number = %s AND session_id = %s AND completed = TRUE
    """, (user_id, goal_id, week_number, session_id), fetch="one")
    return result is not None

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
    query = """
    WITH new_task AS (
        INSERT INTO tasks (goal_id, task_text)
        VALUES (%s, %s)
        RETURNING id
    )
    UPDATE tasks
    SET status = 'archived',
        replaced_by_task_id = (SELECT id FROM new_task),
        replacement_reason = %s
    WHERE id = %s
    RETURNING (SELECT id FROM new_task) AS new_task_id;
    """
    result = execute_query(
        query,
        (goal_id, new_task_text, reason, old_task_id),
        fetch="one",
        commit=True
    )
    return result["new_task_id"] if result else None

def save_reflection_draft(user_id, goal_id, week_number, session_id, step, task_progress, answers, update_idx, q_idx, awaiting_task_edit=None, editing_choice=None):
    execute_query("""
        INSERT INTO reflection_drafts (
            user_id, goal_id, week_number, session_id,
            task_progress, reflection_answers,
            reflection_step, update_task_idx, reflection_q_idx,
            awaiting_task_edit, editing_choice,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (user_id, goal_id, week_number, session_id)
        DO UPDATE SET
            task_progress = EXCLUDED.task_progress,
            reflection_answers = EXCLUDED.reflection_answers,
            reflection_step = EXCLUDED.reflection_step,
            update_task_idx = EXCLUDED.update_task_idx,
            reflection_q_idx = EXCLUDED.reflection_q_idx,
            awaiting_task_edit = EXCLUDED.awaiting_task_edit,
            editing_choice = EXCLUDED.editing_choice,
            updated_at = NOW()
    """, (
        user_id, goal_id, week_number, session_id,
        json.dumps(task_progress), json.dumps(answers),
        step, update_idx, q_idx,
        awaiting_task_edit, editing_choice
    ), commit=True)

def load_reflection_draft(user_id, goal_id, week_number, session_id):
    return execute_query("""
        SELECT * FROM reflection_drafts
        WHERE user_id = %s AND goal_id = %s AND week_number = %s AND session_id = %s
    """, (user_id, goal_id, week_number, session_id), fetch="one")


def delete_reflection_draft(user_id, goal_id, week_number, session_id):
    execute_query("""
        DELETE FROM reflection_drafts
        WHERE user_id = %s AND goal_id = %s AND week_number = %s AND session_id = %s
    """, (user_id, goal_id, week_number, session_id), commit=True)

def get_last_reflection_meta(user_id, goal_id):
    """
    Return the most‐recent reflection’s id and week_number 
    (so we can count its responses), or None.
    """
    return execute_query(
        """
        SELECT id, week_number
          FROM reflections
         WHERE user_id = %s
           AND goal_id = %s
         ORDER BY id DESC
         LIMIT 1
        """,
        (user_id, goal_id),
        fetch="one",
    )


def get_reflection_responses(reflection_id):
    """
    Return all the progress_rating rows for one reflection.
    """
    return execute_query(
        """
        SELECT task_id, progress_rating
          FROM reflection_responses
         WHERE reflection_id = %s
        """,
        (reflection_id,),
        fetch="all",
    )

def get_session_state(user_id):
    row = execute_query(
       "SELECT session_state FROM user_sessions WHERE user_id = %s",
       (user_id,),
       fetch="one"
    )
    return row["session_state"] if row else {}

def save_session_state(user_id, state_dict):
    js = json.dumps(state_dict)
    execute_query("""
        INSERT INTO user_sessions(user_id, session_state)
             VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE
          SET session_state = EXCLUDED.session_state,
              updated_at    = NOW()
    """, (user_id, js), commit=True)


# PHASES
# 0 = registered but not done onboarding
# 1 = training done
# 2 = initial goal and task entered (onboarding done)
# 3 = first reflection done
# 4 = second reflection done