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
        "specific": (
            "To make your goal more specific, try clarifying the exact action you plan to take. "
            "For example, instead of saying 'improve', use a verb like 'draft', 'design', or 'research'."
        ),
        "measurable": (
            "To make your goal more measurable, include numbers or frequencies. "
            "Ask yourself: how much? how many times? what does success look like?"
        ),
        "achievable": (
            "To make your goal more achievable, simplify it into a realistic first step. "
            "Break down large ambitions into what you can actually complete this week."
        ),
        "relevant": (
            "To make your goal more relevant, add a brief reason why it matters to you. "
            "This could be related to personal growth, a deadline, or long-term plans."
        ),
        "timebound": (
            "To make your goal more time-bound, add a deadline or timeframe. "
            "You can use phrases like 'by Friday', 'every morning', or 'in two weeks'."
        ),
        "summary": (
            "This week, you made progress on your goal. Stay consistent and focus on one step at a time. "
            "You're doing great—keep going!"
        ),
        "tasks": (
            "Here’s how to break down a goal into tasks: think of 2–3 small, specific actions you can complete this week. "
            "Each task should help move your goal forward in a practical way."
        )
    }
    return examples.get(type_, "No offline guidance available for this type.")

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
        print(f"(Error generating response: {e})")
        return fake_response(goal_text, type_)

def suggest_specific_fix(goal_text):
   prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal more specific with minimal edits.

    A specific goal clearly describes the action being taken, without turning it into a single small task.

    Example:
    Original: Improve my writing
    Specific: Make progress on my article draft to improve my writing

    Now improve the goal below by making it more specific.

    [Goal]
    {goal_text}
    [/Goal]

    Return 3 lightly edited versions:
    1. ...
    2. ...
    3. ...
    """
   return smart_wrapper(prompt, goal_text, "specific")

def suggest_measurable_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal more measurable with minimal edits.

    A measurable goal includes a quantity or frequency that allows progress to be tracked, while still describing a full goal.

    Example:
    Original: Improve my writing
    Measurable: Finish one complete article draft this week to improve my writing

    Now improve the goal below by making it more measurable.

    [Goal]
    {goal_text}
    [/Goal]

    Return 3 lightly edited versions:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "measurable")

def suggest_achievable_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal more achievable with minimal edits.

    An achievable goal is realistic and can be completed with current time and resources, while still remaining a meaningful weekly goal.

    Example:
    Original: Publish multiple blog posts this week
    Achievable: Draft one blog post this week with the goal of publishing it soon

    Now improve the goal below by making it more achievable.

    [Goal]
    {goal_text}
    [/Goal]

    Return 3 lightly edited versions:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "achievable")

def suggest_relevant_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal more relevant with minimal edits.

    A relevant goal includes a personal reason or motivation that connects the action to a meaningful outcome.

    Example:
    Original: Practice coding every day
    Relevant: Practice coding every day to prepare for job applications

    Now improve the goal below by making it more relevant.

    [Goal]
    {goal_text}
    [/Goal]

    Return 3 lightly edited versions:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "relevant")

def suggest_timebound_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal more time-bound with minimal edits.

    A time-bound goal includes a deadline, timeframe, or schedule that creates urgency and structure.

    Example:
    Original: Organize my notes
    Time-bound: Organize my notes by the end of the week

    Now improve the goal below by making it more time-bound.

    [Goal]
    {goal_text}
    [/Goal]

    Return 3 lightly edited versions:
    1. ...
    2. ...
    3. ...
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
    You help users break down their goals into weekly tasks.

    The user has set the following SMART goal:
    [Goal]
    {goal_text}
    [/Goal]

    These tasks have already been added:
    {existing_list}

    Suggest 3 new example tasks they could complete by the end of this week. Do not repeat or closely match existing tasks. Focus on small, concrete actions that help move the goal forward.

    Only output the 3 new tasks in this format:
    1. ...
    2. ...
    3. ...

    These are just suggestions for inspiration.
    """
    return smart_wrapper(prompt, goal_text, "tasks")