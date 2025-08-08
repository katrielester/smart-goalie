# llama_utils.py

import requests, re
from logger import setup_logger


# LLM_API_URL = "http://213.173.102.150:11434/api/generate"
LLM_API_URL = "https://498spxjyhd6q36-11434.proxy.runpod.net/api/generate"

import os

FAKE_MODE = False
logger = setup_logger()
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
            f"1. Add a deadline, e.g., '{goal_text} every 2 days'<br>"
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
        logger.error(
            "❌ LLM HTTPError: %s; response body: %s",
            he,
            response.text,
            exc_info=True
            )
        return fake_response(goal_text, type_)
    except Exception as e:
        logger.error(
            "❌ LLM request failed",
            exc_info=True
            )
        return fake_response(goal_text, type_)

    text = response.json().get("response", "").strip()
    # Convert any internal newlines to HTML breaks for your app:
    return text.replace("\n", "<br>")

def suggest_specific_fix(goal_text):
    prompt = f"""
Revise the goal to make it more specific with minimal edits.

RULE: Preserve the original wording, change no more than 3 words.

- Use simple language, avoid buzzwords like streamline or optimize.
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
Revise the goal to make it more measurable with minimal edits.

RULE: Preserve the original wording, change no more than 3 words.

- Use simple language, avoid buzzwords like streamline or optimize.
- Include a way to track progress
- Do not use numbers or percentages
- Keep it goal level, not a performance metric
- Keep it short (under 12 words)
- Only make small adjustments.
- Keep the original meaning and structure as much as possible.
- Avoid rewriting the entire goal.

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
Revise the goal to make it more achievablewith minimal edits.

RULE: Preserve the original wording, change no more than 3 words.

- Use simple language, avoid buzzwords like streamline or optimize.
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
Revise the goal to make it more personally relevant with minimal edits.

RULE: Preserve the original wording, change no more than 3 words.

- Use simple language, avoid buzzwords like streamline or optimize.
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
Revise the goal to make it more time-bound with minimal edits.

RULE: Preserve the original wording, change no more than 3 words.

- Use simple language, avoid buzzwords like streamline or optimize.
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
    - Do not mention name of day like "by Monday", instead use each week or every 3 days
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
- Do not mention name of day like "by Monday", instead use each week or every 3 days

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

RULE: Give ONE short, friendly sentence evaluating how specific the goal is, without rewriting it.

Focus only on whether the goal names a single clear outcome.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging

Examples:
- Great focus, this goal names a clear outcome!
- This goal feels broad, consider honing in on one main result.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "measurable":
        prompt = f"""
You are a goal support assistant.

RULE: Give ONE short, friendly sentence evaluating how measurable the goal is, without rewriting it.

Focus only on whether there is a clear way to track progress.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging

Examples:
- Good job, this goal includes a clear progress indicator!
- Almost there, adding a way to measure success will make it better!

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "achievable":
        prompt = f"""
You are a goal support assistant.

RULE: Give ONE short, friendly sentence evaluating how achievable the goal is, without rewriting it.

Focus only on whether the goal seems realistic for ~2 weeks’ effort.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging

Examples:
- Nice, this goal seems doable within two weeks!
- Looks good! Just make sure it fits your energy and schedule.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "relevant":
        prompt = f"""
You are a goal support assistant.

RULE: Give ONE short, friendly sentence evaluating how relevant the goal is, without rewriting it.

Focus only on whether the goal aligns with personal values or priorities.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging

Examples:
- Excellent, this goal aligns with what matters to you!
- Consider adding what personal value this goal connects to.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "timebound":
        prompt = f"""
You are a goal support assistant.

RULE: Give ONE short, friendly sentence evaluating how time-bound the goal is, without rewriting it.

Focus only on whether the goal includes a deadline or timeframe.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging

Examples:
- Great, this goal has a clear timeframe!
- Good start, adding a deadline would give this goal more structure.

[Goal]
{goal_text}
[/Goal]
"""
    else:
        return "Invalid SMART dimension."

    return smart_wrapper(prompt.strip(), goal_text, f"check_{dimension}")
