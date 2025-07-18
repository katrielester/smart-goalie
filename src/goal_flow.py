# goal_flow.py

import streamlit as st
from llama_utils import (
    suggest_specific_fix, suggest_measurable_fix,
    suggest_achievable_fix, suggest_relevant_fix,
    suggest_timebound_fix, suggest_tasks_for_goal,
    extract_goal_variants, check_smart_feedback
)
from db import save_goal, save_task, get_tasks, get_user_phase, update_user_phase
from phases import goal_setting_flow, goal_setting_flow_score

def run_goal_setting():
    USE_LLM_SCORING=True;
    if "goal_step" not in st.session_state:
        st.session_state["goal_step"] = "initial_goal"

    flow = goal_setting_flow_score if USE_LLM_SCORING else goal_setting_flow;

    step = flow[st.session_state["goal_step"]]
    texts = step["text"]
    if isinstance(texts, str):
        texts = [texts]

    current_index = st.session_state.get("message_index", 0)

    if current_index < len(texts):
        current_text = texts[current_index]
        current_text = current_text.replace(
            "{current_goal}", st.session_state.get("current_goal", "")
        )
        
        if USE_LLM_SCORING:
            current_text = current_text.replace(
                "{llm_feedback_result}", st.session_state.get("llm_feedback_result", "")
            )
        
        st.session_state["chat_thread"].append({"sender": "Assistant", "message": current_text})
        st.session_state["message_index"] += 1
        st.rerun()

    elif step.get("buttons"):
        selected = None
        cols = st.columns(len(step["buttons"]))
        for idx, btn in enumerate(step["buttons"]):
            if cols[idx].button(btn, key=f"btn_{btn}"):
                selected = btn
                break
        if selected:
            st.session_state["chat_thread"].append({"sender": "User", "message": selected})
            st.session_state["goal_step"] = step["next"][selected]
            st.session_state["message_index"] = 0
            st.rerun()

    elif step.get("input_type") == "text":
        user_input = st.chat_input("Type your answer")
        if user_input:
            st.session_state["chat_thread"].append({"sender": "User", "message": user_input})
            st.session_state["current_goal"] = user_input
            st.session_state["goal_step"] = step["next"]
            st.session_state["message_index"] = 0
            st.rerun()

    elif "llm_feedback" in step:
        dimension = step["llm_feedback"]
        goal = st.session_state.get("current_goal", "")

        if "llm_feedback_pending" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "Analyzing your goal…"
            })
            st.session_state["llm_feedback_pending"] = True
            st.rerun()

        else:
            feedback = check_smart_feedback(goal, dimension).strip()
            st.session_state["chat_thread"][-1]["message"] = feedback
            st.session_state["goal_step"] = step["next"]
            del st.session_state["llm_feedback_pending"]
            st.session_state["message_index"] = 0
            st.session_state["llm_feedback_result"] = feedback
            st.rerun()

    elif "fix_with_llm" in step:
        fix_type = step["fix_with_llm"]
        goal = st.session_state.get("current_goal", "")

        if "llm_typing" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "Typing..."
            })
            st.session_state["llm_typing"] = True
            st.rerun()

        else:
            if fix_type == "specific":
                updated_goal = suggest_specific_fix(goal)
            elif fix_type == "measurable":
                updated_goal = suggest_measurable_fix(goal)
            elif fix_type == "achievable":
                updated_goal = suggest_achievable_fix(goal)
            elif fix_type == "relevant":
                updated_goal = suggest_relevant_fix(goal)
            elif fix_type == "timebound":
                updated_goal = suggest_timebound_fix(goal)
            else:
                updated_goal = ""

            formatted_variants = extract_goal_variants(updated_goal).strip()
            current_goal = st.session_state.get("current_goal", "")

            st.session_state["chat_thread"][-1]["message"] = (
                f"{formatted_variants}<br><br>"
            )

            del st.session_state["llm_typing"]
            st.session_state["goal_step"] = step["next"]
            st.session_state["message_index"] = 0
            st.rerun()

    elif step.get("complete"):
        goal_id = save_goal(
            user_id=st.session_state["user_id"],
            goal_text=st.session_state["current_goal"]
        )

        st.session_state["goal_id_being_worked"] = goal_id
        st.session_state["task_count"] = 0
        st.session_state["tasks_entered"] = []
        
        existing_tasks = [t["task_text"] for t in get_tasks(goal_id)]
        suggested = suggest_tasks_for_goal(st.session_state["current_goal"], existing_tasks)

        st.session_state["chat_thread"].extend([
            {
                "sender": "Assistant",
                "message": "Your SMART goal has been saved! Now let's break it down into smaller tasks you can do <b>this week</b>. We'll check in with you midweek to help you reflect and adjust if needed."
            },
            {
                "sender": "Assistant",
                "message": (
                    "You’ll now break your goal into weekly tasks. "
                    "<br><br>"
                    "<b>Here’s how it works:</b><br>"
                    "- You’ll set up to 3 small tasks to complete this week<br>"
                    "- These tasks should help you make progress on your goal<br>"
                    "- You’ll reflect on your progress twice each week (midweek and weekend)"
                    "<br><br>"
                    "Try to keep your tasks small, realistic, and clearly tied to this week’s focus."
                )
            },
            {
                "sender": "Assistant",
                "message": "Here are some example tasks you can consider based on your goal:" 
                    + "<br><br>" + suggested
            },
            {
                "sender": "Assistant",
                "message": "Now it’s your turn! What’s one small task you’d like to add first?"
            }
        ])
        st.session_state["task_entry_stage"] = "entry"
        st.session_state["chat_state"] = "add_tasks"
        st.rerun()


