# api.py

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from db import execute_query

PROLIFIC_API_TOKEN = os.environ.get("PROLIFIC_API_TOKEN")
PROLIFIC_API_BASE  = os.environ.get("PROLIFIC_API_BASE", "https://api.prolific.com")  # keep overridable
GROUP_CONTROL_ID   = os.environ.get("PROLIFIC_GROUP_CONTROL_ID")
GROUP_TREATMENT_ID = os.environ.get("PROLIFIC_GROUP_TREATMENT_ID")
PROLIFIC_DRY_RUN = False

class StatusUpdate(BaseModel):
    prolific_id: str          # Prolific PID from Qualtrics
    stage: str                # "presurvey" or "postsurvey"
    group: str | None = None  # "0" or "1" (only needed on presurvey)

app = FastAPI()

def _add_to_prolific_group(prolific_pid: str, group_code: str) -> tuple[bool, str | None]:
    """
    Append a participant to the correct Prolific Participant Group.
    Idempotent: if already present, treat as success.
    """
    if not PROLIFIC_API_TOKEN:
        return False, "Missing PROLIFIC_API_TOKEN"

    group_id = GROUP_TREATMENT_ID if str(group_code).strip() == "1" else GROUP_CONTROL_ID
    if not group_id:
        return False, "Missing group id env var"

    # Example membership endpoint path (check Prolific API docs in your workspace):
    # POST {PROLIFIC_API_BASE}/api/v1/participant-groups/{group_id}/members
    # Body: { "participant_ids": ["<PID>"] }

    url = f"{PROLIFIC_API_BASE}/api/v1/participant-groups/{group_id}/members"
    headers = {
        "Authorization": f"Bearer {PROLIFIC_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"participant_ids": [prolific_pid]}


    if PROLIFIC_DRY_RUN:
        return True, "dry_run"
    else:
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=20)
            # Treat 200/201/204 as success; if API returns 409 for “already in group”, also consider success.
            if r.status_code in (200, 201, 202, 204):
                return True, None
            if r.status_code == 409:
                return True, "Already in group"
            return False, f"Prolific API {r.status_code}: {r.text}"
        except Exception as e:
            return False, str(e)

def update_flag(prolific_id: str, stage: str, group: str | None = None) -> dict:
    """
    - 'presurvey': mark presurvey complete, set Day-0 once, and (optionally) add to Prolific group.
    - 'postsurvey': mark postsurvey complete.
    Returns dict: {"db_ok": bool, "group_ok": bool, "group_msg": str|None}
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
        sql = "UPDATE users SET has_completed_postsurvey = TRUE WHERE prolific_code = %s"
        params = (prolific_id,)
    else:
        return {"db_ok": False, "group_ok": False, "group_msg": "invalid stage"}

    db_ok = True
    try:
        execute_query(sql, params, fetch=None, commit=True)
    except Exception:
        db_ok = False

    group_ok, group_msg = True, None
    if stage == "presurvey" and group is not None:
        group_ok, group_msg = _add_to_prolific_group(prolific_id, group)

    return {"db_ok": db_ok, "group_ok": group_ok, "group_msg": group_msg}

@app.post("/api/update_status")
async def update_status(data: StatusUpdate):
    result = update_flag(data.prolific_id, data.stage, data.group)
    return result

@app.get("/api/update_status")
async def update_status_get(prolific_id: str, stage: str, group: str | None = None):
    result = update_flag(prolific_id, stage, group)
    return result

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