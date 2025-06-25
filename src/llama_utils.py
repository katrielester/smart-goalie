# llama_utils.py

import requests

# LLM_API_URL = "http://213.173.102.150:11434/api/generate"
LLM_API_URL = "https://498spxjyhd6q36-11434.proxy.runpod.net/api/generate"

import os

FAKE_MODE = os.getenv("FAKE_MODE", "true").lower() == "true"

def extract_goal_variants(response_text):
    lines = response_text.strip().splitlines()
    variants = [line.strip() for line in lines if line.strip().startswith(("1.", "2.", "3."))]
    return "\n".join(variants)

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
            json={
                "model": "mistral",
                "prompt": prompt.strip(),
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"(Error generating response: {e})"

def suggest_specific_fix(goal_text):
    prompt = f"""
You are a goal-refinement assistant.

Your task is to rewrite the following goal to make it **more specific** — by clarifying the exact action or task, without changing its scope or adding measurement, time, or motivation.

DO:
- Replace vague words like "more", "better", "regularly" with concrete action verbs
- Keep the goal's intent intact
- Focus only on what the user will do

DO NOT:
- Add numbers, frequency, or timelines (that's for later steps)
- Add motivational phrases or explanations

Return exactly 3 specific versions in this format:
1. ...
2. ...
3. ...

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "specific")

def suggest_measurable_fix(goal_text):
    prompt = f"""
You are a goal-setting assistant.

Your task is to rewrite the following goal to make it **more measurable** — by adding numbers, durations, frequencies, or specific outcomes that can be tracked.

DO:
- Add measurable terms (e.g. how many, how often, how long)
- Keep the action and meaning intact

DO NOT:
- Add timeframes (like "by next week")
- Add motivation or purpose

Return exactly 3 versions in this format:
1. ...
2. ...
3. ...

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "measurable")

def suggest_achievable_fix(goal_text):
    prompt = f"""
You are a goal-setting assistant.

Your task is to rewrite the following goal to make it **more achievable** — by adjusting it into a smaller, realistic first step that can be done with current resources and constraints.

DO:
- Keep the intent the same
- Simplify or reduce the scope to something doable soon

DO NOT:
- Add measurements or timelines
- Use vague phrases like "try to"

Return exactly 3 versions in this format:
1. ...
2. ...
3. ...

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "achievable")

def suggest_relevant_fix(goal_text):
    prompt = f"""
You are a goal-setting assistant.

Your task is to rewrite the following goal to make it **more relevant** — by adding a personal reason or motivation that connects it to something meaningful.

DO:
- Add a phrase like "to improve my health", "to reduce stress", or "for my long-term goals"
- Keep the rest of the goal focused and unchanged

DO NOT:
- Add numbers, deadlines, or how-to steps
- Add general advice

Return exactly 3 versions in this format:
1. ...
2. ...
3. ...

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "relevant")

def suggest_timebound_fix(goal_text):
    prompt = f"""
You are a goal-setting assistant.

Your task is to rewrite the following goal to make it **time-bound** — by adding a clear deadline, duration, or recurring schedule.

DO:
- Add time markers (e.g., "by the end of the week", "in 2 weeks", "every morning")
- Keep the rest of the goal intact

DO NOT:
- Change what the goal is
- Add motivation or measurement

Return exactly 3 versions in this format:
1. ...
2. ...
3. ...

Goal: {goal_text}
"""
    return smart_wrapper(prompt, goal_text, "timebound")

# def refine_goal(raw_goal):
#     prompt = f"""

# Wrap your output in [Goal]...[/Goal] tags.

# Goal: {raw_goal}
# """
#     return smart_wrapper(prompt, raw_goal, "refine")

def summarize_reflection(reflection_text):
    prompt = f"""
Summarize this weekly reflection in 1–2 sentences.

Keep it encouraging and focused on progress, even if small.

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