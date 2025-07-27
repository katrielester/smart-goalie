# chat_thread.py

from datetime import datetime
from db import save_message_to_db

class ChatThread(list):
    def __init__(self, user_id, *entries):
        super().__init__()
        self.user_id = user_id
        for e in entries:
            self.append(e)

    # def append(self, entry):
        
    #     # 1️⃣ Generate one timestamp for both DB & UI
    #     ts = datetime.now().isoformat()
    #     # 2️⃣ Persist into the database, using that same timestamp
    #     save_message_to_db(
    #         self.user_id,
    #         entry["sender"],
    #         entry["message"],
    #         ts
    #     )
    #     # 3️⃣ Store in-memory (so your UI sees it)
    #     super().append({
    #         "sender":    entry["sender"],
    #         "message":   entry["message"],
    #         "timestamp": ts
    #     })

    def append(self, entry):
        ts = datetime.now().isoformat()
        print(f" 🔔 ChatThread.append called: {entry!r} @ {ts}")
        save_message_to_db(self.user_id, entry["sender"], entry["message"], ts)
        super().append({**entry, "timestamp": ts})