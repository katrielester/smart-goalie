import streamlit as st
from db import (
    get_goals, get_tasks, save_reflection, update_task_completion,
    save_task, get_last_reflection, get_next_week_number, reflection_exists,
    get_user_phase, update_user_phase
)
from llama_utils import summarize_reflection

progress_options = ["None", "A little", "Some", "Most", "Completed"]
progress_numeric = {"None": 0, "A little": 1, "Some": 2, "Most": 3, "Completed": 4}

def run_weekly_reflection():
    if st.session_state.get("group") != "treatment":
        st.warning("Reflections are only available for the treatment group.")
        st.stop()

    user_id = st.session_state["user_id"]

    query_params = st.query_params.to_dict()
    week = int(query_params.get("week", 1))
    session = query_params.get("session", "a")

    st.session_state["week"] = week
    st.session_state["session"] = session

    phase = get_user_phase(user_id)

    all_goals = get_goals(user_id)
    if not all_goals:
        st.info("You have no goals to reflect on yet.")
        return

    goal_id, goal_text = all_goals[0]

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

    if "reflection_step" not in st.session_state:
        st.session_state["reflection_step"] = 0
        st.session_state["task_progress"] = {}
        st.session_state["reflection_answers"] = {}
        st.session_state["current_task"] = 0

    if st.session_state["reflection_step"] == 0:
        last_reflection = get_last_reflection(user_id, goal_id)
        if last_reflection:
            last_content, last_week = last_reflection
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"📄 <b>Last Reflection (Week {last_week}):</b><br><br>{last_content.strip()}"
            })

        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": f"Let’s check in on how your goal is going:<br><br><b>{goal_text}</b><br><br>I'll walk you through your tasks one by one — just answer honestly, no pressure."
        })

        st.session_state["reflection_step"] = 1
        st.rerun()

    if 1 <= st.session_state["reflection_step"] <= len(tasks):
        idx = st.session_state["reflection_step"] - 1
        task_id, task_text, _ = tasks[idx]

        if f"ask_progress_{task_id}" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"How much progress did you make on the following task?<br><br><b>{task_text}</b>"
            })
            st.session_state[f"ask_progress_{task_id}"] = True
            st.rerun()

        selected = None
        with st.container():
            for option in progress_options:
                if st.button(option, key=f"{task_id}_{option}"):
                    selected = option
                    break

        if selected:
            st.session_state["chat_thread"].append({
                "sender": "User",
                "message": selected
            })
            st.session_state["task_progress"][task_id] = progress_numeric[selected]
            st.session_state["reflection_step"] += 1
            st.rerun()

    elif st.session_state["reflection_step"] == len(tasks) + 1:
        total = sum(st.session_state["task_progress"].values())
        max_possible = 4 * len(tasks)
        use_success_reflection = total >= 0.75 * max_possible

        if use_success_reflection:
            questions = [
                ("what", "✨ Just a quick one — what helped you make progress this week? (One sentence is fine!)"),
                ("so_what", "🔍 Why do you think it felt easier or more motivating this time?"),
                ("now_what", "➡️ What’s something you’d like to keep doing next week?")
            ]
        else:
            questions = [
                ("outcome", "💡 What’s one benefit you’d gain if next week goes really well?"),
                ("obstacle", "🧱 What got in the way of your tasks this week?"),
                ("plan", "🛠️ If that same obstacle happens again, what could you try?")
            ]

        q_idx = st.session_state.get("reflection_q_idx", 0)
        key, prompt = questions[q_idx]

        if f"ask_{key}" not in st.session_state:
            st.session_state["chat_thread"].append({"sender": "Assistant", "message": prompt})
            st.session_state[f"ask_{key}"] = True
            st.rerun()

        user_input = st.chat_input("Type your answer here...")
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

    elif st.session_state["reflection_step"] == len(tasks) + 2:
        idx = st.session_state.get("update_task_idx", 0)
        if idx < len(tasks):
            task_id, task_text, _ = tasks[idx]
            update_choice = st.radio(
                f"Do you want to keep, modify, or replace this task?<br><br><b>{task_text}</b>",
                ["Keep", "Modify", "Replace"],
                key=f"update_{task_id}"
            )
            if update_choice in ["Modify", "Replace"]:
                new_text = st.chat_input("Write the new version of this task:")
                if new_text:
                    update_task_completion(task_id, True)
                    save_task(goal_id, new_text)
                    st.session_state["chat_thread"].append({"sender": "Assistant", "message": f"✅ Task updated to: '{new_text}'"})
                    st.session_state["chat_thread"].append({"sender": "User", "message": new_text})
                    st.session_state["update_task_idx"] = idx + 1
                    st.rerun()
            else:
                st.session_state["chat_thread"].append({"sender": "Assistant", "message": f"👍 Task kept as is."})
                st.session_state["chat_thread"].append({"sender": "User", "message": update_choice})
                st.session_state["update_task_idx"] = idx + 1
                st.rerun()
        else:
            st.session_state["reflection_step"] += 1
            st.session_state["update_task_idx"] = 0
            st.rerun()

    elif st.session_state["reflection_step"] == len(tasks) + 3:
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

        save_reflection(user_id, goal_id, reflection_text, week_number=week, session=session)

        update_user_phase(user_id, phase + 1)

        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": "✅ Thanks for reflecting! Your responses are saved."
        })
        st.success("Reflection submitted and saved!")

        if st.button("⬅️ Return to Main Menu"):
            st.session_state["chat_state"] = "menu"

        for key in list(st.session_state.keys()):
            if key.startswith("reflection_") or key in [
                "task_progress", "reflection_answers",
                "update_task_idx", "reflection_q_idx"
            ]:
                del st.session_state[key]
        st.rerun()