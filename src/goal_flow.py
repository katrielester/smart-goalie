# goal_flow.py

import streamlit as st
from llama_utils import (
    suggest_specific_fix, suggest_measurable_fix,
    suggest_achievable_fix, suggest_relevant_fix,
    suggest_timebound_fix, suggest_tasks_for_goal
)
from db import save_goal, save_task, get_tasks
from phases import goal_setting_flow

def run_goal_setting():
    step = goal_setting_flow[st.session_state["smart_step"]]
    texts = step["text"]
    if isinstance(texts, str):
        texts = [texts]

    current_index = st.session_state.get("message_index", 0)

    if current_index < len(texts):
        current_text = texts[current_index].replace("{current_goal}", st.session_state.get("current_goal", ""))
        st.session_state["chat_thread"].append({"sender": "Assistant", "message": current_text})
        st.session_state["message_index"] += 1
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

        elif step.get("input_type") == "text":
            user_input = st.chat_input("Type your answer")
            if user_input:
                st.session_state["chat_thread"].append({"sender": "User", "message": user_input})
                st.session_state["current_goal"] = user_input
                st.session_state["smart_step"] = step["next"]
                st.session_state["message_index"] = 0
                st.rerun()

        elif "fix_with_llm" in step:
            fix_type = step["fix_with_llm"]
            goal = st.session_state.get("current_goal", "")

            # STEP 1: Show 'Typing...' only once
            if "llm_typing" not in st.session_state:
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": "Typing..."
                })
                st.session_state["llm_typing"] = True
                st.rerun()

            # STEP 2: If 'Typing...' is already shown, call LLM and replace it
            if st.session_state.get("llm_typing"):
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

                formatted_goal = updated_goal.replace("1.", "<br>1.").replace("2.", "<br>2.").replace("3.", "<br>3.").strip()

                # Replace 'Typing...' with real output
                st.session_state["chat_thread"][-1]["message"] = f"This is an example of a more {fix_type} goal:<br><br>{formatted_goal}<br><br>Try adjusting your goal if it needs improvement.<br>"

                st.session_state["suggested_goal"] = formatted_goal
                st.session_state["smart_step"] = step["next"]
                st.session_state["message_index"] = 0
                del st.session_state["llm_typing"]
                st.rerun()

            # Format the goal output for readability
            formatted_goal = updated_goal.replace("1.", "<br>1.").replace("2.", "<br>2.").replace("3.", "<br>3.")
            formatted_goal = formatted_goal.replace("Answer:", "").strip()

            # Save cleaned output
            st.session_state["suggested_goal"] = formatted_goal
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"This is an example of a more {fix_type} goal:<br><br>{formatted_goal}<br><br>"
                        f"Try adjusting your goal if it needs improvement.<br>"
            })

            st.session_state["smart_step"] = step["next"]
            st.session_state["message_index"] = 0
            st.rerun()

        elif step.get("complete"):
            goal_id = save_goal(
                user_id=st.session_state["user_id"],
                goal_text=st.session_state["current_goal"]
            )

            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "Your SMART goal has been saved! Now let's break it down into smaller tasks you can do <b>this week</b>. We'll check in with you midweek to help you reflect and adjust if needed."
            })

            existing_tasks = [t[1] for t in get_tasks(goal_id)]
            suggested = suggest_tasks_for_goal(st.session_state["current_goal"], existing_tasks)

            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "Here are some example tasks you can consider (just suggestions):<br><br>" + suggested
            })

            st.session_state["goal_id_being_worked"] = goal_id
            st.session_state["task_count"] = 0
            st.session_state["chat_state"] = "add_tasks"
            st.rerun()

def run_add_tasks():
    if st.session_state["task_count"] >= 3:
        st.success("You've added 3 tasks. Great work!")
        st.session_state["chat_state"] = "menu"
        st.rerun()

    task_input = st.chat_input("Add a small task to help achieve your goal")
    if task_input:
        save_task(st.session_state["goal_id_being_worked"], task_input.strip())
        st.session_state["task_count"] += 1
        st.session_state["chat_thread"].append({"sender": "User", "message": f"Task: {task_input.strip()}"})
        if st.session_state["task_count"] >= 1:
            if st.button("Done Adding Tasks"):
                if st.session_state["task_count"] < 3:
                    st.warning("Try to add all 3 tasks for a smoother check-in later.")
                else:
                    st.success("Saved your goal and tasks!")
                    st.session_state["chat_state"] = "menu"
                    st.rerun()
