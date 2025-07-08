# db_utils.py

import pandas as pd
from db import conn  # This brings in your existing global connection

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