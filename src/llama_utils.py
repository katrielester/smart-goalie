# llama_utils.py

import requests, re

# LLM_API_URL = "http://213.173.102.150:11434/api/generate"
LLM_API_URL = "https://498spxjyhd6q36-11434.proxy.runpod.net/api/generate"

import os

FAKE_MODE = False
# FAKE_MODE = os.getenv("FAKE_MODE", "true").lower() == "true"

def extract_goal_variants(response_text):
    parts = re.split(r"<br\s*/?>", response_text)
    variants = [p.strip() for p in parts if p.strip().startswith(("1.","2.","3."))]
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
            f"1. Break '{goal_text}' into smaller, manageable parts<br>"
            "2. Schedule your first step for this week<br>"
            "3. Pick one simple, concrete action to complete by Friday"
        )
    elif type_ == "check_specific":
        return "Good start! Try to clarify the outcome a bit more."

    elif type_ == "check_measurable":
        return "Nice! You could add how often or how much to aim for."

    elif type_ == "check_achievable":
        return "Solid start, let's make sure it fits your current time and energy."

    elif type_ == "check_relevant":
        return "Nice goal, want to add why this matters to you?"

    elif type_ == "check_timebound":
        return "Good start, consider adding when or how long to work on this."
    return "No fallback guidance available for this type."

def smart_wrapper(prompt, goal_text, type_):
    if FAKE_MODE:
        return fake_response(goal_text, type_)
    
    temp = 0.3 if type_.startswith("check_") else 0.7

    if type_ in ("specific", "measurable", "achievable", "relevant", "timebound"):
        # single‐sentence suggestions, under 12 words,  36 tokens max
        max_toks = 25
    elif type_.startswith("check_"):
        # feedback
        max_toks = 60
    else:
        # summaries, tasks, etc.
        max_toks = 150

    payload = {
        "model":       "mistral",
        "prompt":      prompt.strip(),
        "stream":      False,
        "temperature": temp,
        "max_tokens":  max_toks,
        "stop":        ["\n\n"]
    }

    try:
        response = requests.post(LLM_API_URL, json=payload, timeout=60)
        response.raise_for_status()
    except requests.HTTPError as he:
        print("❌ LLM HTTPError:", he, "\nResponse body:", response.text)
        return fake_response(goal_text, type_)
    except Exception as e:
        print("❌ LLM request failed:", e)
        return fake_response(goal_text, type_)

    text = response.json().get("response", "").strip()
    # Convert any internal newlines to HTML breaks for your app:
    return text.replace("\n", "<br>")

def suggest_specific_fix(goal_text):
    prompt = f"""
Revise the goal to make it more specific.

- Keep it high level, not a task or step
- Keep it short (under 12 words)
- Should be breakable into 2 to 3 subtasks
- Do not phrase it like a task

Example:
Not good: Be more productive
Better: Improve focus during work hours

Goal:
{goal_text}

Return only 3 revised versions:
1. ...
2. ...
3. ...
"""
    return smart_wrapper(prompt, goal_text, "specific")

def suggest_measurable_fix(goal_text):
    prompt = f"""
Revise the goal to make it more measurable.

- Include a way to track progress
- Do not use numbers or percentages
- Keep it goal level, not a performance metric
- Keep it short (under 12 words)

Example:
Not good: Complete five interviews per week
Better: Track job interview preparation regularly

Goal:
{goal_text}

Return only 3 revised versions:
1. ...
2. ...
3. ...
"""
    return smart_wrapper(prompt, goal_text, "measurable")

def suggest_achievable_fix(goal_text):
    prompt = f"""
Revise the goal to make it more achievable.

- Keep it doable within 2 weeks
- Stay at the goal level (not tasks)
- Keep it short (under 12 words)

Example: Build a routine for consistent time planning

Goal:
{goal_text}

Return only 3 revised versions:
1. ...
2. ...
3. ...
"""
    return smart_wrapper(prompt, goal_text, "achievable")

def suggest_relevant_fix(goal_text):
    prompt = f"""
Revise the goal to make it more personally relevant.

- Add a short reason or benefit (in brackets is okay)
- Keep it short (under 12 words)
- Phrase it as a high-level goal

Example: Strengthen planning skills (to reduce daily stress)

Goal:
{goal_text}

Return only 3 revised versions:
1. ...
2. ...
3. ...
"""
    return smart_wrapper(prompt, goal_text, "relevant")

