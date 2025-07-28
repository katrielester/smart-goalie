import os
import sys
# allow importing from your src folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI
from pydantic import BaseModel
from db import execute_query

class StatusUpdate(BaseModel):
    prolific_id: str
    stage: str  # "presurvey" or "postsurvey"

app = FastAPI()

def update_flag(prolific_id: str, stage: str) -> bool:
    if stage == "presurvey":
        sql = "UPDATE users SET has_completed_presurvey = TRUE WHERE prolific_code = %s"
    elif stage == "postsurvey":
        sql = "UPDATE users SET has_completed_postsurvey = TRUE WHERE prolific_code = %s"
    else:
        return False

    # tell execute_query not to fetch anything
    try:
        execute_query(sql, (prolific_id,), fetch=None, commit=True)
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
