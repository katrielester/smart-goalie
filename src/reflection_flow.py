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
from db_utils import set_state

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

def save_reflection_state(needs_restore=True):
    # also grab any one-off “asked” or “justifying” flags so they survive a reload/restore
    dynamic = {
        k: v for k, v in st.session_state.items()
        if k.startswith(("ask_", "justifying_", "justified_"))
        }
    set_state(
      reflection_step    = st.session_state["reflection_step"],
      task_progress      = st.session_state["task_progress"],
      reflection_answers = st.session_state["reflection_answers"],
      update_task_idx    = st.session_state["update_task_idx"],
      reflection_q_idx   = st.session_state["reflection_q_idx"],
      awaiting_task_edit = st.session_state["awaiting_task_edit"],
      editing_choice     = st.session_state["editing_choice"],
      needs_restore      = needs_restore,
      **dynamic
    )


def run_weekly_reflection():
    query_params = st.query_params.to_dict()

    if "task_progress" in st.session_state and isinstance(st.session_state["task_progress"], dict):
        raw = st.session_state["task_progress"]
        fixed = {}
        for k, v in raw.items():
            # drop any null‐key
            if k in (None, "null"):
                continue
            try:
                ik = int(k)
            except (ValueError, TypeError):
                ik = k
            fixed[ik] = v
        st.session_state["task_progress"] = fixed

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = query_params.get("user_id")

    if "group" not in st.session_state:
        group_code_raw = get_user_group(st.session_state["user_id"])
        group_code = str(group_code_raw).strip()
        # st.write(f"DEBUG: Raw group from DB: {group_code_raw} (converted to '{group_code}')")
        if group_code == "1":
            set_state(group = "treatment")
        else:
            set_state(group = "control")

    if "group" not in st.session_state:
        st.error("❌ Group not set. Something went wrong in session initialization.")
        st.stop()
    elif st.session_state["group"] != "treatment":
        st.warning("Reflections are only available for the treatment group.")
        st.stop()
    elif not st.session_state.get("chat_state", "").startswith("reflection"):
        st.warning("You're not currently in reflection mode.")
        st.stop()

    user_id = st.session_state["user_id"]

    week = int(query_params.get("week", 1))
    session = query_params.get("session", "a")

    st.session_state["week"] = week
    st.session_state["session"] = session

    phase_key = f"reflection_{week}_{session}"
    st.session_state["chat_state"] = phase_key

    phase = get_user_phase(user_id)

    all_goals = get_goals(user_id)
    if not all_goals:
        st.info("You have no goals to reflect on yet.")
        return
    
    # st.write(all_goals[0])
    goal_id = all_goals[0]["id"]
    goal_text = all_goals[0]["goal_text"]

    if reflection_exists(user_id, goal_id, week, session):

        ack_key = f"reflection_ack_w{week}_s{session}"

        if ack_key not in st.session_state:
            if "chat_thread" not in st.session_state:
                st.session_state["chat_thread"] = ChatThread(st.session_state["user_id"])
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": f"✅ You've already submitted a reflection for <b>Week {week}, Session {session.upper()}</b>.<br><br>Thanks!"
            })
            st.session_state[ack_key] = True
            st.rerun()

        col1, col2 = st.columns(2)
        if col1.button("⬅️ Return to Main Menu"):
            set_state(
                chat_state = "menu",
                needs_restore = False
            )
            del st.session_state[ack_key]
            st.rerun()

        if col2.button("⬅️ Return to Prolific"):
            st.stop()

        return

    tasks = get_tasks(goal_id)
    # st.write(tasks)
    if not tasks:
        st.info("You have no tasks for your goal. Add tasks first.")
        return
    
    for t in tasks:
        st.session_state["task_progress"].setdefault(t["id"], 0)
    
    if "reflection_step" not in st.session_state:
        init_reflection_session()
        save_reflection_state()
        set_state(
            reflection_step=0,
            task_progress={t["id"]:0 for t in get_tasks(goal_id)},
            reflection_answers={},
            update_task_idx=0,
            reflection_q_idx=0,
            awaiting_task_edit=False,
            editing_choice=None,
            needs_restore=True
            )
        st.rerun()


        # if "chat_thread" not in st.session_state:
        #     st.session_state["chat_thread"]=[]

        # st.session_state["reflection_step"] = 0
        # st.session_state["task_progress"] = {}
        # st.session_state["reflection_answers"] = {}
        # st.session_state["current_task"] = 0

        # --- PATCH: Early branch if in edit mode ---
    # If user is in the middle of editing or inputting a new task, only show edit UI
    if st.session_state.get("awaiting_task_edit") in [True, "awaiting_input"]:
        idx = st.session_state.get("update_task_idx", 0)
        task = tasks[idx] if idx < len(tasks) else None
        task_id = task["id"] if task else None
        # Suggestion message should appear only once
        if st.session_state["awaiting_task_edit"] == True:
            if "ask_for_edit" not in st.session_state:
                # Only append these once
                reflection_answers = st.session_state.get("reflection_answers", {})
                existing_tasks     = [t["task_text"] for t in tasks]
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
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": "✍️ Please write the new version of this task."
                })
                st.session_state["ask_for_edit"] = True
                save_reflection_state()
                st.rerun()
            # Otherwise, just render input
            else:
                new_text = st.chat_input("Type your updated task here...")
                if new_text:
                    reason = st.session_state.get("editing_choice", "Modified")
                    # Defensive: fallback to "Modified" if not set
                    task = tasks[st.session_state["update_task_idx"]]
                    task_id = task["id"]
                    new_task_id = replace_or_modify_task(goal_id, task_id, new_text, reason)
                    st.session_state["task_progress"][new_task_id] = st.session_state["task_progress"].pop(task_id, 0)
                    st.session_state["chat_thread"].append({
                        "sender": "Assistant",
                        "message": f"✅ Task updated to: '<b>{new_text}</b>'"
                    })
                    st.session_state["chat_thread"].append({
                        "sender": "User",
                        "message": new_text
                    })
                    st.session_state["awaiting_task_edit"] = False
                    st.session_state["editing_choice"] = None
                    st.session_state["update_task_idx"] += 1
                    # Clean ask_for_edit so if user hits reload again, doesn't get stuck
                    if "ask_for_edit" in st.session_state:
                        del st.session_state["ask_for_edit"]

                    save_reflection_state()

                    st.rerun()
            # Prevent other UI from rendering
            return
        elif st.session_state["awaiting_task_edit"] == "awaiting_input":
            # This branch should be unreachable now, but for safety:
            new_text = st.chat_input("Type your updated task here...")
            if new_text:
                reason = st.session_state.get("editing_choice", "Modified")
                task = tasks[st.session_state["update_task_idx"]]
                task_id = task["id"]
                new_task_id = replace_or_modify_task(goal_id, task_id, new_text, reason)
                st.session_state["task_progress"][new_task_id] = st.session_state["task_progress"].pop(task_id, 0)
                st.session_state["chat_thread"].append({
                    "sender": "Assistant",
                    "message": f"✅ Task updated to: '<b>{new_text}</b>'"
                })
                st.session_state["chat_thread"].append({
                    "sender": "User",
                    "message": new_text
                })
                st.session_state["awaiting_task_edit"] = False
                st.session_state["editing_choice"] = None
                st.session_state["update_task_idx"] += 1
                if "ask_for_edit" in st.session_state:
                    del st.session_state["ask_for_edit"]
                save_reflection_state()

                st.rerun()
            return
    # --- END PATCH ---



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
        save_reflection_state()

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
            save_reflection_state()

            st.rerun()

        # 2️⃣ Show side-by-side buttons for the 5 options
        selected = None
        if not st.session_state.get(f"justifying_{task_id}", False):
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
            save_reflection_state()
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

                save_reflection_state()



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
            save_reflection_state()
            st.rerun()

        user_input = st.chat_input("Type your answer here...")
        if user_input:
            st.session_state["chat_thread"].append({"sender": "User", "message": user_input})
            st.session_state["reflection_answers"][key] = user_input
            q_idx += 1
            save_reflection_state()


            if q_idx < len(questions):
                st.session_state["reflection_q_idx"] = q_idx
                save_reflection_state()

                st.rerun()
            else:
                st.session_state["reflection_step"] += 1
                st.session_state["reflection_q_idx"] = 0
                save_reflection_state()

                st.rerun()

    # Goal Alignment Reflection
    elif st.session_state["reflection_step"] == len(tasks) + 2:
        if "ask_alignment" not in st.session_state:
            st.session_state["chat_thread"].append({
                "sender": "Assistant",
                "message": "🧭 Thinking about your tasks and your goal, do you feel your current tasks still <b>match the goal well</b>?<br><br>Feel free to share your thoughts, whether they align well, or if anything feels a bit off."
            })
            st.session_state["ask_alignment"] = True
            save_reflection_state()
            st.rerun()

        user_input = st.chat_input("Type your answer here...")
        if user_input:
            st.session_state["chat_thread"].append({"sender": "User", "message": user_input})
            st.session_state["reflection_answers"]["task_alignment"] = user_input
            st.session_state["reflection_step"] += 1
            save_reflection_state()

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

                save_reflection_state()



                if selected in ["Modify", "Replace"]:
                    st.session_state["awaiting_task_edit"] = True
                    st.session_state["editing_choice"] = selected
                    save_reflection_state()

                    st.rerun()
                else:
                    st.session_state["chat_thread"].append({
                        "sender": "Assistant",
                        "message": "👍 Task kept as is."
                    })
                    st.session_state["update_task_idx"] += 1
                    save_reflection_state()

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
                    st.session_state["editing_choice"] = None
                    st.session_state["update_task_idx"] += 1

                    save_reflection_state()


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
            save_reflection_state()


            st.rerun()

    elif st.session_state["reflection_step"] == len(tasks) + 4:
        task_results = []
        for task in tasks:  
            task_id = task["id"]
            task_text = task["task_text"]
            val = st.session_state["task_progress"].get(task_id, 0)
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
            rating = st.session_state["task_progress"].get(task_id, 0)
            save_reflection_response(reflection_id, task_id=task_id, progress_rating=rating)
            
                
        # Save open-text question answers
        for key, answer in st.session_state["reflection_answers"].items():
            save_reflection_response(reflection_id, answer_key=key, answer_text=answer)

        update_user_phase(user_id, phase + 1)

        active_tasks = get_tasks(goal_id)
        if not active_tasks:
            st.warning("⚠️ You have no active tasks left. Please add new tasks before the next reflection.")
            if st.button("➕ Add Tasks Now"):
                set_state(
                    chat_state = "add_tasks",
                    needs_restore = False
                )
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
            set_state(
                chat_state = "menu",
                needs_restore = False
            )

        for key in list(st.session_state.keys()):
            if (
                key.startswith("reflection_") 
                or key.startswith(("ask_", "justifying_", "justified_"))
                or key in [
                "task_progress", "reflection_answers",
                "update_task_idx", "reflection_q_idx"]
                ):
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
    st.session_state["editing_choice"] = None
