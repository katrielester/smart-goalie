# STREAMLIT EXPERIMENT
import streamlit as st
import time
from datetime import datetime
from db import (
    create_user, user_completed_training, mark_training_completed,
    save_message_to_db, get_chat_history, get_user_info,
    save_goal, save_task, save_reflection,
    get_tasks, get_goals, get_reflections, user_goals_exist,
)
from reflection_flow import run_weekly_reflection
from goal_flow import run_goal_setting
from phases import smart_training_flow
from prompts import system_prompt_goal_refiner, system_prompt_reflection_summary
from logger import setup_logger
import os

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
logger = setup_logger()

st.set_page_config(page_title="SMART Goal Chatbot", layout="centered")

st.session_state.setdefault("chat_state", "intro")
st.session_state.setdefault("user_id", "")
st.session_state.setdefault("chat_thread", [])
st.session_state.setdefault("smart_step", "intro")
st.session_state.setdefault("message_index", 0)
st.session_state.setdefault("current_goal", "")

with st.sidebar:
    st.title("User Panel")

    query_params = st.query_params
    prolific_id = query_params.get("PROLIFIC_PID")

    if prolific_id:
        user_id = prolific_id
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = user_id
        st.info(f"Authenticated as Prolific ID: {user_id}")
    elif DEV_MODE:
        user_id = st.text_input("Enter your Prolific ID")
        if not st.session_state.get("authenticated"):
            if st.button("Authenticate (DEV only)") and user_id:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user_id
                st.rerun()
        else:
            st.info(f"Manually authenticated as {st.session_state['user_id']}")
    else:
        st.warning("Please access this link via Prolific.")
        st.stop()

    if st.session_state.get("authenticated"):
        user_info = get_user_info(user_id)

        if user_info:
            prolific_code, has_completed_training, db_group = user_info
            st.session_state["group"] = db_group.strip().lower()
        else:
            group_param = st.query_params.get("g", ["2"])[0]
            group_assignment = group_param
            create_user(user_id, prolific_code=user_id, group=group_assignment)
            st.session_state["group"] = "treatment" if group_param == "1" else "control"

        if "chat_state" not in st.session_state or st.session_state["chat_state"] not in [
            "smart_training", "goal_setting", "menu", "reflection", "view_goals"
        ]:
            if user_completed_training(user_id):
                if not st.session_state["chat_thread"]:
                    st.session_state["chat_thread"].append({
                        "sender": "Assistant",
                        "message": "Welcome back! What would you like to do today?"
                    })
                st.session_state["chat_state"] = "menu"
            else:
                st.session_state["chat_state"] = "intro"

        if st.session_state["group"] == "treatment":
            if "week" in st.query_params and "session" in st.query_params:
                st.session_state["chat_state"] = "reflection"

        if "did_rerun_auth" not in st.session_state:
            st.session_state["did_rerun_auth"] = True
            st.rerun()

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Please authenticate first.")
    st.stop()

st.title("SMART Goalie")

# Render messages with st.chat_message
for entry in st.session_state["chat_thread"]:
    with st.chat_message("assistant" if entry["sender"] == "Assistant" else "user"):
        st.markdown(entry["message"])

st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)

def run_intro():
    intro_message = "Hi! I'm Goalie. Are you ready to learn about SMART goals!"
    if "did_intro_rerun" not in st.session_state or not st.session_state["did_intro_rerun"]:
        if not any(entry["message"] == intro_message for entry in st.session_state["chat_thread"]):
            st.session_state["chat_thread"].append({"sender": "Assistant", "message": intro_message})
            st.session_state["did_intro_rerun"] = True
            st.rerun()
    if st.session_state.get("chat_state") == "intro":
        if st.button("Yes, let's start", key="start_training_btn"):
            st.session_state["chat_thread"].append({"sender": "User", "message": "Yes, let's start"})
            st.session_state["chat_state"] = "smart_training"
            st.session_state["smart_step"] = "intro"
            st.session_state["message_index"] = 0
            st.rerun()

def run_smart_training():
    step = smart_training_flow[st.session_state["smart_step"]]
    texts = step["text"]
    if isinstance(texts, str):
        texts = [texts]

    current_index = st.session_state.get("message_index", 0)
    all_texts_rendered = current_index >= len(texts)

    if not all_texts_rendered:
        rendered_messages = [entry["message"] for entry in st.session_state["chat_thread"] if entry["sender"] == "Assistant"]
        current_text = texts[current_index]
        current_text = current_text.replace("{user_name}", st.session_state.get("user_name", ""))
        current_text = current_text.replace("{full_goal}", st.session_state.get("full_goal", ""))

        if current_text not in rendered_messages:
            st.session_state["chat_thread"].append({"sender": "Assistant", "message": current_text})

        st.session_state["message_index"] += 1
        # time.sleep(0.5)
        st.rerun()

    else:
        if step.get("buttons"):
            selected = None
            cols = st.columns(len(step["buttons"]))
            for idx, btn in enumerate(step["buttons"]):
                if cols[idx].button(btn, key=f"btn_{btn}"):
                    selected = btn
                    break
            if selected:
                st.session_state["chat_thread"].append({"sender": "User", "message": selected})
                st.session_state["smart_step"] = step["next"][selected]
                st.session_state["message_index"] = 0
                st.rerun()

        elif step.get("complete"):
            mark_training_completed(st.session_state["user_id"])
            st.session_state["chat_state"] = "goal_setting"
            st.session_state["smart_step"] = "initial_goal"
            st.session_state["message_index"] = 0
            st.rerun()

def run_menu():
    if st.button("➕ Create a New Goal"):
        st.session_state["chat_state"] = "goal_setting"
        st.session_state["smart_step"] = "initial_goal"
        st.session_state["message_index"] = 0
        st.rerun()
    if user_goals_exist(st.session_state["user_id"]):
        if st.button("✅ View Existing Goal and Tasks"):
            st.session_state["chat_state"] = "view_goals"
            st.rerun()
    if st.session_state.get("group") == "treatment" and user_goals_exist(st.session_state["user_id"]):
        if st.button("✏️ Weekly Reflection"):
            st.session_state["chat_state"] = "reflection"
            st.rerun()

def run_view_goals():
    if st.button("Back to Menu"):
        st.session_state["chat_state"] = "menu"
        st.rerun()

if st.session_state["chat_state"] == "intro":
    run_intro()
elif st.session_state["chat_state"] == "smart_training":
    run_smart_training()
elif st.session_state["chat_state"] == "menu":
    run_menu()
elif st.session_state["chat_state"] == "goal_setting":
    run_goal_setting()
elif st.session_state["chat_state"] == "reflection":
    run_weekly_reflection()
elif st.session_state["chat_state"] == "view_goals":
    run_view_goals()