#streamlit_app.py

import streamlit as st
import time
from datetime import datetime
from db import (
    create_user, user_completed_training, mark_training_completed,
    save_message_to_db, get_chat_history, get_user_info,
    save_goal, save_task, save_reflection,
    get_tasks, get_goals, user_goals_exist,
    get_goals_with_task_counts, get_last_reflection_meta, get_reflection_responses
)
from reflection_flow import run_weekly_reflection
from goal_flow import run_goal_setting, run_add_tasks
from phases import smart_training_flow
from prompts import system_prompt_goal_refiner, system_prompt_reflection_summary
from logger import setup_logger

import os


DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

logger = setup_logger()

st.set_page_config(page_title="SMART Goal Chatbot", layout="centered")

st.markdown("""
    <style>
    button {
        background-color: #1f77b4;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        margin-bottom: 0.5rem;
        text-align: left;
        width: 100%;
    }
    button:hover {
        background-color: #145a86;
    }
    </style>
""", unsafe_allow_html=True)

# st.session_state.setdefault("chat_state", "intro")
# st.session_state.setdefault("user_id", "")
# st.session_state.setdefault("chat_thread", [])
# st.session_state.setdefault("smart_step", "intro")
# st.session_state.setdefault("message_index", 0)
# st.session_state.setdefault("current_goal", "")

# Dynamic chat height
if "chat_state" in st.session_state:
    if st.session_state["chat_state"] in ["menu", "view_goals"]:
        chat_height = "45vh"
    else:
        chat_height = "60vh"
else:
    chat_height = "60vh"  # fallback if not initialized yet

if "did_auth_init" not in st.session_state:
    st.session_state["did_auth_init"] = False

with st.sidebar:
    if DEV_MODE:
        if st.button("Dev: Jump to Goal Setting"):
            st.session_state["chat_state"] = "goal_setting"
            st.session_state["message_index"] = 0
            st.rerun()

        if st.button("Dev: Jump to Reflection"):
            st.session_state["chat_state"] = "reflection"
            st.session_state["week"] = 1
            st.session_state["session"] = "a"
            st.rerun()

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


if st.session_state.get("authenticated") and "chat_state" not in st.session_state:
    query_params = st.query_params.to_dict()
    week = query_params.get("week")
    session = query_params.get("session")
    print("Init Debug — Week:", week, "| Session:", session)

    user_id = st.session_state["user_id"]

    # Check if user exists in DB
    user_info = get_user_info(user_id)
    if not user_info:
        group = query_params.get("g", ["2"])[0]
        create_user(user_id, prolific_code=user_id, group=group)
        st.session_state["group"] = "treatment" if group == "1" else "control"
    else:
        group = user_info["group_assignment"]
        st.session_state["group"] = "treatment" if str(group).strip() == "1" else "control"
        st.write(st.session_state.get("group"),group)

    # Routing logic
    print("Week:", week)
    print("Session:", session)
    print("Group (from DB or URL):", st.session_state["group"], group)

    if st.session_state["group"] == "treatment" and week and session:
        st.session_state["week"] = int(week)
        st.session_state["session"] = session
        st.session_state["chat_state"] = "reflection"
    elif user_completed_training(user_id):
        st.session_state["chat_state"] = "menu"
    else:
        st.session_state["chat_state"] = "intro"

    # Common session vars
    st.session_state["chat_thread"] = []
    st.session_state["smart_step"] = "intro"
    st.session_state["message_index"] = 0
    st.session_state["current_goal"] = ""
    st.session_state["force_task_handled"] = False

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Please authenticate first.")
    st.stop()

#  FORCE TASK ENTRY IF GOAL EXISTS BUT NO TASK

# Only run force-task logic once per session unless reset
if "force_task_handled" not in st.session_state:
    st.session_state["force_task_handled"] = False

goals = get_goals_with_task_counts(st.session_state["user_id"])

