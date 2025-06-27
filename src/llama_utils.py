# llama_utils.py

import requests

# LLM_API_URL = "http://213.173.102.150:11434/api/generate"
LLM_API_URL = "https://498spxjyhd6q36-11434.proxy.runpod.net/api/generate"

import os

FAKE_MODE = os.getenv("FAKE_MODE", "true").lower() == "true"

def extract_goal_variants(response_text):
    lines = response_text.strip().splitlines()
    variants = [line.strip() for line in lines if line.strip().startswith(("1.", "2.", "3."))]
    return "<br>".join(variants)

def fake_response(goal_text, type_):
    if type_ == "specific":
        return (
            f"1. Clarify and define exactly what you plan to do. e.g., instead of '{goal_text}', say 'Research and outline my topic for the article'<br>"
            f"2. Replace general terms with actionable verbs. e.g., 'Draft the first two sections of my article'<br>"
            f"3. Add a clear action phrase, e.g., 'Schedule two sessions to focus on writing this week'"
        )
    elif type_ == "measurable":
        return (
            f"1. Add frequency, e.g., '{goal_text}, three times this week'<br>"
            f"2. Add quantity, e.g., '{goal_text}, for at least 30 minutes each time'<br>"
            f"3. Define success, e.g., 'Complete one full version of the task'"
        )
    elif type_ == "achievable":
        return (
            f"1. Scale it down, e.g., 'Do a first draft' instead of 'Finish the full project'<br>"
            f"2. Choose just one focus area, e.g., 'Just research background sources'<br>"
            f"3. Limit time, e.g., '{goal_text}, but only for 1 hour per session'"
        )
    elif type_ == "relevant":
        return (
            f"1. Add motivation, e.g., '{goal_text} to prepare for job interviews'<br>"
            f"2. Tie to a deadline, e.g., '{goal_text} because the application is due next month'<br>"
            f"3. Link to values, e.g., '{goal_text} to improve my skills in something I care about'"
        )
    elif type_ == "timebound":
        return (
            f"1. Add a deadline, e.g., '{goal_text} by Friday'<br>"
            f"2. Use a schedule, e.g., '{goal_text} every morning at 9 AM'<br>"
            f"3. Set a timeframe, e.g., '{goal_text} for the next 2 weeks'"
        )
    elif type_ == "summary":
        return (
            "This week, you made progress on your goal. Stay consistent and focus on one step at a time. "
            "You're doing great, keep going!"
        )
    elif type_ == "tasks":
        return (
            "1. Break the goal into parts<br>"
            "2. Schedule a first step<br>"
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

    Your task is to make the following goal more specific with minimal edits.

    A specific goal describes one clear outcome or focus area — not something vague like "do better" or "be more consistent." Avoid bundling multiple actions.

    Examples:
    Original: Do better in interviews  
    Specific: Improve my interview skills by practicing behavioral questions

    Original: Get healthier  
    Specific: Improve my health by building a consistent walking routine

    Now revise the goal below to be more specific. Suggest 3 lightly edited versions:

    [Goal]  
    {goal_text}  
    [/Goal]

    Return them in this format:
    1. ...
    2. ...
    3. ...
    """
        return smart_wrapper(prompt, goal_text, "specific")

def suggest_measurable_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal more measurable with minimal edits.

    A measurable goal includes a way to track progress — like a number, frequency, or result — while still being a high-level goal that will take around 2 weeks of effort.

    Example:
    Original: Learn a new skill  
    Measurable: Complete a free transcription course to learn a new skill

    Now improve the goal below by making it more measurable (without turning it into a one-off task).

    [Goal]  
    {goal_text}  
    [/Goal]

    Please return 3 lightly edited versions, numbered in this format:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "measurable")

def suggest_achievable_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal more achievable with minimal edits.

    An achievable goal should still feel meaningful and take at least 2 weeks to make progress — but it should fit the person’s current time, energy, and situation.

    Example:  
    Original: Become fluent in Spanish  
    Achievable: Complete 10 beginner Spanish lessons to start building fluency

    Now improve the goal below by making it more achievable (without shrinking it into a short weekly task).

    [Goal]  
    {goal_text}  
    [/Goal]

    Please return 3 lightly edited versions, numbered in this format:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "achievable")

def suggest_relevant_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to make the goal feel more personally meaningful with minimal edits.

    A relevant goal includes a reason it matters to the person — something tied to their values, interests, goals, or current priorities.

    Example:  
    Original: Learn data entry  
    Relevant: Learn data entry to access more flexible online jobs

    Now improve the goal below by making it more personally relevant.

    [Goal]  
    {goal_text}  
    [/Goal]

    Please return 3 lightly edited versions, numbered in this format:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "relevant")

def suggest_timebound_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task is to add a clear timeframe to the goal with minimal edits.

    A time-bound goal includes a deadline, schedule, or timeframe — something realistic that gives the goal structure and momentum over 2+ weeks.

    Example:  
    Original: Improve my typing speed  
    Time-bound: Improve my typing speed by completing a 2-week typing bootcamp

    Now improve the goal below by making it more time-bound.

    [Goal]  
    {goal_text}  
    [/Goal]

    Please return 3 lightly edited versions, numbered in this format:
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
    existing_list = "<br>".join(f"- {task}" for task in existing_tasks) if existing_tasks else "None"

    prompt = f"""
    You help users break down SMART goals into short, concrete weekly tasks.

    The user's SMART goal is:
    [Goal]
    {goal_text}
    [/Goal]

    Tasks already added (do not repeat or rephrase these):
    {existing_list}

    Suggest exactly 3 new weekly tasks. Each task should:
    - Be actionable and specific (describe the exact action)
    - Fit into a single sentence, under 15 words
    - Be achievable within one week
    - Include a time, quantity, or duration if relevant

    Avoid:
    - Rambling or multiple steps per task
    - Repeating existing tasks
    - Generic phrasing like "try to..." or "maybe"

    Respond with only the 3 tasks, in this format:

    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "tasks")