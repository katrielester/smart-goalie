# chat_thread.py

from datetime import datetime
from db import save_message_to_db
import streamlit as st

class ChatThread(list):
    def __init__(self, user_id, *entries):
        super().__init__()
        self.user_id = user_id
        for e in entries:
            self.append(e)

    def append(self, entry):
        # Pick the DB‐side sender value
        db_sender = "bot" if entry["sender"] == "Assistant" else "user"

        # Generate one timestamp for both DB & UI
        ts = datetime.now().isoformat()

        skip_literals = {
            "🔎 Analyzing your goal…", 
            "✍️ Typing...", 
            "Thinking of task suggestions for you… ✍️"
        }

        skip_substrings = [
            "You've already submitted a reflection"
        ]

        msg = entry["message"].strip()

        should_skip = (
            msg in skip_literals
            or any(sub in msg for sub in skip_substrings)
        )

        if not should_skip:
            # Persist into the database with the mapped sender
            save_message_to_db(
                self.user_id,
                db_sender,
                entry["message"],
                ts,
                phase=st.session_state["chat_state"]  
                )

        # Store in-memory for UI (with the original label)
        super().append({
            "sender":    entry["sender"],
            "message":   entry["message"],
            "timestamp": ts
        })

    def extend(self, entries):
        for e in entries:
            self.append(e)

    def __iadd__(self, entries):
        self.extend(entries)
        return self