# Only trigger if there ARE goals and one of them has zero tasks
if (
    st.session_state["chat_state"] not in ["reflection", "smart_training", "goal_setting"] 
    and goals 
    and not st.session_state.get("force_task_handled", False)):
    goal_with_no_active_tasks = next((g for g in goals if g["task_count"] == 0), None)

    if goal_with_no_active_tasks:
        # Prevent infinite rerun loop BEFORE rerun
        st.session_state["force_task_handled"] = True

        st.session_state["goal_id_being_worked"] = goal_with_no_active_tasks["id"]
        st.session_state["current_goal"] = goal_with_no_active_tasks["goal_text"]
        st.session_state["tasks_saved"] = []
        st.session_state["task_entry_stage"] = "suggest"
        st.session_state["chat_state"] = "add_tasks"
        st.session_state["chat_thread"] = [{
            "sender": "Assistant",
            "message": (
                "Welcome back! It looks like you've set a goal but haven't added any weekly tasks yet:<br><br>"
                f"<b>{goal_with_no_active_tasks['goal_text']}</b><br><br>"
                "Let's start by adding your first task to help you move forward this week."
            )
        }]

        st.rerun()

add_tasks_goal_id = st.query_params.get("add_tasks_for_goal")

if add_tasks_goal_id:
    try:
        goal_id = int(add_tasks_goal_id)
        goal_list = get_goals(st.session_state["user_id"])
        goal = next((g for g in goal_list if g["id"] == goal_id), None)
    except Exception:
        goal = None

    if goal:
        st.session_state["goal_id_being_worked"] = goal_id
        st.session_state["current_goal"] = goal["goal_text"]
        st.session_state["tasks_saved"] = []
        st.session_state["task_entry_stage"] = "suggest"
        st.session_state["chat_state"] = "add_tasks"

        # Only add message if not already in chat
        already_has_prompt = any("adding more tasks for your goal" in m["message"] for m in st.session_state["chat_thread"])
        if not already_has_prompt:
            st.session_state["chat_thread"] = [{
                "sender": "Assistant",
                "message": (
                    f"You're adding more tasks for your goal:<br><br><b>{goal['goal_text']}</b><br><br>"
                    "Let's break it down into small weekly steps."
                )
            }]
        st.rerun()

st.title("SMART Goalie")


import streamlit.components.v1 as components

# Use pixel height for consistent layout
chat_height_px = 400
# if st.session_state["chat_state"] not in ["menu", "view_goals"] else 400

# GOAL OVERVIEW INJECTION
# Inject goal HTML into chat thread if viewing goals
if st.session_state["chat_state"] == "view_goals":
    if not any(
        "Your SMART Goals:" in m["message"] or "You haven’t created any goals" in m["message"]
        for m in st.session_state["chat_thread"]
    ):
        user_id = str(st.session_state["user_id"])  # Ensure it's a string
        goals = get_goals(st.session_state["user_id"])
        if not goals:
            goal_html = "<div class='chat-left'>You haven’t created any goals yet.</div>"
        else:
            goal_html = "<div class='chat-left'><strong>Your SMART Goals:</strong><br>"
            for goal in goals:
                goal_id = goal["id"]
                goal_text = goal["goal_text"]
                goal_html += f"<strong>Goal:</strong> {goal_text}<br>"
                tasks = get_tasks(goal_id, active_only=True)
                if tasks:
                    for task in tasks:
                        task_id = task["id"]
                        task_text = task["task_text"]
                        completed = task["completed"]
                        status = "✅" if completed else "⬜️"
                        goal_html += f"{status} {task_text}<br>"
                else:
                    goal_html += "<em>No subtasks yet.</em><br>"
                # goal_html += "<hr>"
            goal_html += "</div>"

        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": goal_html
        })
        # now show “X of Y tasks done last week”
        meta = get_last_reflection_meta(user_id, goal_id)
        if meta:
            responses = get_reflection_responses(meta["id"])
            total_tasks = len(tasks)
            done = sum(1 for r in responses if r["progress_rating"] == 4)
            summary_html = (
                "<div class='chat-left'>"
                f"<b>Last Reflection (Week {meta['week_number']}):</b><br>"
                f"✅ You completed {done}/{total_tasks} tasks."
                "</div>"
            )
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": summary_html
            })

# STABLE VER
# chat_bubble_html = "".join([
#     f'<div class="{"chat-left" if m["sender"] == "Assistant" else "chat-right"}">{m["message"]}</div>'
#     for m in st.session_state["chat_thread"]
# ])

