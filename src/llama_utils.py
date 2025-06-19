# llama_utils.py

import requests

LLM_API_URL = "https://smart-goalie-llm.onrender.com/generate"

import os

FAKE_MODE = os.getenv("FAKE_MODE", "true").lower() == "true"

def fake_response(goal_text, type_):
    examples = {
        "specific": f"This is an example of a more specific goal based on your input: 'Finish the backend module of my project.' Consider narrowing down your goal like this if it's too broad.",
        "measurable": f"This is an example of a more measurable goal: 'Complete three sections of my code, each with unit tests, by Friday.' Adding numbers and timelines can help track progress.",
        "achievable": f"This is an example of a more achievable goal: 'Finish the login and signup features this week.' Try scaling down if the goal feels overwhelming.",
        "relevant": f"This is an example of a more relevant goal: 'Finish the project to strengthen my programming portfolio.' Adding why it matters to you can boost motivation.",
        "timebound": f"This is an example of a time-bound goal: 'Submit the final version by the end of next week.' Timelines create urgency and accountability.",
        "refine": f"[Goal]Finish the final draft of my project report by next Friday to meet the submission deadline.[/Goal]",
        "summary": f"This week, you made progress on your goal. Stay consistent and focus on one step at a time. You're doing great—keep going!",
        "tasks": "1. Write the project outline\n2. Draft the introduction\n3. Collect feedback on initial draft"
    }
    return examples.get(type_, "This is a placeholder response.")

def smart_wrapper(prompt, goal_text, type_):
    if FAKE_MODE:
        return fake_response(goal_text, type_)
    try:
        response = requests.post(
            LLM_API_URL,
            json={"prompt": prompt.strip(), "max_tokens":256}
        )
        response.raise_for_status()
        return  response.json().get("response","").strip()
    except Exception as e:
        return f"(Error generating response: {e})"

def suggest_specific_fix(goal_text):
    prompt = f"""
You're a friendly goal-setting assistant helping online crowdworkers improve their goals.

Let’s make this goal more **specific**. That means making it clear:
- What exactly do you want to do?
- What task or topic is it about?
- Where or how will it happen?

Only change the goal if it’s too general or vague. Keep the same meaning.

Give **three clearer versions** with different ways to make it more specific. Think in terms of tasks, platforms, or topics.

Format:
1. [Version 1]
2. [Version 2]
3. [Version 3]

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "specific")

def suggest_measurable_fix(goal_text):
    prompt = f"""
You're a friendly goal-setting assistant helping online crowdworkers improve their goals.

Let’s make this goal more **measurable**. That means adding something you can count or track:
- How many?
- How often?
- For how long?
- What will show it’s done?

Only update the goal if it’s missing these details. Keep the meaning the same.

Give **three versions** with different ways to make it measurable. Try numbers, hours, or task counts.

Format:
1. [Version 1]
2. [Version 2]
3. [Version 3]

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "measurable")

def suggest_achievable_fix(goal_text):
    prompt = f"""
You're a friendly goal-setting assistant helping online crowdworkers improve their goals.

Let’s make this goal more **achievable**—something realistic you can actually do with your time, skills, and tools.

If the goal feels too big or difficult to finish in a short time, simplify it just a little. Keep the original idea the same.

Give **three improved versions** that feel doable. Think small wins or first steps.

Format:
1. [Version 1]
2. [Version 2]
3. [Version 3]

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "achievable")

def suggest_relevant_fix(goal_text):
    prompt = f"""
You're a friendly goal-setting assistant helping online crowdworkers improve their goals.

Let’s make this goal more **relevant**. That means showing why it matters to you—maybe for your work, learning, or daily life.

If the goal doesn’t say *why* it’s useful, add a quick reason that fits with the user’s bigger picture.

Give **three versions**, each with a short phrase that makes the goal more meaningful or personal.

Format:
1. [Version 1]
2. [Version 2]
3. [Version 3]

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "relevant")

def suggest_timebound_fix(goal_text):
    prompt = f"""
You are a goal-setting coach. Add a realistic timeframe or deadline to the following goal if it does not already have one.
Keep the user's original intent.
Return only the improved time-bound goal.

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "timebound")

def refine_goal(raw_goal):
    prompt = f"""
Refine the following goal using SMART criteria. Format the output like this:
[Goal]Your SMART goal[/Goal]

Goal: {raw_goal}
"""
    return smart_wrapper(prompt, raw_goal, "refine")

def summarize_reflection(reflection_text):
    prompt = f"""
This is a user's weekly reflection. Summarize their progress and motivate them kindly.

Reflection:
{reflection_text}
"""
    return smart_wrapper(prompt, reflection_text, "summary")

def suggest_tasks_for_goal(goal_text, existing_tasks=None):
    existing_tasks = existing_tasks or []

    existing_list = "\n".join(f"- {task}" for task in existing_tasks) if existing_tasks else "None"

    prompt = f"""
You are a productivity coach. The user has just created the following SMART goal:

Goal:
{goal_text}

They have already added these tasks for this week:
{existing_list}

Now, suggest 3 **new** example tasks they could complete by the end of this week, **excluding anything similar to the existing ones**. Your suggestions should help break down the goal into small, actionable steps.

Only provide the new suggestions in this format:
1. ...
2. ...
3. ...

Make it clear that these are just examples for inspiration.
"""
    return smart_wrapper(prompt, goal_text, "tasks")