# reflection_flow.py

import streamlit as st
from db import (
    get_goals, get_tasks, save_reflection, update_task_completion,
    save_task, get_last_reflection, get_next_week_number, reflection_exists
)
from llama_utils import summarize_reflection

progress_options = ["None", "A little", "Some", "Most", "Completed"]
progress_numeric = {"None": 0, "A little": 1, "Some": 2, "Most": 3, "Completed": 4}

SIMS_QUESTIONS = [
    "Working on my tasks is interesting to me.",
    "I have fun performing my work tasks.",
    "I feel good when I am working on my tasks."
]
UWES_QUESTIONS = [
    "When working, I feel bursting with energy.",
    "I am enthusiastic about my work.",
    "I am immersed in my work."
]

def run_weekly_reflection():
    user_id = st.session_state["user_id"]

    # Get week and session from query params
    query_params = st.query_params.to_dict()
    week = int(query_params.get("week", 1))  # fallback = 1
    session = query_params.get("session", "a")  # fallback = 'a'

    st.session_state["week"] = week
    st.session_state["session"] = session

    # Get the goal
    all_goals = get_goals(user_id)
    if not all_goals:
        st.info("You have no goals to reflect on yet.")
        return

    goal_id, goal_text = all_goals[0]

    # Check if this session's reflection already exists
    if reflection_exists(user_id, goal_id, week, session):
        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": f"✅ You've already submitted a reflection for <b>Week {week}, Session {session.upper()}</b>.<br><br>Thanks!"
        })
        if st.button("⬅️ Return to Prolific"):
            st.stop()
        return

    tasks = get_tasks(goal_id)
    if not tasks:
        st.info("You have no tasks for your goal. Add tasks first.")
        return

    # Chat-style state: track where the user is in the reflection flow
    if "reflection_step" not in st.session_state:
        st.session_state["reflection_step"] = 0
        st.session_state["task_progress"] = {}
        st.session_state["reflection_answers"] = {}
        st.session_state["sims_responses"] = []
        st.session_state["uwes_responses"] = []
        st.session_state["current_task"] = 0

    # Show last reflection at the start
    if st.session_state["reflection_step"] == 0:

        last_reflection = get_last_reflection(user_id, goal_id)
        if last_reflection:
            last_content, last_week = last_reflection
            st.session_state["chat_thread"].append({"sender": "Assistant", "message":
                f"📄 <b>Last Reflection (Week {last_week}):</b><br><br>{last_content.strip()}"})
            
        st.session_state["chat_thread"].append({"sender": "Assistant", "message":
            f"Now, let's reflect on your goal:<br><br></b>{goal_text}</b><br><br> I'll ask about each task, one by one."
        })
        
        st.session_state["reflection_step"] = 1
        st.rerun()

    # 1. Ask about progress for each task
    if 1<= st.session_state["reflection_step"] <= len(tasks):
        idx = st.session_state["reflection_step"] - 1
        task_id, task_text, _ = tasks[idx]

        if f"ask_progress_{task_id}" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"How much progress did you make on the following task: <br><br> <b>{task_text}</b>"
            })
            st.session_state[f"ask_progress_{task_id}"] = True
            st.rerun()
        
        selected=None
        with st.container():
            for option in progress_options:
                if st.button(option, key=f"{task_id}_{option}"):
                    selected = option
                    break

        if selected:
            st.session_state["chat_thread"].append({
                "sender":"User",
                "message":selected
            })
            st.session_state["task_progress"][task_id] = progress_numeric[selected]
            st.session_state["reflection_step"] +=1
            st.rerun()


    # 2. Once all tasks have been rated, branch: Success (What-So-What-NowWhat) or WOOP
    elif st.session_state["reflection_step"] == len(tasks) + 1:
        total = sum(st.session_state["task_progress"].values())
        max_possible = 4 * len(tasks)
        use_success_reflection = total >= 0.75 * max_possible

        if use_success_reflection:
            # What? So What? Now What?
            questions = [
                ("what", "What helped you make progress on this goal?"),
                ("so_what", "Why do you think this goal was easier or more motivating this week?"),
                ("now_what", "What will you carry forward into next week’s plan?")
            ]
        else:
            # WOOP
            questions = [
                ("outcome", "If you succeed next week, what’s a benefit you’d experience?"),
                ("obstacle", "What was the biggest barrier this week?"),
                ("plan", "Plan: If [obstacle], then I will [action].")
            ]

        q_idx = st.session_state.get("reflection_q_idx", 0)
        key, prompt = questions[q_idx]
        
        if f"ask_{key}" not in st.session_state:
            st.session_state["chat_thread"].append({"sender": "Assistant", "message": prompt})
            st.session_state[f"ask_{key}"] = True
            st.rerun()

        user_input = st.chat_input("Type your answer...")
        if user_input:
            st.session_state["chat_thread"].append({"sender": "User", "message": user_input})
            st.session_state["reflection_answers"][key] = user_input
            q_idx += 1
            if q_idx < len(questions):
                st.session_state["reflection_q_idx"] = q_idx
                st.rerun()
            else:
                st.session_state["reflection_step"] += 1
                st.session_state["reflection_q_idx"] = 0
                st.rerun()

    # 3. Task update for each task (optional, chat-style)
    elif st.session_state["reflection_step"] == len(tasks) + 2:
        idx = st.session_state.get("update_task_idx", 0)
        if idx < len(tasks):
            task_id, task_text, _ = tasks[idx]
            update_choice = st.radio(
                f"Do you want to keep, modify, or replace the task '{task_text}'?",
                ["Keep", "Modify", "Replace"],
                key=f"update_{task_id}"
            )
            if update_choice in ["Modify", "Replace"]:
                new_text = st.chat_input(f"Enter the new version for the task '{task_text}':")
                if new_text:
                    update_task_completion(task_id, True)
                    save_task(goal_id, new_text)
                    st.session_state["chat_thread"].append({"sender": "Assistant", "message": f"Task '{task_text}' will be updated to: '{new_text}'"})
                    st.session_state["chat_thread"].append({"sender": "User", "message": new_text})
                    st.session_state["update_task_idx"] = idx + 1
                    st.rerun()
            else:
                st.session_state["chat_thread"].append({"sender": "Assistant", "message": f"Do you want to keep, modify, or replace the task '{task_text}'?"})
                st.session_state["chat_thread"].append({"sender": "User", "message": update_choice})
                st.session_state["update_task_idx"] = idx + 1
                st.rerun()
        else:
            st.session_state["reflection_step"] += 1
            st.session_state["update_task_idx"] = 0
            st.rerun()

    # 4. Motivation and Engagement, chat style (SIMS, then UWES)
    # elif st.session_state["reflection_step"] == len(tasks) + 3:
    #     all_qs = SIMS_QUESTIONS + UWES_QUESTIONS
    #     q_idx = st.session_state.get("motivation_idx", 0)
    #     q = all_qs[q_idx]
    #     scale = 5 if q in SIMS_QUESTIONS else 7
    #     if f"ask_motivation_{q_idx}" not in st.session_state:
    #         st.session_state["chat_thread"].append({"sender": "Assistant", "message": q})
    #         st.session_state[f"ask_motivation_{q_idx}"] = True
    #         st.rerun()

    #     user_input = st.chat_input("Enter a number from 1 to 5" if scale == 5 else "Enter a number from 1 to 7")
    #     if user_input:
    #         try:
    #             val = int(user_input.strip())
    #             if 1 <= val <= scale:
    #                 st.session_state["chat_thread"].append({"sender": "User", "message": user_input})
    #                 if q in SIMS_QUESTIONS:
    #                     st.session_state["sims_responses"].append(val)
    #                 else:
    #                     st.session_state["uwes_responses"].append(val)
    #                 st.session_state["motivation_idx"] = q_idx + 1
    #                 st.rerun()
    #             else:
    #                 st.session_state["chat_thread"].append({"sender": "Assistant", "message": f"Please enter a number between 1 and {scale}."})
    #         except ValueError:
    #             st.session_state["chat_thread"].append({"sender": "Assistant", "message": "Please enter a valid number."})
    #         q_idx += 1
    #         if q_idx < len(all_qs):
    #             st.session_state["motivation_idx"] = q_idx
    #             st.rerun()
    #         else:
    #             st.session_state["reflection_step"] += 1
    #             st.session_state["motivation_idx"] = 0
    #             st.rerun()

    # 5. Final summary and save
    elif st.session_state["reflection_step"] == len(tasks) + 4:
        # Assemble reflection text
        task_results = []
        for task_id, task_text, _ in tasks:
            val = st.session_state["task_progress"][task_id]
            label = [k for k, v in progress_numeric.items() if v == val][0]
            task_results.append(f"{task_text}: {label}")
        progress_str = "<br>".join(task_results)

        answers = st.session_state["reflection_answers"]
        if "what" in answers:
            reflection_text = (
                f"Task Progress:<br>{progress_str}<br><br>"
                f"WHAT: {answers.get('what')}<br>SO WHAT: {answers.get('so_what')}<br>NOW WHAT: {answers.get('now_what')}<br>"
            )
        else:
            reflection_text = (
                f"Task Progress:<br>{progress_str}<br><br>"
                f"OUTCOME: {answers.get('outcome')}<br>OBSTACLE: {answers.get('obstacle')}<br>PLAN: {answers.get('plan')}<br>"
            )

        # Save to DB
        next_week = get_next_week_number(user_id, goal_id)
        save_reflection(user_id, goal_id, reflection_text, week_number=week, session=session)

        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": "Thanks for reflecting! Your responses are saved."
        })
        st.success("Reflection submitted and saved!")
        if st.button("⬅️ Return to Main Menu"):
            st.session_state["chat_state"] = "menu"
        # Optionally clear chatbot state too:
        for key in list(st.session_state.keys()):
            if key.startswith("reflection_") or key in [
                "task_progress", "reflection_answers",
                "sims_responses", "uwes_responses",
                "motivation_idx", "update_task_idx"
            ]:
                del st.session_state[key]
        st.rerun()
    
        # Optionally summarize
        # summary = summarize_reflection(reflection_text)
        # st.session_state["chat_thread"].append({"sender": "Assistant", "message": summary})
        # Reset session state for next use
        for key in ["reflection_step", "task_progress", "reflection_answers", "sims_responses", "uwes_responses"]:
            if key in st.session_state:
                del st.session_state[key]