# EXPERIMENTAL START #
previous_len = st.session_state.get("last_rendered_index", 0)
current_len = len(st.session_state["chat_thread"])

# Mark which are new
chat_bubble_html = ""
for i, m in enumerate(st.session_state["chat_thread"]):
    css_class = "chat-left" if m["sender"] == "Assistant" else "chat-right"
    if i >= previous_len:
        # This is a new message – hide initially
        chat_bubble_html += f'<div class="{css_class} message" style="display: none;">{m["message"]}</div>'
    else:
        chat_bubble_html += f'<div class="{css_class}">{m["message"]}</div>'

# Save current length for next render
st.session_state["last_rendered_index"] = current_len

# EXPERIMENTAL END #


# Render chat container
with st.container():
    # STABLE VER START #
    # Static HTML
    # components.html(f"""
    #     <html>
    #     <head>
    #     <style>
    #         body {{
    #             font-family: "Segoe UI", sans-serif;
    #             margin: 0;
    #             padding: 0;
    #             background-color: #0e1117;
    #             color: #f0f0f0;
    #         }}

    #         .chat-wrapper {{
    #             height: {chat_height_px}px;
    #             overflow-y: auto;
    #             padding: 10px;
    #             border-radius: 10px;
    #             border: 1px solid #444;
    #             background-color: #1c1f26;
    #         }}

    #         .chat-left {{
    #             text-align: left;
    #             background-color: #2b2f38;
    #             color: #eaeaea;
    #             border-radius: 10px;
    #             padding: 10px;
    #             margin: 5px 0;
    #             max-width: 70%;
    #             display: block;
    #             word-wrap: break-word;
    #         }}

    #         .chat-right {{
    #             text-align: right;
    #             background-color: #005fcf;
    #             color: #ffffff;
    #             border-radius: 10px;
    #             padding: 10px;
    #             margin: 5px 0;
    #             max-width: 70%;
    #             margin-left: auto;
    #             display: block;
    #             word-wrap: break-word;
    #         }}
    #     </style>
    #     </head>
    #     <body>
    #         <div id="chatbox" class="chat-wrapper">
    #             {chat_bubble_html}
    #             <div id="endofchat" style="height: 30px;"></div>
    #         </div>
    #         <script>
    #             const chatBox = document.getElementById("chatbox");
    #             chatBox.scrollTop = chatBox.scrollHeight;
    #         </script>
    #     </body>
    #     </html>
    # """, height=chat_height_px, scrolling=False)
    # STABLE VER END #

    # EXPERIMENTAL VER START #
    components.html(f"""
    <html>
    <head>
    <style>
        body {{
            font-family: "Segoe UI", sans-serif;
            margin: 0;
            padding: 0;
            background-color: #0e1117;
            color: #f0f0f0;
        }}
        .chat-wrapper {{
            height: {chat_height_px}px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #444;
            background-color: #1c1f26;
        }}
        .chat-left {{
            text-align: left;
            background-color: #2b2f38;
            color: #eaeaea;
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            max-width: 70%;
            display: block;
            word-wrap: break-word;
        }}
        .chat-right {{
            text-align: right;
            background-color: #005fcf;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
            max-width: 70%;
            margin-left: auto;
            display: block;
            word-wrap: break-word;
        }}
    </style>
    </head>
    <body>
        <div id="chatbox" class="chat-wrapper">
            {chat_bubble_html}
            <div id="endofchat" style="height: 30px;"></div>
        </div>
        <script>
            const chatBox = document.getElementById("chatbox");
            const newMessages = document.querySelectorAll(".message");

            function revealMessages(i) {{
                if (i >= newMessages.length) return;
                newMessages[i].style.display = "block";
                chatBox.scrollTop = chatBox.scrollHeight;
                setTimeout(() => revealMessages(i + 1), 100);
            }}

            chatBox.scrollTop = chatBox.scrollHeight;
            revealMessages(0);
        </script>
    </body>
    </html>
    """, height=chat_height_px, scrolling=False)

    # EXPERIMENTAL VER END #


