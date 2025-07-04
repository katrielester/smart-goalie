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

    Your task: Revise the goal below to make it more specific, using minimal edits.

    Guidelines:
    - Keep the goal high-level (should take ~2 weeks of effort and can be broken into 2–3 weekly tasks later)
    - Make it more concrete and focused (avoid vague phrases like "do better").
    - Do NOT shrink it into a short-term task or add detailed steps.

    Each revision must be:
    - A single sentence
    - Under 15 words

    Examples:

    Original: Do better in interviews  
    Specific: Improve my interview skills by practicing behavioral questions

    Original: Get healthier  
    Specific: Improve my health by building a consistent exercise routine

    Now revise the goal below:

    [Goal]  
    {goal_text}  
    [/Goal]

    Return only 3 revised versions, numbered like this:
    1. ...
    2. ...
    3. ...
    """
        return smart_wrapper(prompt, goal_text, "specific")

def suggest_measurable_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task: Make the goal more measurable using minimal edits while keeping it high-level.

    Guidelines:
    - Add a way to track progress (e.g., frequency, quantity, or visible milestone).
    - Do NOT turn the goal into a one-time task or a detailed plan.
    - Keep the goal high-level (should take ~2 weeks of effort and can be broken into 2–3 weekly tasks later)
    
    Each version must be:
    - A single sentence
    - Under 15 words

    Examples:

    Original: Learn a new skill  
    Measurable: Learn a new skill by completing progress-based online lessons

    Now revise the goal below:

    [Goal]  
    {goal_text}  
    [/Goal]

    Return only 3 revised versions, numbered like this:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "measurable")

def suggest_achievable_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task: Make the goal more achievable using minimal edits without turning it into a weekly task.

    Guidelines:
    - Keep the goal high-level (should take ~2 weeks of effort and can be broken into 2–3 weekly tasks later)
    - Adjust the scale to fit someone’s current time, energy, or situation.
    - Do NOT break it down into step-by-step tasks.

    Each version must be:
    - A single sentence
    - Under 15 words

    Examples:

    Original: Become fluent in Spanish  
    Achievable: Complete beginner Spanish lessons to start building fluency

    Now revise the goal below:

    [Goal]  
    {goal_text}  
    [/Goal]

    Return only 3 revised versions, numbered like this:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "achievable")

def suggest_relevant_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task: Make the goal more personally meaningful to the person with minimal edits.

    Guidelines:
    - Add a reason the goal matters (e.g. values, priorities, or long-term benefit).
    - Keep the goal high-level (should take ~2 weeks of effort and can be broken into 2–3 weekly tasks later).
    - Do NOT turn it into a personal story or detailed explanation.

    Each version must be:
    - A single sentence
    - Under 15 words

    Examples:

    Original: Learn data entry  
    Relevant: Learn data entry to access flexible online work opportunities

    Now revise the goal below:

    [Goal]  
    {goal_text}  
    [/Goal]

    Return only 3 revised versions, numbered like this:
    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "relevant")

def suggest_timebound_fix(goal_text):
    prompt = f"""
    You are a goal refinement assistant.

    Your task: Add a realistic timeframe to the goal with minimal edits.

    Guidelines:
    - Include a realistic timeframe, schedule, or deadline.
    - Keep the goal high-level (should take ~2 weeks of effort and can be broken into 2–3 weekly tasks later)
    - Do NOT break the goal into smaller steps like one-time tasks or detailed plan.

    Each revision must be:
    - A single sentence
    - Under 15 words

    Examples:

    Original: Improve my typing speed  
    Time-bound: Improve my typing speed over the next 2 weeks

    Now revise the goal below:

    [Goal]  
    {goal_text}  
    [/Goal]

    Return 3 revised versions, numbered like this:
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

# CHECK SMART FEEDBACK
def check_smart_feedback(goal_text, dimension):
    if dimension == "specific":
        prompt = f"""
You are a goal support assistant.

Your task is to give one short, friendly sentence of feedback on how *specific* the goal below is.

Focus only on whether the goal clearly identifies one concrete focus or outcome (not vague like do better or get on track).

Guidelines:
- Do not score or critique.
- Do not give suggestions or rewrite the goal.
- Do not comment on whether it is measurable, achievable, or time-bound.
- Assume the goal should be high-level (to be completed in ~2 weeks and broken into smaller tasks).

Examples of feedback:
- Looks clear and focused, nice work!
- Good start! Try to clarify the outcome a bit more.
- Nice effort! You might want to zoom in on one focus.

[Goal]
{goal_text}
[/Goal]
"""
    
    elif dimension == "measurable":
        prompt = f"""
You are a goal support assistant.

Your task is to give one short, friendly sentence of feedback on how *measurable* the goal below is.

Focus only on whether there's a way to track progress — like frequency, quantity, or visible progress.

Guidelines:
- Do not score or critique.
- Do not suggest revisions or changes.
- Do not comment on whether the goal is specific, achievable, or time-bound.
- Assume the goal should be high-level (about 2 weeks of effort, with smaller tasks later).

Examples of feedback:
- Great, there's a clear way to track progress here.
- Nice! You could add how often or how much to aim for.
- Good start, let's consider adding a simple way to check your progress.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "achievable":
        prompt = f"""
You are a goal support assistant.

Your task is to give one short, friendly sentence of feedback on how *achievable* the goal below is.

Focus only on whether the goal seems realistic within ~2 weeks, given someone's time, energy, and situation.

Guidelines:
- Do not score or criticize.
- Do not offer suggestions or rewrite the goal.
- Do not comment on whether the goal is measurable or specific.
- Assume the goal will be broken into smaller weekly tasks.

Examples of feedback:
- Nice, it looks balanced and doable!
- Solid start, let's make sure it fits your current time and energy.
- This feels meaningful, ust check that it's realistic for 2 weeks.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "relevant":
        prompt = f"""
You are a goal support assistant.

Your task is to give one short, friendly sentence of feedback on how *personally relevant* the goal below is.

Focus only on whether it seems tied to a value, interest, or current priority for the user.

Guidelines:
- Do not score or evaluate.
- Do not give suggestions or assumptions about personal context.
- Do not comment on other SMART traits like measurability or specificity.
- Assume the goal is intended to guide ~2 weeks of effort.

Examples of feedback:
- Looks like a great fit for your current focus. Keep it up!
- Nice goal, want to add why this matters to you?
- You're on the right track! A quick 'why' could add more clarity.

[Goal]
{goal_text}
[/Goal]
"""

    elif dimension == "timebound":
        prompt = f"""
You are a goal support assistant.

Your task is to give one short, friendly sentence of feedback on whether the goal has a clear *timeframe*.

Focus only on whether the goal includes a deadline, schedule, or timeframe that gives it momentum.

Guidelines:
- Do not score or critique.
- Do not suggest edits or rewrites.
- Do not comment on how specific, measurable, or achievable the goal is.
- The timeframe should fit a two-week span, but not be overly rigid or detailed.

Examples of feedback:
- Great! The timeframe gives this goal structure.
- Good start, consider adding when or how long to work on this.
- Looks good! Just make sure it fits your next two weeks.

[Goal]
{goal_text}
[/Goal]
"""
    else:
        return "Invalid SMART dimension."

    return smart_wrapper(prompt.strip(), goal_text, f"check_{dimension}")