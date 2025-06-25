#streamlit_app.py

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

if "authenticated" not in st.session_state:
    query_params = st.query_params
    group_code = query_params.get("g", ["2"])[0]  # Default to "2"
    group_assignment = "treatment" if group_code == "1" else "control"
    st.session_state["group"] = group_assignment

with st.sidebar:
    if DEV_MODE:
        if st.button("Dev: Jump to Goal Setting"):
            st.session_state["chat_state"] = "goal_setting"
            st.session_state["message_index"] = 0
            st.rerun()

        if st.button("Dev: Jump to Reflection"):
            st.session_state["chat_state"] = "reflection"
            st.rerun()

# with st.sidebar:
#     st.title("User Panel")
#     user_id = st.text_input("Enter your Prolific ID")
    
#     if st.button("Authenticate"):
#         if user_id:
#             st.session_state["authenticated"] = True
#             st.session_state["user_id"] = user_id

#             user_info = get_user_info(user_id)

#             if user_info:
#                 print("🔍 Raw user_info from DB:", user_info)
#                 prolific_code, has_completed_training, db_group = user_info
#                 st.session_state["group"] = db_group.strip().lower()
#             else:
#                 # Use URL param if user doesn't exist in DB
#                 group_param = st.query_params.get("g", ["2"])[0]
#                 group_assignment = "treatment" if group_param == "1" else "control"
#                 create_user(user_id, prolific_code=user_id, group=group_assignment)
#                 st.session_state["group"] = group_assignment

#             if user_completed_training(user_id):
#                 st.session_state["chat_thread"] = [{
#                     "sender": "Assistant",
#                     "message": "Welcome back! What would you like to do today?"
#                 }]
#                 st.session_state["chat_state"] = "menu"
#             else:
#                 st.session_state["chat_thread"] = [{
#                     "sender": "Assistant",
#                     "message": "Hi! I'm Goalie. Are you ready to learn about SMART goals?"
#                 }]
#                 st.session_state["chat_state"] = "intro"

#             # Auto-jump into reflection if week/session params exist and user is treatment
#             if st.session_state["group"] == "treatment":
#                 if "week" in st.query_params and "session" in st.query_params:
#                     st.session_state["chat_state"] = "reflection"

#             st.success("Welcome!")
#             st.rerun()
#         else:
#             st.error("Please provide your Prolific ID.")

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
        if st.button("Authenticate (DEV only)") and user_id:
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user_id
            if "did_rerun_auth" not in st.session_state:
                st.session_state["did_rerun_auth"] = True
                st.rerun()
            st.info(f"Manually authenticated as {user_id}")
    else:
        st.warning("Please access this link via Prolific.")
        st.stop()

    if st.session_state.get("authenticated"):
        user_info = get_user_info(user_id)

        if user_info:
            prolific_code, has_completed_training, db_group = user_info
            st.session_state["group"] = db_group.strip().lower()
        else:
            # Use URL param if user doesn't exist in DB
            group_param = st.query_params.get("g", ["2"])[0]
            group_assignment = "treatment" if group_param == "1" else "control"
            create_user(user_id, prolific_code=user_id, group=group_assignment)
            st.session_state["group"] = group_assignment

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

        # Auto-jump into reflection if week/session params exist and user is treatment
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

# for entry in st.session_state["chat_thread"]:
#     with st.chat_message("assistant" if entry["sender"] == "Assistant" else "user"):
#         st.markdown(entry["message"])

import streamlit.components.v1 as components

# Use pixel height for consistent layout
chat_height_px = 400
# if st.session_state["chat_state"] not in ["menu", "view_goals"] else 400