def run_intro():
    intro_message = "Hi! I'm Goalie. Are you ready to learn about SMART goals?"

    if "did_intro_rerun" not in st.session_state or not st.session_state["did_intro_rerun"]:
        if not any(entry["message"] == intro_message for entry in st.session_state["chat_thread"]):
            st.session_state["chat_thread"].append({"sender": "Assistant", "message": intro_message})
            st.session_state["did_intro_rerun"] = True
            st.rerun()

    if st.session_state.get("chat_state") == "intro":
        if st.button("Yes, let's start!", key="start_training_btn"):
            st.session_state["chat_thread"].append({"sender": "User", "message": "Yes, let's start!"})
            st.session_state["chat_state"] = "smart_training"
            st.session_state["smart_step"] = "intro"
            st.session_state["message_index"] = 0
            st.rerun()

def run_smart_training():
    print("🔵 In run_smart_training()")
    step = smart_training_flow[st.session_state["smart_step"]]
    if st.session_state["smart_step"] not in smart_training_flow:
        st.error(f"❌ Step '{st.session_state['smart_step']}' not found in smart_training_flow!")
        st.stop()
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
        elif step.get("complete"):
            if not(user_completed_training(st.session_state["user_id"])):
                mark_training_completed(st.session_state["user_id"])
            st.session_state["chat_state"] = "goal_setting"
            st.session_state["goal_step"] = "initial_goal"
            st.session_state["message_index"] = 0
            st.rerun()

def run_menu():
    if "chat_thread" not in st.session_state:
        st.session_state["chat_thread"] = []

    # Only show this prompt if it's not already the last message from Assistant
    if not st.session_state["chat_thread"] or (
        st.session_state["chat_thread"][-1]["sender"] == "Assistant" and
        "What would you like to do next?" not in st.session_state["chat_thread"][-1]["message"]
    ):
        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": "What would you like to do next? You can view your goal, review training, or create something new."
        })
        st.rerun()

    if not user_goals_exist(st.session_state["user_id"]):
        if st.button("➕ Create a New Goal"):
            st.session_state["chat_state"] = "goal_setting"
            st.session_state["goal_step"] = "initial_goal"
            st.session_state["message_index"] = 0
            st.rerun()
    else:
        if st.button("✅ View Existing Goal and Tasks"):
            st.session_state["chat_state"] = "view_goals"
            st.rerun()

    if user_completed_training(st.session_state["user_id"]):
        if st.button("📚 Review SMART Goal Training"):
            st.session_state["chat_state"] = "smart_training"
            st.session_state["smart_step"] = "intro"
            st.session_state["message_index"] = 0
            st.rerun()

            
    # if st.session_state.get("group") == "treatment" and user_goals_exist(st.session_state["user_id"]):
    #     if st.button("✏️ Weekly Reflection"):
    #         st.session_state["chat_state"] = "reflection"
    #         st.rerun()

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
    goals = get_goals_with_task_counts(st.session_state["user_id"])

    if goals:
        goal = goals[0] 
        task_count = goal["task_count"]
        goal_id = goal["id"]

        # Show the Add Task button only if task count <3
        if task_count < 3:
            if st.button("➕ Add Another Task"):
                st.session_state["goal_id_being_worked"] = goal_id
                st.session_state["current_goal"] = goal["goal_text"]
                st.session_state["tasks_saved"] = []
                st.session_state["task_entry_stage"] = "suggest"
                st.session_state["chat_state"] = "add_tasks"

                # Don't re-append this if coming from add_tasks_goal_id!
                st.session_state["chat_thread"] = [{
                    "sender": "Assistant",
                    "message": (
                        f"You're adding more tasks for your goal:<br><br><b>{goal['goal_text']}</b><br><br>"
                        "Let's break it down into small weekly steps."
                    )
                }]
                run_add_tasks()
                st.stop()
    if st.button("Back to Menu"):
        st.session_state["chat_state"] = "menu"
        st.rerun()

print("chat_state before routing:", st.session_state.get("chat_state"))
if "chat_state" not in st.session_state:
    st.stop()

state = st.session_state["chat_state"]

if state == "intro":
    run_intro()
elif state == "smart_training":
    run_smart_training()
elif state == "menu":
    run_menu()
elif state == "goal_setting":
    run_goal_setting()
elif state == "reflection":
    run_weekly_reflection()
elif state == "view_goals":
    run_view_goals()
elif state == "add_tasks":
    run_add_tasks()