from datetime import datetime
from db import save_message_to_db

class ChatThread(list):
    def __init__(self, user_id, *entries):
        super().__init__()
        self.user_id = user_id
        for e in entries:
            self.append(e)

    def append(self, entry):
        # 1️⃣ Pick the DB‐side sender value
        db_sender = "bot" if entry["sender"] == "Assistant" else "user"

        # 2️⃣ Generate one timestamp for both DB & UI
        ts = datetime.now().isoformat()

        # 3️⃣ Persist into the database with the mapped sender
        save_message_to_db(
            self.user_id,
            db_sender,
            entry["message"],
            ts
        )

        # 4️⃣ Store in-memory for UI (with the original label)
        super().append({
            "sender":    entry["sender"],
            "message":   entry["message"],
            "timestamp": ts
        })
