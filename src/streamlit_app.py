#streamlit_app.py

import streamlit as st
import time
from datetime import datetime
from db import (
    create_user, user_completed_training, mark_training_completed,
    save_message_to_db, get_chat_history,
    save_goal, save_task, save_reflection,
    get_tasks, get_goals, get_reflections, user_goals_exist,
)
from llama_utils import (
    refine_goal, suggest_specific_fix, suggest_measurable_fix,
    suggest_achievable_fix, suggest_relevant_fix, suggest_timebound_fix,
    summarize_reflection,
)
from reflection_flow import run_weekly_reflection
from phases import smart_training_flow, weekly_reflection_prompts, goal_setting_flow
from prompts import system_prompt_goal_refiner, system_prompt_reflection_summary
from logger import setup_logger

logger = setup_logger()

st.set_page_config(page_title="SMART Goal Chatbot", layout="centered")

st.session_state.setdefault("chat_state", "intro")
st.session_state.setdefault("user_id", "")
st.session_state.setdefault("chat_thread", [])
st.session_state.setdefault("smart_step", "intro")
st.session_state.setdefault("message_index", 0)
st.session_state.setdefault("current_goal", "")

# Dynamic chat height
if st.session_state["chat_state"] in ["menu", "view_goals"]:
    chat_height = "45vh"  # tighter chat when UI is crowded
else:
    chat_height = "60vh"  # default height

query_params = st.query_params
group_code = query_params.get("g", ["2"])[0]  # Default to "2" (control)

group_assignment = "treatment" if group_code == "1" else "control"
st.session_state["group"] = group_assignment

with st.sidebar:
    if st.button("Dev: Jump to Goal Setting"):
        st.session_state["chat_state"] = "goal_setting"
        st.session_state["smart_step"] = "initial_goal"
        st.session_state["message_index"] = 0
        st.rerun()

with st.sidebar:
    st.title("User Panel")
    user_id = st.text_input("Enter your Prolific ID")
    if st.button("Authenticate"):
        if user_id:
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user_id
            create_user(user_id, prolific_code=user_id, group=group_assignment)

            if user_completed_training(user_id):
                st.session_state["chat_thread"] = [{
                    "sender": "Assistant",
                    "message": "Welcome back! What would you like to do today?"
                }]
                st.session_state["chat_state"] = "menu"
            else:
                st.session_state["chat_thread"] = [{
                    "sender": "Assistant",
                    "message": "Hi! I'm Goalie. Are you ready to learn about SMART goals?"
                }]
                st.session_state["chat_state"] = "intro"

            st.success(f"Welcome!")
            st.rerun()
        else:
            st.error("Please provide your Prolific ID.")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Please authenticate first.")
    st.stop()

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .chat-container { height: {chat_height}; overflow-y: auto; padding: 10px; border-radius: 10px; }
    .chat-left { text-align: left; background-color: #e0e0e0; color: #000000; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 70%; display: block; }
    .chat-right { text-align: right; background-color: #007BFF; color: #ffffff; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 70%; margin-left: auto; display: block; }
    </style>
""", unsafe_allow_html=True)

st.title("SMART Goals with Goalie")

with st.container():
    chat_html = '<div id="chat" class="chat-container">'
    for entry in st.session_state["chat_thread"]:
        style = "chat-left" if entry["sender"] == "Assistant" else "chat-right"
        chat_html += f'<div class="{style}">{entry["message"]}</div>'
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    st.markdown("""
        <script>
        const scrollToBottom = () => {
            const container = document.getElementById("chat");
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }

        new MutationObserver(scrollToBottom).observe(
            document.getElementById("chat"),
            { childList: true, subtree: true }
        );

        window.addEventListener("load", scrollToBottom);
        </script>
    """, unsafe_allow_html=True)

from goal_flow import run_goal_setting

def run_intro():
    intro_message = "Hi! I'm Goalie. Are you ready to learn about SMART goals?"
    if not any(entry["message"] == intro_message for entry in st.session_state["chat_thread"]):
        st.session_state["chat_thread"].append({"sender": "Assistant", "message": intro_message})
    if st.button("Yes, let's start", key="start_training_btn"):
        if not any(entry["message"] == "Yes, let's start" for entry in st.session_state["chat_thread"]):
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

    # Step 1: Show assistant messages one-by-one
    if not all_texts_rendered:
        rendered_messages = [entry["message"] for entry in st.session_state["chat_thread"] if entry["sender"] == "Assistant"]
        current_text = texts[current_index]
        current_text = current_text.replace("{user_name}", st.session_state.get("user_name", ""))
        current_text = current_text.replace("{full_goal}", st.session_state.get("full_goal", ""))

        if current_text not in rendered_messages:
            st.session_state["chat_thread"].append({"sender": "Assistant", "message": current_text})

        # Always advance index after rendering
        st.session_state["message_index"] += 1
        time.sleep(0.7)
        st.rerun()

    # Step 2: Handle buttons or input after all messages are rendered
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

        elif step.get("input_type") == "text":
            user_input = st.chat_input("Type your answer")
            if user_input:
                st.session_state["chat_thread"].append({"sender": "User", "message": user_input})

                # Handle relevance explanation path
                if st.session_state["smart_step"] in ["relevant_prompt", "relevant_explain_anyway"]:
                    base_goal = "I would like to work out three times a week, at least 30 minutes each time"
                    relevance_reason = user_input.strip()

                    if not relevance_reason.lower().startswith("to "):
                        relevance_reason = "to " + relevance_reason

                    full_goal = f"{base_goal}, {relevance_reason}."
                    st.session_state["full_goal"] = full_goal
                    st.session_state["smart_step"] = "relevant_echo"
                    st.session_state["message_index"] = 0
                    st.rerun()

                # Generic case for all other steps
                else:
                    if st.session_state["smart_step"] == "get_name":
                        st.session_state["user_name"] = user_input

                    st.session_state["smart_step"] = step["next"]
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
        if st.button("✅ View Existing Goals"):
            st.session_state["chat_state"] = "view_goals"
            st.rerun()
    if st.session_state.get("group") == "treatment" and user_goals_exist(st.session_state["user_id"]):
        if st.button("✏️ Weekly Reflection"):
            st.session_state["chat_state"] = "reflection"
            st.rerun()

# def run_reflection():
#     st.subheader("Weekly Check-In")
#     responses = []
#     for q in weekly_reflection_prompts:
#         ans = st.text_area(q, key=q)
#         responses.append(f"{q}\n{ans}\n")
#     if st.button("Submit Reflection"):
#         full_reflection = "\n".join(responses)
#         save_reflection(st.session_state["user_id"], None, full_reflection, week_number=1)
#         with st.spinner("Summarizing your progress..."):
#             summary = summarize_reflection(full_reflection)
#         st.session_state["chat_thread"].append({"sender": "User", "message": full_reflection})
#         st.session_state["chat_thread"].append({"sender": "Assistant", "message": summary})
#         st.success("Reflection submitted!")

def run_view_goals():
    st.subheader("Your SMART Goals")

    goals = get_goals(st.session_state["user_id"])

    if not goals:
        st.info("You haven’t created any goals yet.")
    else:
        for goal_id, goal_text in goals:
            st.markdown(f"**Goal:** {goal_text}")
            tasks = get_tasks(goal_id)
            if tasks:
                for task_id, task_text, completed in tasks:
                    status = "✅" if completed else "⬜️"
                    st.markdown(f"- {status} {task_text}")
            else:
                st.markdown("_No subtasks yet._")
            st.markdown("---")

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