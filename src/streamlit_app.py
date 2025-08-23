#streamlit_app.py

import streamlit as st
import os
import uuid
from chat_thread import ChatThread
import streamlit.components.v1 as components

import textwrap

from study_text import study_period_phrase, reflection_invite_phrase


restore_id = str(uuid.uuid4())
print(f"🔄 Restore Cycle: {restore_id}")

st.set_page_config(page_title="SMART Goal Chatbot", layout="centered")

st.markdown(
    """
    <script>
      const observer = new MutationObserver(() => {
        const ta = document.querySelector('textarea[autofocus]');
        if (ta) {
          ta.removeAttribute('autofocus');
          observer.disconnect();
        }
      });
      observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
      /* Pin Streamlit's chat-input to the bottom */
      div[data-testid="stChat"] div[data-testid="stChatInputContainer"] {
        position: sticky !important;
        bottom: 0;
        z-index: 100;
        background: #1c1f26;
        padding-top: 8px;
      }
      /* Give your chat-iframe room to breathe */
      .chat-wrapper {
        height: calc(100vh - 80px) !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<style>
/* Make the 'Tip & Help' expander header stand out */
section[data-testid="stSidebar"] details[open] > summary {
  background: #2b6cb0 !important;   /* blue */
  color: #fff !important;
  border-radius: 8px;
  padding: 6px 10px;
}
section[data-testid="stSidebar"] details > summary:hover {
  filter: brightness(0.95);
}
</style>
""", unsafe_allow_html=True)



# healthz handler:
if st.query_params.get("healthz") is not None:
    st.write("")  # 200 OK
    st.stop()     # skip the rest

# ---- GLOBAL USER GUARD ----
user_id = st.session_state.get("user_id") or st.query_params.get("PROLIFIC_PID")
if not user_id:
    st.warning("⚠️ Please access the chatbot using your unique study link from Prolific (with your ID in the URL).")
    st.stop()
else:
    st.session_state["user_id"] = user_id  # Always sync to session state for later use
    if not isinstance(st.session_state.get("chat_thread"), ChatThread):
        st.session_state["chat_thread"] = ChatThread(user_id)
# ---------------------------

import time
from datetime import datetime
from db_utils import build_goal_tasks_text, set_state

from db import (
    create_user, user_completed_training, mark_training_completed,
    save_message_to_db, get_chat_history, get_user_info,
    save_goal, save_task, save_reflection,
    get_tasks, get_goals, user_goals_exist,
    get_goals_with_task_counts, get_last_reflection_meta, get_reflection_responses,
    get_session_state, save_session_state, reflection_exists
)
from reflection_flow import run_weekly_reflection
from goal_flow import run_goal_setting, run_add_tasks
from phases import smart_training_flow
from prompts import system_prompt_goal_refiner, system_prompt_reflection_summary
from logger import setup_logger


# st.write("CWD:", os.getcwd())
# st.write("Dir listing:", os.listdir())
# st.stop()


# replace your current DEV_MODE lines with this:
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

dev_param = st.query_params.get("dev")
if isinstance(dev_param, list):
    dev_param = dev_param[0]
if dev_param == "1":
    DEV_MODE = True

def ensure_download_content(goal_text, tasks):
    if "download_content" not in st.session_state:
        st.session_state["download_content"] = build_goal_tasks_text(goal_text, tasks)
    return st.session_state["download_content"]


logger = setup_logger()

# st.set_page_config(page_title="SMART Goal Chatbot", layout="centered")

