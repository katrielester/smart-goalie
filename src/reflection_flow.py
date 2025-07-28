# reflection_flow.py

import streamlit as st
from db import (
    get_goals, get_tasks, save_reflection, update_task_completion,
    save_task, get_last_reflection, get_next_week_number, reflection_exists,
    get_user_phase, update_user_phase, get_user_group, replace_or_modify_task,
    save_reflection_response, save_reflection_draft, load_reflection_draft, delete_reflection_draft
)
from llama_utils import summarize_reflection, suggest_tasks_with_context
import json
from chat_thread import ChatThread

progress_options = [
    "Not started",
    "Started",
    "Halfway done",
    "Mostly completed",
    "Fully completed"
]
progress_numeric = {
    "Not started": 0,
    "Started": 1,
    "Halfway done": 2,
    "Mostly completed": 3,
    "Fully completed": 4,
}

def run_weekly_reflection():
    query_params = st.query_params.to_dict()

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = query_params.get("user_id")

    if "group" not in st.session_state:
        group_code_raw = get_user_group(st.session_state["user_id"])
        group_code = str(group_code_raw).strip()
        # st.write(f"DEBUG: Raw group from DB: {group_code_raw} (converted to '{group_code}')")
        if group_code == "1":
            st.session_state["group"] = "treatment"
        else:
            st.session_state["group"] = "control"

    if "group" not in st.session_state:
        st.error("❌ Group not set. Something went wrong in session initialization.")
        st.stop()
    elif st.session_state["group"] != "treatment":
        st.warning("Reflections are only available for the treatment group.")
        st.stop()
    if st.session_state.get("chat_state") != "reflection":
        st.warning("You're not currently in reflection mode.")
        st.stop()

    user_id = st.session_state["user_id"]

    week = int(query_params.get("week", 1))
    session = query_params.get("session", "a")

    st.session_state["week"] = week
    st.session_state["session"] = session

    phase = get_user_phase(user_id)

    all_goals = get_goals(user_id)
    if not all_goals:
        st.info("You have no goals to reflect on yet.")
        return
    
    # st.write(all_goals[0])
    goal_id = all_goals[0]["id"]
    goal_text = all_goals[0]["goal_text"]

    if reflection_exists(user_id, goal_id, week, session):
        if "reflection_acknowledged" not in st.session_state:
            if "chat_thread" not in st.session_state:
                st.session_state["chat_thread"] = ChatThread(st.session_state["user_id"])
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"✅ You've already submitted a reflection for <b>Week {week}, Session {session.upper()}</b>.<br><br>Thanks!"
            })
            st.session_state["reflection_acknowledged"] = True
            st.rerun()

        col1, col2 = st.columns(2)
        if col1.button("⬅️ Return to Main Menu"):
            st.session_state["chat_state"] = "menu"
            del st.session_state["reflection_acknowledged"]
            st.rerun()

        if col2.button("⬅️ Return to Prolific"):
            st.stop()

        return

    tasks = get_tasks(goal_id)
    # st.write(tasks)
    if not tasks:
        st.info("You have no tasks for your goal. Add tasks first.")
        return

    if "reflection_step" not in st.session_state:
        draft = load_reflection_draft(user_id, goal_id, week, session)

        if draft:
            st.session_state["reflection_step"] = draft["reflection_step"]
            
            raw_prog = draft["task_progress"]
            if isinstance(raw_prog, str):
                st.session_state["task_progress"] = json.loads(raw_prog)
            else:
                st.session_state["task_progress"] = raw_prog or {}
            
            raw_ans = draft["reflection_answers"]
            if isinstance(raw_ans, str):
                st.session_state["reflection_answers"] = json.loads(raw_ans)
            else:
                st.session_state["reflection_answers"] = raw_ans or {}

            st.session_state["update_task_idx"] = draft["update_task_idx"]
            st.session_state["reflection_q_idx"] = draft["reflection_q_idx"]
            if "chat_thread" not in st.session_state:
                st.session_state["chat_thread"] = ChatThread(st.session_state["user_id"])
        else:
            init_reflection_session()

        # if "chat_thread" not in st.session_state:
        #     st.session_state["chat_thread"]=[]

        # st.session_state["reflection_step"] = 0
        # st.session_state["task_progress"] = {}
        # st.session_state["reflection_answers"] = {}
        # st.session_state["current_task"] = 0

    if st.session_state["reflection_step"] == 0:
        st.write("Reflection step:", st.session_state.get("reflection_step"))

        last_reflection = get_last_reflection(user_id, goal_id)

        if last_reflection and last_reflection.get("reflection_text", "").strip():
            last_content = last_reflection["reflection_text"]
            last_week = last_reflection["week_number"]
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"📄 <b>Last Reflection (Week {last_week}):</b><br><br>{last_content.strip()}"
            })
        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": "🔸 Reflection Time 🔸"
        })
        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": f"Let’s check in on how your goal is going:<br><br><b>{goal_text}</b><br><br>I'll walk you through your tasks one by one. Just answer honestly, no pressure."
        })

        st.session_state["reflection_step"] = 1
        st.rerun()

    if 1 <= st.session_state["reflection_step"] <= len(tasks):
        idx = st.session_state["reflection_step"] - 1
        task = tasks[idx]
        task_id = task["id"]
        task_text = task["task_text"]

        # 1️⃣ Ask for progress if not already asked
        if f"ask_progress_{task_id}" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"How much progress did you make on this task?<br><br><b>{task_text}</b>"
            })
            st.session_state[f"ask_progress_{task_id}"] = True
            st.rerun()

        # 2️⃣ Show side-by-side buttons for the 5 options
        selected = None
        cols = st.columns(len(progress_options))
        for i, option in enumerate(progress_options):
            if cols[i].button(option, key=f"{task_id}_{option}"):
                selected = option
                break

        if selected and not st.session_state.get(f"justifying_{task_id}"):
            # echo user choice
            st.session_state["chat_thread"].append({
                "sender": "User",
                "message": selected
            })
            # store numeric rating
            st.session_state["task_progress"][task_id] = progress_numeric[selected]

            # 3️⃣ Immediately ask for a brief justification
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "What have you completed so far, and what still needs to be done?"
            })
            st.session_state[f"justifying_{task_id}"] = True
            st.rerun()

        # 4️⃣ Capture the user’s justification before moving on
        if st.session_state.get(f"justifying_{task_id}") and f"justified_{task_id}" not in st.session_state:
            justification = st.chat_input("Type your answer here…")
            if justification:
                # echo user justification
                st.session_state["chat_thread"].append({
                    "sender": "User",
                    "message": justification
                })
                # save it under reflection_answers
                st.session_state["reflection_answers"][f"justification_{task_id}"] = justification

                # mark as done and move to next task
                st.session_state[f"justified_{task_id}"] = True
                st.session_state["reflection_step"] += 1

                save_reflection_draft(
                    user_id=user_id,
                    goal_id=goal_id,
                    week_number=week,
                    session_id=session,
                    step=st.session_state["reflection_step"],
                    task_progress=st.session_state.get("task_progress", {}),
                    answers=st.session_state.get("reflection_answers", {}),
                    update_idx=st.session_state.get("update_task_idx", 0),
                    q_idx=st.session_state.get("reflection_q_idx", 0)
                )

                st.rerun()

        # selected = None
        # cols = st.columns(len(progress_options))
        # for idx, option in enumerate(progress_options):
        #     if cols[idx].button(option, key=f"{task_id}_{option}"):
        #         selected = option
        #         break

        # if selected:
        #     st.session_state["chat_thread"].append({
        #         "sender": "User",
        #         "message": selected
        #     })
        #     st.session_state["task_progress"][task_id] = progress_numeric[selected]
        #     st.session_state["reflection_step"] += 1
        #     save_reflection_draft(
        #         user_id=user_id,
        #         goal_id=goal_id,
        #         week_number=week,
        #         session_id=session,
        #         step=st.session_state["reflection_step"],
        #         task_progress=st.session_state.get("task_progress", {}),
        #         answers=st.session_state.get("reflection_answers", {}),
        #         update_idx=st.session_state.get("update_task_idx", 0),
        #         q_idx=st.session_state.get("reflection_q_idx", 0)
        #     )
        #     st.rerun()

    elif st.session_state["reflection_step"] == len(tasks) + 1:
        total = sum(st.session_state["task_progress"].values())
        max_possible = 4 * len(tasks)
        use_success_reflection = total >= 0.65 * max_possible

        if use_success_reflection:
            questions = [
                ("what", "✨ Just a quick one: <b>what helped you make progress this week?</b> (One sentence is fine!)"),
                ("so_what", "🔍 Why do you think it <b>felt easier or more motivating</b> this time?"),
                ("now_what", "➡️ What’s something you’d like to <b>keep doing next week</b>?")
            ]
        else:
            questions = [
                ("outcome", "💡 What’s one <b>benefit</b> you’d gain if next week goes really well?"),
                ("obstacle", "🚧 What <b>got in the way</b> of your tasks this week?"),
                ("plan", "🛠️ If that same obstacle happens again, <b>what could you try?</b>")
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
            save_reflection_draft(
                user_id=user_id,
                goal_id=goal_id,
                week_number=week,
                session_id=session,
                step=st.session_state["reflection_step"],
                task_progress=st.session_state.get("task_progress", {}),
                answers=st.session_state.get("reflection_answers", {}),
                update_idx=st.session_state.get("update_task_idx", 0),
                q_idx=st.session_state.get("reflection_q_idx", 0)
            )
            if q_idx < len(questions):
                st.session_state["reflection_q_idx"] = q_idx
                st.rerun()
            else:
                st.session_state["reflection_step"] += 1
                st.session_state["reflection_q_idx"] = 0
                st.rerun()

    # Goal Alignment Reflection
    elif st.session_state["reflection_step"] == len(tasks) + 2:
        if "ask_alignment" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "🧭 Thinking about your tasks and your goal, do you feel your current tasks still <b>match the goal well</b>?<br><br>Feel free to share your thoughts, whether they align well, or if anything feels a bit off."
            })
            st.session_state["ask_alignment"] = True
            st.rerun()

        user_input = st.chat_input("Type your answer here...")
        if user_input:
            st.session_state["chat_thread"].append({"sender": "User", "message": user_input})
            st.session_state["reflection_answers"]["task_alignment"] = user_input
            st.session_state["reflection_step"] += 1
            st.rerun()

    elif st.session_state["reflection_step"] == len(tasks) + 3:
        idx = st.session_state.get("update_task_idx", 0)
        if idx < len(tasks):
            task = tasks[idx]
            task_id = task["id"]
            task_text = task["task_text"]
            
            if f"ask_update_{task_id}" not in st.session_state:
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": f"What do you want to do with this task?<br><br><b>{task_text}</b>"
                })
                st.session_state[f"ask_update_{task_id}"] = True
                st.rerun()

            choices = ["Keep", "Modify", "Replace"]
            selected = None
            cols = st.columns(len(choices))
            for idx, choice in enumerate(choices):
                if cols[idx].button(choice, key=f"{task_id}_{choice}"):
                    selected = choice
                    break

            if selected:
                st.session_state["chat_thread"].append({
                    "sender": "User",
                    "message": selected
                })
                st.session_state[f"update_choice_{task_id}"] = selected

                save_reflection_draft(
                    user_id=user_id,
                    goal_id=goal_id,
                    week_number=week,
                    session_id=session,
                    step=st.session_state["reflection_step"],
                    task_progress=st.session_state.get("task_progress", {}),
                    answers=st.session_state.get("reflection_answers", {}),
                    update_idx=st.session_state.get("update_task_idx", 0),
                    q_idx=st.session_state.get("reflection_q_idx", 0)
                )

                if selected in ["Modify", "Replace"]:
                    st.session_state["awaiting_task_edit"] = True
                else:
                    st.session_state["chat_thread"].append({
                        "sender": "Assistant",
                        "message": "👍 Task kept as is."
                    })
                    st.session_state["update_task_idx"] += 1
                    st.rerun()

            if st.session_state.get("awaiting_task_edit") is True:
                # reuse goal_text you set at top of run_weekly_reflection()
                reflection_answers = st.session_state.get("reflection_answers", {})
                existing_tasks     = [t["task_text"] for t in tasks]
                
                # call with reflection + existing tasks
                suggestions = suggest_tasks_with_context(
                    goal_text,
                    reflection_answers,
                    existing_tasks
                )
                if suggestions:
                    st.session_state["chat_thread"].append({
                        "sender": "Assistant",
                        "message": (
                        "💡 Based on your goal and what you just reflected, here are some fresh task ideas:<br><br>" + suggestions
                        )
                    })
                # now ask them to write their updated task
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": "✍️ Please write the new version of this task."
                })
                st.session_state["awaiting_task_edit"] = "awaiting_input"
                st.rerun()

            elif st.session_state.get("awaiting_task_edit") == "awaiting_input":
                new_text = st.chat_input("Type your updated task here...")
                if new_text:
                    task = tasks[st.session_state["update_task_idx"]]
                    task_id = task["id"]
                    reason = "Modified" if st.session_state[f"update_choice_{task_id}"] == "Modify" else "Replaced"

                    new_task_id = replace_or_modify_task(goal_id, task_id, new_text, reason)

                    st.session_state["chat_thread"].append({
                        "sender": "Assistant",
                        "message": f"✅ Task updated to: '<b>{new_text}</b>'"
                    })
                    st.session_state["chat_thread"].append({
                        "sender": "User",
                        "message": new_text
                    })

                    st.session_state["awaiting_task_edit"] = False
                    st.session_state["update_task_idx"] += 1

                    save_reflection_draft(
                        user_id=user_id,
                        goal_id=goal_id,
                        week_number=week,
                        session_id=session,
                        step=st.session_state["reflection_step"],
                        task_progress=st.session_state.get("task_progress", {}),
                        answers=st.session_state.get("reflection_answers", {}),
                        update_idx=st.session_state.get("update_task_idx", 0),
                        q_idx=q_idx
                    )
                    st.rerun()
                # if new_text:
                #     task = tasks[st.session_state["update_task_idx"]]
                #     task_id = task["id"]
                #     reason = "Modified" if st.session_state[f"update_choice_{task_id}"] == "Modify" else "Replaced"

                #     new_task_id = replace_or_modify_task(goal_id, task_id, new_text, reason)

                #     st.session_state["chat_thread"].append({
                #         "sender": "Assistant",
                #         "message": f"✅ Task updated to: '{new_text}'"
                #     })
                #     st.session_state["chat_thread"].append({
                #         "sender": "User",
                #         "message": new_text
                #     })

                #     st.session_state["awaiting_task_edit"] = False
                #     st.session_state["update_task_idx"] += 1
                #     save_reflection_draft(
                #         user_id=user_id,
                #         goal_id=goal_id,
                #         week_number=week,
                #         session_id=session,
                #         step=st.session_state["reflection_step"],
                #         task_progress=st.session_state.get("task_progress", {}),
                #         answers=st.session_state.get("reflection_answers", {}),
                #         update_idx=st.session_state.get("update_task_idx", 0),
                #         q_idx=st.session_state.get("reflection_q_idx", 0)
                #     )
                #     st.rerun()
        else:
            st.session_state["reflection_step"] += 1
            st.session_state["update_task_idx"] = 0
            save_reflection_draft(
                user_id=user_id,
                goal_id=goal_id,
                week_number=week,
                session_id=session,
                step=st.session_state["reflection_step"],
                task_progress=st.session_state.get("task_progress", {}),
                answers=st.session_state.get("reflection_answers", {}),
                update_idx=st.session_state.get("update_task_idx", 0),
                q_idx=st.session_state.get("reflection_q_idx", 0)
            )
            st.rerun()

    elif st.session_state["reflection_step"] == len(tasks) + 4:
        task_results = []
        for task in tasks:  
            task_id = task["id"]
            task_text = task["task_text"]
            val = st.session_state["task_progress"][task_id]
            label = [k for k, v in progress_numeric.items() if v == val][0]
            task_results.append(f"{task_text}: {label}")
        progress_str = "<br>".join(task_results)

        answers = st.session_state["reflection_answers"]
        alignment = answers.get("task_alignment", None)
        if "what" in answers:
            reflection_text = (
                f"Task Progress:<br>{progress_str}<br><br>"
                + (f"ALIGNMENT: {alignment}<br><br>" if alignment else "")
                + f"WHAT: {answers.get('what')}<br>SO WHAT: {answers.get('so_what')}<br>NOW WHAT: {answers.get('now_what')}<br>"
            )
        else:
            reflection_text = (
                f"Task Progress:<br>{progress_str}<br><br>"
                + (f"ALIGNMENT: {alignment}<br><br>" if alignment else "")
                + f"OUTCOME: {answers.get('outcome')}<br>OBSTACLE: {answers.get('obstacle')}<br>PLAN: {answers.get('plan')}<br>"
            )

        reflection_id = save_reflection(user_id, goal_id, reflection_text, week_number=week, session_id=session)

        # Save task progress
        for task in tasks:
            task_id = task["id"]
            rating = st.session_state["task_progress"][task_id]
            save_reflection_response(reflection_id, task_id=task_id, progress_rating=rating)
                
        # Save open-text question answers
        for key, answer in st.session_state["reflection_answers"].items():
            save_reflection_response(reflection_id, answer_key=key, answer_text=answer)

        update_user_phase(user_id, phase + 1)

        active_tasks = get_tasks(goal_id)
        if not active_tasks:
            st.warning("⚠️ You have no active tasks left. Please add new tasks before the next reflection.")
            if st.button("➕ Add Tasks Now"):
                st.session_state["chat_state"] = "add_tasks"
                st.rerun()

        delete_reflection_draft(user_id, goal_id, week, session)

        summary = summarize_reflection(reflection_text)
        st.session_state["chat_thread"].append({
            "sender": "Assistant",
            "message": summary
        })
        

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

def init_reflection_session():
    if "chat_thread" not in st.session_state:
        st.session_state["chat_thread"] = ChatThread(st.session_state["user_id"])

    st.session_state["reflection_step"] = 0
    st.session_state["task_progress"] = {}
    st.session_state["reflection_answers"] = {}
    st.session_state["current_task"] = 0
    st.session_state["reflection_q_idx"] = 0
    st.session_state["update_task_idx"] = 0
    st.session_state["awaiting_task_edit"] = False