# reflection_flow.py
import streamlit as st
from db import get_goals, get_tasks, save_reflection, update_task_completion, save_task
from llama_utils import summarize_reflection

# Ratings for progress per subtask
progress_options = ["None", "A little", "Some", "Most", "Completed"]
progress_numeric = {"None": 0, "A little": 1, "Some": 2, "Most": 3, "Completed": 4}

# SIMS + UWES Questions
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
    all_goals = get_goals(user_id)
    overall_reflection_data = []

    for goal_id, goal_text in all_goals:
        st.markdown(f"### Goal: {goal_text}")
        tasks = get_tasks(goal_id)

        st.markdown("#### How much progress did you make on each task?")
        task_progress = {}

        for task_id, task_text, _ in tasks:
            rating = st.radio(f"{task_text}", progress_options, key=f"task_{task_id}_rating")
            task_progress[task_id] = progress_numeric[rating]

        # Determine which reflection path to use
        progress_sum = sum(task_progress.values())
        max_possible = 4 * len(task_progress)  # 4 = max rating
        use_success_reflection = progress_sum >= 0.75 * max_possible

        if use_success_reflection:
            st.subheader("Success Reflection (What – So What – Now What)")
            what = st.text_area("What helped you make progress on this goal?")
            so_what = st.text_area("Why do you think this goal was easier or more motivating this week?")
            now_what = st.text_area("What will you carry forward into next week’s plan?")
            full_reflection = f"WHAT: {what}\nSO WHAT: {so_what}\nNOW WHAT: {now_what}"
        else:
            st.subheader("WOOP Reflection")
            outcome = st.text_area("Outcome – If you succeed next week, what’s a benefit you’d experience?")
            obstacle = st.text_area("Obstacle – What was the biggest barrier this week?")
            plan = st.text_area("Plan – If [obstacle], then I will [action].")
            full_reflection = f"OUTCOME: {outcome}\nOBSTACLE: {obstacle}\nPLAN: {plan}"

        # Task update
        st.subheader("Update your tasks for next week")
        for task_id, task_text, _ in tasks:
            update = st.radio(
                f"Update for task: {task_text}",
                ["Keep", "Modify", "Replace"],
                key=f"task_{task_id}_update"
            )
            if update in ["Modify", "Replace"]:
                new_text = st.text_input(f"New version for task:", key=f"new_task_text_{task_id}")
                if new_text:
                    update_task_completion(task_id, True)  # mark old as complete (archived)
                    save_task(goal_id, new_text)

        st.markdown("---")
        save_reflection(user_id, goal_id, full_reflection, week_number=1)  # Update week logic if needed
        overall_reflection_data.append(full_reflection)

    st.subheader("Final Questions – Motivation & Engagement")

    for q in SIMS_QUESTIONS:
        st.slider(q, 1, 5, key=f"sims_{q}")

    for q in UWES_QUESTIONS:
        st.slider(q, 1, 7, key=f"uwes_{q}")

    if st.button("Submit Weekly Reflection"):
        summary = summarize_reflection("\n\n".join(overall_reflection_data))
        st.session_state["chat_thread"].append({"sender": "Assistant", "message": summary})
        st.success("Reflection submitted! Your insights have been saved.")
