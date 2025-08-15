# api.py

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from db import execute_query

class StatusUpdate(BaseModel):
    prolific_id: str
    stage: str  # "presurvey" or "postsurvey"

app = FastAPI()

def update_flag(prolific_id: str, stage: str) -> bool:
    """
    - For 'presurvey': mark presurvey complete AND set Day-0 (onboarding_completed_at) once.
      Uses COALESCE to avoid overwriting if it was already set.
    - For 'postsurvey': mark postsurvey complete.
    """
    if stage == "presurvey":
        sql = """
        UPDATE users
           SET has_completed_presurvey = TRUE,
               onboarding_completed_at = COALESCE(onboarding_completed_at, NOW())
         WHERE prolific_code = %s
        """
        params = (prolific_id,)
    elif stage == "postsurvey":
        sql = """
        UPDATE users
           SET has_completed_postsurvey = TRUE
         WHERE prolific_code = %s
        """
        params = (prolific_id,)
    else:
        return False

    try:
        execute_query(sql, params, fetch=None, commit=True)
        return True
    except Exception:
        return False

@app.post("/api/update_status")
async def update_status(data: StatusUpdate):
    success = update_flag(data.prolific_id, data.stage)
    return {"success": success}

@app.get("/api/update_status")
async def update_status_get(prolific_id: str, stage: str):
    success = update_flag(prolific_id, stage)
    return {"success": success}


@app.get("/api/get_goal_and_tasks")
async def get_goal_and_tasks(prolific_id: str):
    user_row = execute_query(
        "SELECT user_id FROM users WHERE prolific_code = %s",
        (prolific_id,),
        fetch="one"
    )
    if not user_row:
        return JSONResponse(content={"success": False, "error": "User not found"}, status_code=404)

    user_id = user_row["user_id"]

    goal_row = execute_query(
        "SELECT id, goal_text FROM goals WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1",
        (user_id,),
        fetch="one"
    )
    if not goal_row:
        return JSONResponse(content={"success": False, "error": "Goal not found"}, status_code=404)

    goal_id = goal_row["id"]
    goal_text = goal_row["goal_text"]

    tasks = execute_query(
        "SELECT task_text, completed FROM tasks WHERE goal_id = %s AND status = 'active'",
        (goal_id,),
        fetch="all"
    )

    return {
        "success": True,
        "goal": goal_text,
        "tasks": [{"task_text": t["task_text"], "completed": t["completed"]} for t in tasks],
    }