# Inject goal HTML into chat thread if viewing goals
if st.session_state["chat_state"] == "view_goals":
    if not any(
        "Your SMART Goals:" in m["message"] or "You haven’t created any goals" in m["message"]
        for m in st.session_state["chat_thread"]
    ):
        goals = get_goals(st.session_state["user_id"])
        if not goals:
            goal_html = "<div class='chat-left'>You haven’t created any goals yet.</div>"
        else:
            goal_html = "<div class='chat-left'><strong>Your SMART Goals:</strong><br>"
            for goal_id, goal_text in goals:
                goal_html += f"<strong>Goal:</strong> {goal_text}<br>"
                tasks = get_tasks(goal_id)
                if tasks:
                    for task_id, task_text, completed in tasks:
                        status = "✅" if completed else "⬜️"
                        goal_html += f"{status} {task_text}<br>"
                else:
                    goal_html += "<em>No subtasks yet.</em><br>"
                goal_html += "<hr>"
            goal_html += "</div>"

        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": goal_html
        })

chat_bubble_html = "".join([
    f'<div class="{"chat-left" if m["sender"] == "Assistant" else "chat-right"}">{m["message"]}</div>'
    for m in st.session_state["chat_thread"]
])

# Render chat container
with st.container():
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
        .chat-bubble {{
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease-in-out;
            margin: 5px 0;
            padding: 10px;
            max-width: 70%;
            border-radius: 10px;
            word-wrap: break-word;
        }}
        .chat-left {{
            background-color: #2b2f38;
            text-align: left;
            color: #eaeaea;
        }}
        .chat-right {{
            background-color: #005fcf;
            text-align: right;
            color: #ffffff;
            margin-left: auto;
        }}
    </style>
    </head>
    <body>
        <div id="chatbox" class="chat-wrapper"></div>

        <script>
            const messages = {[
                {
                    "sender": m["sender"],
                    "message": m["message"].replace("\\n", "<br>").replace('"', '\\"')
                } for m in st.session_state["chat_thread"]
            ]};

            const chatbox = document.getElementById("chatbox");

            function addBubble(index) {{
                if (index >= messages.length) return;

                const m = messages[index];
                const bubble = document.createElement("div");
                bubble.classList.add("chat-bubble");
                bubble.classList.add(m.sender === "Assistant" ? "chat-left" : "chat-right");
                bubble.innerHTML = m.message;

                chatbox.appendChild(bubble);

                // Trigger animation
                setTimeout(() => {{
                    bubble.style.opacity = 1;
                    bubble.style.transform = "translateY(0)";
                    chatbox.scrollTop = chatbox.scrollHeight;
                }}, 50);

                setTimeout(() => {{
                    addBubble(index + 1);
                }}, 600);  // delay between bubbles
            }}

            addBubble(0);
        </script>
    </body>
    </html>
    """, height=chat_height_px + 20, scrolling=False)
    
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


def run_intro():
    print("🟢 In run_intro()")
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
    print("🔵 In run_smart_training()")
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
        # time.sleep(0.7)
        # st.rerun()

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
        if st.button("✅ View Existing Goal and Tasks"):
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
    # Only add the chat message if not already rendered
    # already_rendered = any(
    #     "Your SMART Goals:" in m["message"] or "You haven’t created any goals" in m["message"]
    #     for m in st.session_state["chat_thread"]
    # )

    # if not already_rendered:
    #     goals = get_goals(st.session_state["user_id"])
    #     if not goals:
    #         goal_html = "<div class='chat-left'>You haven’t created any goals yet.</div>"
    #     else:
    #         goal_html = "<div class='chat-left'><strong>Your SMART Goals:</strong><br>"
    #         for goal_id, goal_text in goals:
    #             goal_html += f"<strong>Goal:</strong> {goal_text}<br>"
    #             tasks = get_tasks(goal_id)
    #             if tasks:
    #                 for task_id, task_text, completed in tasks:
    #                     status = "✅" if completed else "⬜️"
    #                     goal_html += f"{status} {task_text}<br>"
    #             else:
    #                 goal_html += "<em>No subtasks yet.</em><br>"
    #             goal_html += "<hr>"
    #         goal_html += "</div>"

    #     st.session_state["chat_thread"].append({
    #         "sender": "Assistant",
    #         "message": goal_html
    #     })

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