# db_utils.py
import streamlit as st
import pandas as pd
from db import conn, save_session_state  # This brings in your existing global connection


# At the top of goal_flow.py (or in a shared utils module)
def build_goal_tasks_text(goal, tasks):
    """
    Build a clean text blob for download.
    """
    lines = [
        "Your SMART Goal:",
        goal,
        "",
        "Weekly Tasks:"
    ]
    for t in tasks:
        lines.append(f"- {t}")
    return "\n".join(lines)

def set_state(**kwargs):
    for k, v in kwargs.items():
        st.session_state[k] = v
    
    dynamic_flags = [k for k in st.session_state.keys()
                     if k.startswith(("ask_", "justifying_", "justified_"))]
    
    keys_to_save = [
        "needs_restore",
        
        # routing
        "chat_state",
        "group",

        # SMART‑training
        "smart_step",
        "message_index",

        # Goal‑setting
        "goal_step",
        "current_goal",

        # Task‑entry
        "goal_id_being_worked",
        "task_entry_stage",
        "candidate_task",

        "tasks_saved","force_task_handled",

        # Reflection
        "week",
        "session",
        "reflection_step",
        "task_progress",
        "reflection_answers",
        "update_task_idx",
        "reflection_q_idx",
        "awaiting_task_edit",
        "editing_choice",
    ] + dynamic_flags
    
    # also save the “view goals” trigger if set
    if "trigger_view_goals" in st.session_state:
        keys_to_save.append("trigger_view_goals")

    to_save = {k: st.session_state.get(k) for k in keys_to_save}
    save_session_state(st.session_state["user_id"], to_save)


def export_chat_history(user_id, format="csv"):
    query = "SELECT * FROM chat_history WHERE user_id = %s"
    df = pd.read_sql_query(query, conn, params=(user_id,))

    if format == "csv":
        df.to_csv(f"chat_history_{user_id}.csv", index=False)
    elif format == "json":
        df.to_json(f"chat_history_{user_id}.json", orient="records", indent=2)
    else:
        raise ValueError("Unsupported format. Use 'csv' or 'json'.")

def export_goals_tasks(user_id, format="csv"):
    goals_query = "SELECT * FROM goals WHERE user_id = %s"
    tasks_query = """
        SELECT tasks.* 
        FROM tasks 
        JOIN goals ON tasks.goal_id = goals.id 
        WHERE goals.user_id = %s
    """

    goals_df = pd.read_sql_query(goals_query, conn, params=(user_id,))
    tasks_df = pd.read_sql_query(tasks_query, conn, params=(user_id,))

    if format == "csv":
        goals_df.to_csv(f"goals_{user_id}.csv", index=False)
        tasks_df.to_csv(f"tasks_{user_id}.csv", index=False)
    elif format == "json":
        goals_df.to_json(f"goals_{user_id}.json", orient="records", indent=2)
        tasks_df.to_json(f"tasks_{user_id}.json", orient="records", indent=2)
    else:
        raise ValueError("Unsupported format. Use 'csv' or 'json'.")

def export_reflections(user_id, format="csv"):
    query = "SELECT * FROM reflections WHERE user_id = %s"
    df = pd.read_sql_query(query, conn, params=(user_id,))

    if format == "csv":
        df.to_csv(f"reflections_{user_id}.csv", index=False)
    elif format == "json":
        df.to_json(f"reflections_{user_id}.json", orient="records", indent=2)
    else:
        raise ValueError("Unsupported format. Use 'csv' or 'json'.")