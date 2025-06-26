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
    if type_ == "specific":
        return (
            f"1. Clarify and define exactly what you plan to do. e.g., instead of '{goal_text}', say 'Research and outline my topic for the article'\n"
            f"2. Replace general terms with actionable verbs. e.g., 'Draft the first two sections of my article'\n"
            f"3. Add a clear action phrase, e.g., 'Schedule two sessions to focus on writing this week'"
        )
    elif type_ == "measurable":
        return (
            f"1. Add frequency, e.g., '{goal_text}, three times this week'\n"
            f"2. Add quantity, e.g., '{goal_text}, for at least 30 minutes each time'\n"
            f"3. Define success, e.g., 'Complete one full version of the task'"
        )
    elif type_ == "achievable":
        return (
            f"1. Scale it down, e.g., 'Do a first draft' instead of 'Finish the full project'\n"
            f"2. Choose just one focus area, e.g., 'Just research background sources'\n"
            f"3. Limit time, e.g., '{goal_text}, but only for 1 hour per session'"
        )
    elif type_ == "relevant":
        return (
            f"1. Add motivation, e.g., '{goal_text} to prepare for job interviews'\n"
            f"2. Tie to a deadline, e.g., '{goal_text} because the application is due next month'\n"
            f"3. Link to values, e.g., '{goal_text} to improve my skills in something I care about'"
        )
    elif type_ == "timebound":
        return (
            f"1. Add a deadline, e.g., '{goal_text} by Friday'\n"
            f"2. Use a schedule, e.g., '{goal_text} every morning at 9 AM'\n"
            f"3. Set a timeframe, e.g., '{goal_text} for the next 2 weeks'"
        )
    elif type_ == "summary":
        return (
            "This week, you made progress on your goal. Stay consistent and focus on one step at a time. "
            "You're doing great, keep going!"
        )
    elif type_ == "tasks":
        return (
            "1. Break the goal into parts\n"
            "2. Schedule a first step\n"
            "3. Identify one small, specific task to complete by Friday"
        )

    return "No fallback guidance available for this type."

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
You are a supportive goal coach.

Your task is to summarize the user's weekly reflection in a warm and encouraging tone.

1. Keep the summary short (1–2 sentences).
2. Focus on any progress made — even small steps.
3. If the user is struggling, highlight their effort and suggest they keep going.

Reflection:
{reflection_text}

Return only the summary. End with a short positive note (e.g., "See you next time!" or "You’re doing great — keep it up!")
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