st.markdown("""
    <style>
      /* Apply to all Streamlit buttons: normal, download, link */
      .stButton>button,
      .stDownloadButton>button,
      .stLinkButton>button {
        background-color: #1f77b4 !important;
        color: #fff      !important;  /* always white by default */
        border-radius: 8px !important;
      }
      /* Hover should remain white text on darker blue */
      .stButton>button:hover,
      .stDownloadButton>button:hover,
      .stLinkButton>button:hover {
        background-color: #145a86 !important;
        color: #fff !important;
      }

      /* In light-mode browsers, swap text to black for better contrast */
      @media (prefers-color-scheme: light) {
        .stButton>button,
        .stDownloadButton>button,
        .stLinkButton>button {
          color: #000 !important;
        }
        .stButton>button:hover,
        .stDownloadButton>button:hover,
        .stLinkButton>button:hover {
          color: #000 !important;
        }
      }
    .block-container {
            padding-top: 0.5rem !important;
            }
    h1 {
            margin-top: 2rem !important;
            margin-bottom: 0.5rem !important;
            }
    section[data-testid="stBlock"] {
            margin-bottom: 4px !important;
            padding-bottom: 4px !important;
            }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* ─── More space between all sidebar blocks ─── */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;         /* space between direct children */
        padding-bottom: 0.5rem !important;
    }
    /* ─── Extra padding around buttons ─── */
    section[data-testid="stSidebar"] button > div {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
    st.title("🎯 Your Dashboard")

    query_params = st.query_params
    prolific_id = query_params.get("PROLIFIC_PID")

    if prolific_id:
        user_id = prolific_id
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = user_id
        st.markdown(f"\n**Prolific ID:** {user_id}")

    else:
        st.warning("Please access this link via Prolific.")
        st.stop()
    
if "chat_state" in st.session_state:
    cstate =st.session_state["chat_state"]
    if cstate == "intro":
        txt_state= "Introduction"
    elif cstate == "smart_training":
        txt_state= "SMART Goal Training"
    elif cstate == "menu":
        txt_state= "Menu"
    elif cstate == "goal_setting":
        txt_state= "Goal Setting"
    elif cstate.startswith("reflection"):
        txt_state= "Reflection"
    elif cstate == "view_goals":
        txt_state= "View Goals"
    elif cstate == "add_tasks":
        txt_state= "Add Tasks"
    else:
        txt_state= "SMART Goalie"
    st.sidebar.write(f"**Phase**: {txt_state}\n")
    st.sidebar.divider()
else:
    st.sidebar.write("\n")


with st.sidebar:
    st.warning(
            "⏳ **Please be patient**\n\n"
            "When you click or submit, Goalie might take a moment and the page may refresh. That’s normal! \n\n Just wait for the next message to appear, no need to click or type twice. Double-pressing can sometimes add extra text or jump ahead."
        )
    with st.expander("💡 Tip & Help", expanded=False):
        st.write(
            "\n\n• Hit **View Goal & Tasks** to see, download, and add tasks to your plan.  \n\n"
            "• You can set up to 3 weekly tasks. \n\n"
            "• Collapse this panel for more space if you prefer."
        )

    if DEV_MODE:
        if not user_goals_exist (st.session_state["user_id"]):
            if st.button("DEV: Jump to Goal Setting"):
                set_state(
                    chat_state = "goal_setting",
                    goal_step = "initial_goal",
                    message_index = 0
                )
                st.session_state["chat_state"] = "goal_setting"
                st.session_state["goal_step"] = "initial_goal" 
                mark_training_completed(st.session_state["user_id"])
                st.session_state["message_index"] = 0
                st.rerun()

        if st.button("DEV: Jump to Reflection 1-a"):
            st.session_state["chat_state"] = "reflection"
            st.session_state["week"] = 1
            st.session_state["session"] = "a"
            st.rerun()

        if st.sidebar.button("DEV: Force clear session_state"):
            st.session_state.clear()
            st.rerun()

if dev_param=="1":
    # debug: show me what keys are present on *every* render
    st.sidebar.json(dict(st.session_state))
    # and show whether chat_state is missing
    st.sidebar.write("🛠 chat_state missing?", "chat_state" not in st.session_state)
    if st.sidebar.button("DEV: Jump to Reflection 1-b"):
        st.session_state["chat_state"] = "reflection"
        st.session_state["week"] = 1
        st.session_state["session"] = "b"
        st.rerun()

if st.session_state.get("authenticated") and "chat_state" not in st.session_state:
    query_params = st.query_params.to_dict()
    week = query_params.get("week", [None])[0]
    session = query_params.get("session", [None])[0]
    print("!!! Init Debug — Week:", week, "| Session:", session)

    user_id = st.session_state["user_id"]

    # Check if user exists in DB
    user_info = get_user_info(user_id)
    if not user_info:
        # default to control = "0"
        group = query_params.get("g", ["0"])[0]
        batch = query_params.get("b", ["-1"])[0]
        create_user(user_id, prolific_code=user_id, group=group, batch=batch)
        st.session_state["group"] = "treatment" if group == "1" else "control"
    else:
        group = user_info["group_assignment"]
        st.session_state["group"] = "treatment" if str(group).strip() == "1" else "control"

    print("🧬 DB restore fingerprint:", st.session_state.get("RESTORED_FROM_DB", "(not restored this run)"))

    saved = get_session_state(user_id) or {}

    q = st.query_params.to_dict()
    w = q.get("week", [None])[0] if isinstance(q.get("week"), list) else q.get("week")
    s = q.get("session", [None])[0] if isinstance(q.get("session"), list) else q.get("session")

    deep_link_present = bool(w and s)
    deep_target = f"reflection_{str(w).strip()}_{str(s).strip().lower()}" if deep_link_present else None
    saved_chat_state = saved.get("chat_state")

    # Only skip restore if there is a deep link AND it points to a different reflection
    should_skip_restore = deep_link_present and (deep_target != saved_chat_state)

    print ("restored_done" in st.session_state)

    if saved.get("needs_restore") and "restored_done" not in st.session_state and not should_skip_restore:
        logger.info("🔄 Restoring session from DB | user_id=%s | restore_id=%s", user_id, restore_id)
        print("🟩 DB restore triggered for", user_id)
        

        st.session_state["RESTORED_FROM_DB"] = str(restore_id)
        print("🔄 SESSION RESTORED FROM DB! UUID:", st.session_state["RESTORED_FROM_DB"])
        

        # 1) Restore your flow flags
        for k, v in saved.items():
            st.session_state[k] = v

        # 2) Rebuild only this phase's chat history
        current_phase = st.session_state["chat_state"]
        history = get_chat_history(user_id, current_phase)

        # 3) Create a fresh ChatThread and disable DB writes for replay
        if current_phase in ("view_goals", "add_tasks"):
            ct = ChatThread(user_id)
        else:
            orig_append = ChatThread.append
            ct = ChatThread(user_id)
            ct.append = lambda entry: list.append(ct, entry)

            # 4) Replay each message in order
            for row in history:
                ui_sender = "Assistant" if row["sender"] == "bot" else "User"
                ct.append({
                    "sender":    ui_sender,
                    "message":   row["message"],
                    "timestamp": row["timestamp"],
                })

            # 5) Re‑enable real append() so new messages still save
            ct.append = orig_append.__get__(ct, ChatThread)

        # 6) Store for the UI
        st.session_state["chat_thread"] = ct

        st.session_state["restored_done"] = True

        st.session_state["just_restored"] = True
        
        st.rerun()

    else:
        logger.info("⚪ No DB restore needed | user_id=%s | restore_id=%s", user_id, restore_id)
        print("🟦 No DB restore needed, menu phase set")

        # No restore needed, fresh start
        st.session_state["chat_state"]  = "menu"
        st.session_state.setdefault("chat_thread", ChatThread(user_id))


    goals = get_goals_with_task_counts(user_id)
    # only warn if they've actually added ≥1 task
    has_any_task = any(g["task_count"] > 0 for g in goals)
    
    if has_any_task and (user_info["has_completed_presurvey"] == False) and not (saved.get("needs_restore")):
        goal = goals[0]
        goal_id   = goal["id"]
        goal_text = goal["goal_text"]
        tasks     = get_tasks(goal_id, active_only=True)
        
        if "download_content" not in st.session_state:
            st.session_state["download_content"] = build_goal_tasks_text(
                goal_text,
                [ t["task_text"] for t in tasks ]  # even if tasks is empty, this will still work
                )
        gr_code = 1 if str(user_info["group_assignment"]).strip() == "1" else 0
        survey_url = (
                "https://tudelft.fra1.qualtrics.com/jfe/form/SV_7VP8TpSQSHWq0U6"
                f"?user_id={user_info['prolific_code']}&group={gr_code}"
            )

        # 1. Heading + warning
        st.title("📝 Pre-Survey Required")
        st.warning("You still need to complete a short pre-survey before continuing. It takes under 5 minutes.")

        # 2. Clean, dedented instructions
        st.markdown(textwrap.dedent("""
        1. **Download your plan**  
        If you haven't downloaded your goal and tasks, click the 📄 **Download Goal & Tasks** button below and save the file somewhere safe.

        2. **Take the survey**  
        Click the 🚀 **Open Pre-Survey** button to launch the Qualtrics survey in a new tab.

        3. **Return & resume**  
        When you're done, come back here and hit your browser's **Refresh** button to continue.
        """))

        # 3. Two-column actions
        col1, col2 = st.columns([1,1])
        with col1:
            data = ensure_download_content(goal_text, [t["task_text"] for t in tasks])
            st.download_button(
            label="📄 Download Goal & Tasks",
            data=data,
            file_name="my_smart_goal.txt",
            mime="text/plain",
            )
        with col2:
            st.link_button("🚀 Open Pre-Survey",survey_url)

        # 4. Friendly reminder
        st.info("After you finish the survey, come back and refresh the page to continue.")

        # 5. GROUP EXPLANATION
        if st.session_state["group"] == "treatment":
            st.info(
                f"Over {study_period_phrase()}, you will receive reflection invitations on Prolific {reflection_invite_phrase()}. "
                "These check‑ins will help you reflect on your SMART goal and the weekly tasks you just created."
            )
        else:
            st.info(
                f"After the survey, please work on the goal and tasks you just created at your own pace.\n "
                f"We'll be in touch again in {study_period_phrase()} with a brief follow-up.\n\n"
            )

        st.session_state.clear()

        # if "chat_thread" not in st.session_state:
        #     st.session_state["chat_thread"] = ChatThread(st.session_state["user_id"])

        st.stop()

    if not saved.get("needs_restore"):
        # Routing logic
        print("Week:", week)
        print("Session:", session)
        print("Group (from DB or URL):", st.session_state["group"], group)
        
        if st.session_state["group"] == "treatment" and week and session:
            phase_key = f"reflection_{week}_{session}"
            set_state(chat_state=phase_key, needs_restore=True)

        elif user_completed_training(user_id):
            set_state(
                chat_state="menu", 
                needs_restore=False
                )
        else:
            set_state(
                chat_state="intro", 
                needs_restore=False
                )

        # Common session vars
        st.session_state.setdefault("chat_thread", ChatThread(st.session_state["user_id"]))
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

# Only trigger when we are back at menu AND there is a goal with no tasks
if (
    st.session_state.get("chat_state") == "menu" 
    and goals 
    and not st.session_state.get("force_task_handled", False)
    and not st.session_state.get("needs_restore", False)):

    goal_with_no_active_tasks = next((g for g in goals if g["task_count"] == 0), None)

    if goal_with_no_active_tasks:
        # Prevent infinite rerun loop BEFORE rerun
        st.session_state["force_task_handled"] = True

        st.session_state["goal_id_being_worked"] = goal_with_no_active_tasks["id"]
        st.session_state["current_goal"] = goal_with_no_active_tasks["goal_text"]
        # st.session_state["tasks_saved"] = []
        st.session_state["tasks_saved"] = [
            t["task_text"] for t in get_tasks(goal_with_no_active_tasks["id"], active_only=True)
        ]
        st.session_state["task_entry_stage"] = "suggest"
        set_state(
            chat_state="add_tasks",
            goal_id_being_worked = goal_with_no_active_tasks["id"],
            current_goal = goal_with_no_active_tasks["goal_text"],
            task_entry_stage = "suggest",
            needs_restore = False
            )
        ct = ChatThread(st.session_state["user_id"])
        ct.append({
            "sender": "Assistant",
            "message": (
                "Welcome back! It looks like you've set a goal but haven't added any weekly tasks yet:<br><br>"
                f"<b>{goal_with_no_active_tasks['goal_text']}</b><br><br>"
                "Let's start by adding your first task to help you move forward this week."
            )
        })
        st.session_state["chat_thread"] = ct

        st.rerun()

vals = st.query_params.get("add_tasks_for_goal", [])
if vals:
    try:       
        goal_id = int(vals[0])
        goal_list = get_goals(st.session_state["user_id"])
        goal = next((g for g in goal_list if g["id"] == goal_id), None)
    except ValueError:
        goal_id = None

    if goal:
        # st.session_state["tasks_saved"] = []
        st.session_state["tasks_saved"] = [
            t["task_text"] for t in get_tasks(goal_id, active_only=True)
        ]
        set_state(
            chat_state="add_tasks",
            needs_restore = False,
            goal_id_being_worked = goal_id,
            current_goal = goal["goal_text"],
            task_entry_stage = "suggest"
            )

        # Only add message if not already in chat
        already_has_prompt = any("adding more tasks for your goal" in m["message"] for m in st.session_state["chat_thread"])
        if not already_has_prompt:
            ct = ChatThread(st.session_state["user_id"])
            ct.append({
                "sender": "Assistant",
                    "message": (
                        f"You're adding more tasks for your goal:<br><br><b>{goal['goal_text']}</b><br><br>"
                        "Let's break it down into small weekly steps."
                    )
            })
            st.session_state["chat_thread"] = ct
        st.rerun()

st.title("SMART Goalie")



# Use pixel height for consistent layout
chat_height_px = 500
# EXPERIMENTAL START #

previous_len = st.session_state.get("last_rendered_index", 0)
chat_list   = st.session_state.get("chat_thread", [])
current_len  = len(chat_list)


# Mark which are new
chat_bubble_html = ""
for i, m in enumerate(st.session_state["chat_thread"]):
    css_class = "chat-left" if m["sender"] == "Assistant" else "chat-right"
    if i >= previous_len:
        # This is a new message, hide initially
        chat_bubble_html += f'<div class="{css_class} message" style="display: none;">{m["message"]}</div>'
    else:
        chat_bubble_html += f'<div class="{css_class}">{m["message"]}</div>'

# Save current length for next render
st.session_state["last_rendered_index"] = current_len

# EXPERIMENTAL END #


# Render chat container
with st.container():
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
            height: calc(100vh - 40px) !important;
            overflow-y: auto;
            padding: 10px;
            padding-bottom: 0px !important;
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
            <div id="endofchat" style="height: 10px;"></div>
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

# # if we've been told to show a download, render it here in the normal Streamlit UI
# if st.session_state.get("show_download"):
#     st.download_button(
#         label="📄 Download your goal & tasks",
#         data=st.session_state["download_content"],
#         file_name="my_smart_goal.txt",
#         mime="text/plain",
#     )

    # EXPERIMENTAL VER END 

# ────────────────────────────────────────────────────────────
# JS “ping” to keep the WebSocket alive every 25 s
components.html(
    """
    <script>
      // Toggle a dummy boolean so the ping value changes each time
      window._ping = !window._ping;
      setInterval(() => {
        Streamlit.setComponentValue(window._ping);
      }, 25_000);
    </script>
    """,
    height=0,
    scrolling=False,
)
# ────────────────────────────────────────────────────────────

st.markdown("""
    <style>
    /* Remove default Streamlit padding/margin between components */
    div[data-testid="stVerticalBlock"] {
        gap: 1px !important;
        padding-bottom: 1px !important;
    }

    div.block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    /* Kill bottom margin of iframe container */
    iframe {
        margin-bottom: 0px !important;
        display: block;
    }
    </style>
""", unsafe_allow_html=True)





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
            set_state(
                chat_state= "smart_training", 
                message_index = 0, 
                needs_restore = True,
                smart_step = "intro")
            st.rerun()

def run_smart_training():
    first= not user_completed_training(st.session_state["user_id"])
    print("🔵 In run_smart_training()")
    if st.session_state["smart_step"] not in smart_training_flow:
        st.error(f"❌ Step '{st.session_state['smart_step']}' not found in smart_training_flow!")
        st.stop()
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
        # st.session_state["message_index"] += 1
        set_state(
            message_index = st.session_state["message_index"] + 1,
            needs_restore=first
            )
        time.sleep(0.3)
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
                # st.session_state["smart_step"] = step["next"][selected]
                # st.session_state["message_index"] = 0
                set_state(
                    smart_step = step["next"][selected],
                    message_index = 0,
                    needs_restore=first
                )
                st.rerun()
        elif step.get("complete"):
            if not(user_completed_training(st.session_state["user_id"])):
                mark_training_completed(st.session_state["user_id"])
                set_state(
                    chat_state= "goal_setting", 
                    message_index = 0,
                    goal_step = "initial_goal",
                    needs_restore=True
                    )
            else:
                set_state(
                    chat_state= "menu", 
                    message_index = 0,
                    needs_restore=False
                    )
            st.rerun()

def run_menu():
    user_id = st.session_state["user_id"]
    chat_thread = st.session_state.setdefault("chat_thread", [])

    # Only ever append if chat_thread is empty
    if not chat_thread:
        if user_goals_exist(user_id):
            goals = get_goals_with_task_counts(user_id)
            task_count = goals[0]["task_count"]
            tasks_left = max(3 - task_count, 0)
            if tasks_left > 0:
                add_line = f"You can add up to {tasks_left} more to keep the momentum going, "
            else:
                add_line = "You can"

            chat_thread.append({
                "sender": "Assistant",
                "message": (
                    f"🎉 Nice work so far! You've set {task_count}/3 tasks. <br>"
                    f"{add_line} view & download your current goal and tasks, or review the SMART training.  <br><br>"
                    "What would you like to do next?"
                )
                
            })
        else:
            chat_thread.append({
                "sender": "Assistant",
                "message": "You have not set a goal yet. Please create a goal to proceed!"
            })
        st.session_state["chat_thread"] = chat_thread
        st.rerun()

    last_msg = chat_thread[-1]
    goals_exist = user_goals_exist(user_id)

    # Only append menu bubble ONCE per menu render
    if (
        last_msg["sender"] == "Assistant"
        and last_msg["message"] == "You have not set a goal yet. Please create a goal to proceed!"
        and not goals_exist
    ):
        pass
    elif (
        last_msg["sender"] == "Assistant"
        and last_msg["message"].startswith("🎉 Nice work so far")
        and goals_exist
    ):
        pass
    else:
        if goals_exist:
            goals = get_goals_with_task_counts(user_id)
            task_count = goals[0]["task_count"]
            tasks_left = max(3 - task_count, 0)
            if tasks_left > 0:
                add_line = f"You can add up to {tasks_left} more to keep the momentum going, "
            else:
                add_line = "You can"

            chat_thread.append({
                "sender": "Assistant",
                "message": (
                    f"🎉 Nice work so far! You've set {task_count}/3 tasks. <br>"
                    f"{add_line} view & download your current goal and tasks, or review the SMART training.  <br><br>"
                    "What would you like to do next?"
                )
                
            })
        else:
            chat_thread.append({
                "sender": "Assistant",
                "message": "You have not set a goal yet. Please create a goal to proceed!"
            })
        st.session_state["chat_thread"] = chat_thread
        st.rerun()

    # ────── BUTTONS UI ──────

    col1,col2= st.columns(2)

    if not user_goals_exist(st.session_state["user_id"]):
        if col1.button("➕ Create a New Goal"):
            set_state(
                chat_state = "goal_setting",
                goal_step = "initial_goal",
                message_index = 0,
                needs_restore=True
                )
            st.rerun()
    else:
        if col1.button("✅ View Goal and Tasks"):
            st.session_state["trigger_view_goals"] = True
            set_state(
                chat_state = "view_goals",
                needs_restore=True
                )
            st.rerun()

    if user_completed_training(st.session_state["user_id"]):
        if col2.button("📚 Review SMART Goal Training"):
            set_state(
                chat_state = "smart_training",
                smart_step = "intro",
                message_index = 0,
                needs_restore=False
            )
            st.rerun()


def run_view_goals():
    # 1) grab & consume the “I just clicked view” flag
    triggered = st.session_state.get("trigger_view_goals", False)

    user_id = st.session_state["user_id"]
    goals   = get_goals_with_task_counts(user_id)
    if not goals:
        st.session_state["chat_thread"].append({
            "sender":"Assistant",
            "message":"You haven't created any goals yet."
        })
        # no return here — we still want to show the buttons below
    else:
        goal      = goals[0]
        goal_id   = goal["id"]
        goal_text = goal["goal_text"]
        tasks     = get_tasks(goal_id, active_only=True)

        if triggered:
            # only append these two bubbles ONCE, right after the button click
            html = "<div class='chat-left'>"
            html += f"<strong>Your SMART Goal:</strong><br>{goal_text}<br><br>"
            for t in tasks:
                status = "✅" if t["completed"] else "⬜️"
                html += f"{status} {t['task_text']}<br>"
            html += "</div>"

            st.session_state["chat_thread"].append({"sender":"Assistant","message":html})

            meta = get_last_reflection_meta(user_id, goal_id)
            if meta:
                rows = get_reflection_responses(meta["id"])
                done  = sum(1 for r in rows if r.get("task_id") and r["progress_rating"]==4)
                total = len([r for r in rows if r.get("task_id")])
                summary = (
                    "<div class='chat-left'>"
                    f"<b>Last Reflection (Week {meta['week_number']}):</b><br>"
                    f"✅ You completed {done}/{total} tasks."
                    "</div>"
                )
                st.session_state["chat_thread"].append({"sender":"Assistant","message":summary})
            st.session_state["trigger_view_goals"] = False
            st.rerun()

    # 2) now always render the two columns of buttons
    col1, col2, col3 = st.columns([1,1,1])
    if goals and len(tasks) < 3 and col1.button("➕ Add Another Task"):
        existing_active = [t["task_text"] for t in get_tasks(goal_id,active_only=True)]
        st.session_state.update({
            "chat_state":"add_tasks",
            "goal_id_being_worked":goal_id,
            "current_goal":goal_text,
            "tasks_saved":existing_active.copy(),
            "task_entry_stage":"suggest"
        })
        # reset thread to just the “adding tasks” prompt
        ct = ChatThread(user_id)
        ct.append({
            "sender":"Assistant",
            "message":(
                f"You're adding more tasks for your goal:<br><br><b>{goal_text}</b>"
            )
        })
        st.session_state["chat_thread"] = ct
        run_add_tasks()
        st.stop()

    if col2.button("⬅️ Back to Menu"):
        set_state(
            chat_state    = "menu",
            needs_restore = False
            )
        st.rerun()

    if goals:
        with col3:
            # build a simple text file: goal on top, then each active task
            if "download_content" not in st.session_state:
                st.session_state["download_content"] = build_goal_tasks_text(
                    goal_text,
                    [ t["task_text"] for t in tasks ]  # even if tasks is empty, this will still work
                    )
            st.download_button(
                label="📄 Download Goal & Tasks",
                data=st.session_state["download_content"],
                file_name="my_smart_goal.txt",
                mime="text/plain",
                )

# ────────────────────────────────────────────────────────────
# Ensure deep links like ?week=1&session=a always route into reflection,
# even when chat_state already exists.
# ONLY if that specific reflection does not exist yet.
# Only allow for treatment users and valid session values.
w = st.query_params.get("week")
s = st.query_params.get("session")
if st.session_state.get("group") == "treatment" and w and s:
    # Normalize values possibly coming as lists
    w = w[0] if isinstance(w, list) else w
    s = s[0] if isinstance(s, list) else s
    w = str(w).strip()
    s = str(s).strip().lower()

    in_reflection = str(st.session_state.get("chat_state", "")).startswith("reflection")
    finishing     = st.session_state.get("summary_pending") or st.session_state.get("_post_submit")
    if in_reflection and finishing:
        pass  # don't touch chat_state or query params during summary phase
    else:
        if w in {"1", "2"} and s in {"a", "b"}:
            user_id = st.session_state["user_id"]
            goals = get_goals(user_id)  
            if goals:
                goal_id = goals[0]["id"]
                # If NOT submitted yet, go to reflection
                if not reflection_exists(user_id, goal_id, int(w), s):
                    set_state(
                        chat_state=f"reflection_{w}_{s}",
                        week=int(w),
                        session=s,
                        needs_restore=True
                    )
                else:
                    # Already submitted, drop week/session so user can use the menu
                    st.toast(f"You have already submitted reflection session for Week {w}, Session {s}!", icon="✅")
                    st.query_params.pop("week", None)
                    st.query_params.pop("session", None)
                    set_state(chat_state="menu", needs_restore=False)
            else:
                # No goal yet, reflection makes no sense; clear params and stay menu
                st.query_params.pop("week", None)
                st.query_params.pop("session", None)
                set_state(chat_state="menu", needs_restore=False)
# ────────────────────────────────────────────────────────────

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
elif state.startswith("reflection"):
    run_weekly_reflection()
elif state == "view_goals":
    run_view_goals()
elif state == "add_tasks":
    run_add_tasks()