def suggest_timebound_fix(goal_text):
    prompt = f"""
Revise the goal to make it more time-bound.

- Add a timeframe (e.g., 2 weeks, end of month), but not a specific date
- Keep it high-level (not a checklist item)
- Keep it under 12 words

Example: Improve work planning by the end of the month

Goal:
{goal_text}

Return only 3 revised versions:
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
2. Focus on any progress made, even small steps.
3. If the user is struggling, highlight their effort and suggest they keep going.
4. Paraphrase rather than quote the user's exact words.

Reflection:
{reflection_text}

Return only the summary. End with a short positive note (e.g., "See you next time!" or "You’re doing great — keep it up!")
"""
    return smart_wrapper(prompt, reflection_text, "summary")

def summarize_goal_reflection(goal, alignment_answer, confidence_answer):
    prompt = f"""
You are a supportive progress coach helping users reflect on their SMART goal pursuit.

Based on the user's input below, summarize their reflection in a warm, friendly tone. 

1. Keep it short: 1–2 sentences max.
2. Mention whether their current tasks still align with the goal.
3. Acknowledge if they feel confident or uncertain.
4. End with encouragement like “Keep it up!” or “You’ve got this!”

SMART Goal: {goal}

Do the tasks still align with the goal?  
User: {alignment_answer}

How confident do they feel about continuing with this goal?  
User: {confidence_answer}

Now write the summary:
"""
    return smart_wrapper(prompt.strip(), alignment_answer + confidence_answer, "summary")

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
    - Each task must be concise, under 12 words
    - Be achievable within one week
    - Include a time, quantity, or duration if relevant

    Avoid:
    - Rambling or multiple steps per task
    - Evaluation-heavy instructions
    - Repeating existing tasks
    - Generic phrasing like "try to..." or "maybe"

    Respond with only the 3 tasks, in this format:

    1. ...
    2. ...
    3. ...
    """
    return smart_wrapper(prompt, goal_text, "tasks")

def suggest_tasks_with_context(goal_text, reflection_answers=None, existing_tasks=None):
    reflection_context = ""
    if reflection_answers:
        for k, v in reflection_answers.items():
            reflection_context += f"{k.upper()}: {v}\n"

    existing_tasks = existing_tasks or []
    existing_list = "<br>".join(f"- {task}" for task in existing_tasks) if existing_tasks else "None"

    prompt = f"""
You help users break down SMART goals into short, concrete weekly tasks.

The user's SMART goal is:
[Goal]
{goal_text}
[/Goal]

Reflection context (to inspire useful ideas):
{reflection_context.strip()}

Tasks already added (do not repeat or rephrase these):
{existing_list}

Suggest exactly 3 new weekly tasks. Each task should:
- Be actionable and specific (describe the exact action)
- Fit into a single sentence, under 12 words
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
- Never rewrite the goal. Feedback should not suggest how to fix it.
- Do not comment on whether it is measurable, achievable, or time-bound.
- Assume the goal should be high-level (to be completed in ~2 weeks and broken into smaller tasks).
- Keep your feedback short and friendly (1–2 sentences and under 20 words).
- Avoid hedging or passive phrases (like “could be”, “might want to”).

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
- Never rewrite the goal. Feedback should not suggest how to fix it.
- Do not comment on whether the goal is specific, achievable, or time-bound.
- Assume the goal should be high-level (about 2 weeks of effort, with smaller tasks later).
- Keep your feedback short and friendly (1–2 sentences and under 20 words).
- Avoid hedging or passive phrases (like “could be”, “might want to”).

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
- Never rewrite the goal. Feedback should not suggest how to fix it.
- Do not comment on whether the goal is measurable or specific.
- Assume the goal will be broken into smaller weekly tasks.
- Keep your feedback short and friendly (1–2 sentences and under 20 words).
- Avoid hedging or passive phrases (like “could be”, “might want to”).

Examples of feedback:
- Nice, it looks balanced and doable!
- Solid start, let's make sure it fits your current time and energy.
- This feels meaningful, just check that it's realistic for 2 weeks.

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
- Never rewrite the goal. Feedback should not suggest how to fix it.
- Never make assumptions about personal context.
- Do not comment on other SMART traits like measurability or specificity.
- Assume the goal is intended to guide ~2 weeks of effort.
- Keep your feedback short and friendly (1–2 sentences and under 20 words).
- Avoid hedging or passive phrases (like “could be”, “might want to”).

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
- Never rewrite the goal. Feedback should not suggest how to fix it.
- Do not comment on how specific, measurable, or achievable the goal is.
- The timeframe should fit a two-week span, but not be overly rigid or detailed.
- Keep your feedback short and friendly (1–2 sentences and under 20 words).
- Avoid hedging or passive phrases (like “could be”, “might want to”).

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