def run_add_tasks():
    print("DEBUG: run_add_tasks() triggered")
    print("→ task_entry_stage:", st.session_state["task_entry_stage"])
    goal_id = st.session_state.get("goal_id_being_worked")

    if "tasks_saved" not in st.session_state:
        st.session_state["tasks_saved"] = []

    if "task_entry_stage" not in st.session_state:
        st.session_state["task_entry_stage"] = "suggest"

    # ✅ Always run this if in suggest stage (even after rerun)
    if st.session_state["task_entry_stage"] == "suggest":
        if "suggestion_pending" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "Thinking of task suggestions for you… ✍️"
            })
            st.session_state["suggestion_pending"] = True
            st.rerun()
        else:
            existing_tasks = [t["task_text"] for t in get_tasks(goal_id)]
            current_goal = st.session_state.get("current_goal", "")
            try:
                suggested = extract_goal_variants(suggest_tasks_for_goal(current_goal, existing_tasks))
            except:
                suggested = (
                    "1. Break down your goal into a 30-minute session<br>"
                    "2. Block calendar time to work on it<br>"
                    "3. Set a reminder to check your progress"
                )

            st.session_state["chat_thread"][-1] = {
                "sender": "Assistant",
                "message": f"Here are some task ideas based on your goal:<br><br>{suggested}<br><br>"
                        "Type one of these or add your own!"
            }
            st.session_state["task_entry_stage"] = "entry"
            del st.session_state["suggestion_pending"]
            st.rerun()

    elif st.session_state["task_entry_stage"] == "entry":
        task_input = st.chat_input("Type a small task you'd like to do")

        if task_input:
            st.session_state["candidate_task"] = task_input.strip()
            st.session_state["chat_thread"].append({
                "sender": "User",
                "message": task_input.strip()
            })
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"Would you like to save this task?<br><br><b>{task_input.strip()}</b><br><br>"
                           "Please confirm below."
            })
            st.session_state["task_entry_stage"] = "confirm"
            st.rerun()

    elif st.session_state["task_entry_stage"] == "confirm":
        col1, col2 = st.columns([1, 1])
        if col1.button("✅ Yes, save task"):
            existing_active_tasks = get_tasks(goal_id)
            if len(existing_active_tasks) >= 3:
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": (
                        "⚠️ You already have 3 active tasks for this goal.<br>"
                        "Please replace or archive one during your next reflection before adding more."
                    )
                })
                st.session_state["chat_state"] = "menu"
                del st.session_state["task_entry_stage"]
                st.rerun()
            task = st.session_state.pop("candidate_task")
            save_task(goal_id, task)
            st.session_state["force_task_handled"] = False
            st.session_state["tasks_saved"].append(task)

            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"Saved: <b>{task}</b>"
            })

            if len(st.session_state["tasks_saved"]) < 3:
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": "Would you like to add another task?"
                })
                st.session_state["task_entry_stage"] = "add_more_decision"
            else:
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": "You've added 3 tasks! You're all set for now."
                })
                if get_user_phase(st.session_state["user_id"]) < 2:
                    show_reflection_explanation()
                    update_user_phase(st.session_state["user_id"], 2)
                st.session_state["chat_state"] = "menu"
                del st.session_state["task_entry_stage"]
            st.rerun()

        if col2.button("❌ No, I want to edit"): 
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "No problem! Please enter a new task."
            })
            st.session_state["task_entry_stage"] = "entry"
            del st.session_state["candidate_task"]
            st.rerun()
    elif st.session_state["task_entry_stage"] == "add_more_decision":
        col1, col2 = st.columns([1, 1])
        if col1.button("➕ Yes, add another"):
            st.session_state["task_entry_stage"] = "suggest"
            st.rerun()

        if col2.button("✅ No, done for now"):
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"You’ve added {len(st.session_state['tasks_saved'])} task(s). "
                        "You can review or update them during your reflection later."
            })
            if get_user_phase(st.session_state["user_id"]) < 2:
                show_reflection_explanation()
                update_user_phase(st.session_state["user_id"], 2)
            st.session_state["chat_state"] = "menu"
            del st.session_state["task_entry_stage"]
            st.rerun()


def show_reflection_explanation():
    group = st.session_state.get("group")
    if group == "treatment":
        msg = (
            "You’re all set! Over the next two weeks, you’ll receive reflection prompts here in this chat roughly twice a week. "
            "These check-ins will help you reflect on your SMART goal and the weekly tasks you just created.\n\n"
            "Looking forward to seeing your progress!"
        )
    else:
        msg = (
            "You’re all set! Over the next two weeks, you’ll receive reminder messages via Prolific around twice a week. "
            "You can reflect on your goal however you’d like, i’s up to you.\n\nThanks again for participating!"
        )

    st.session_state["chat_thread"].append({"sender": "Assistant", "message": msg})
    
    st.session_state["chat_thread"].append({
        "sender": "Assistant",
        "message": (
            "Awesome job setting your goal and tasks! Just one last step, please take a quick survey to lock it in. You’ll get a code at the end to return to Prolific. "
            "<br><br><a href='[QUALTRICS PRE-SURVEY LINK]' target='_blank'>Click here to begin the survey</a>"
        )
    })