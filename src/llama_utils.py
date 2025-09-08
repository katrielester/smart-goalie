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
            f"- Clarify and define exactly what you plan to do. e.g., instead of '{goal_text}', say 'Research and outline my topic for the article'<br>"
            f"- Replace general terms with actionable verbs. e.g., 'Draft the first two sections of my article'<br>"
            f"- Add a clear action phrase, e.g., 'Schedule two sessions to focus on writing this week'"
        )
    elif type_ == "measurable":
        return (
            f"- Add frequency, e.g., '{goal_text}, three times this week'<br>"
            f"- Add quantity, e.g., '{goal_text}, for at least 30 minutes each time'<br>"
            f"- Define success, e.g., 'Complete one full version of the task'"
        )
    elif type_ == "achievable":
        return (
            f"- Scale it down, e.g., 'Do a first draft' instead of 'Finish the full project'<br>"
            f"- Choose just one focus area, e.g., 'Just research background sources'<br>"
            f"- Limit time, e.g., '{goal_text}, for 1 hour per session'"
        )
    elif type_ == "relevant":
        return (
            f"- Add motivation, e.g., '{goal_text} to prepare for job interviews'<br>"
            f"- Tie to a deadline, e.g., '{goal_text} because the application is due next month'<br>"
            f"- Link to values, e.g., '{goal_text} to improve my skills in something I care about'"
        )
    elif type_ == "timebound":
        return (
            f"- Add a deadline, e.g., '{goal_text} every 2 days'<br>"
            f"- Use a schedule, e.g., '{goal_text} every morning at 9 AM'<br>"
            f"- Set a timeframe, e.g., '{goal_text} for the next 2 weeks'"
        )
    elif type_ == "summary":
        return (
            "NOLLM"
        )
    elif type_ == "tasks":
        return (
            f"- Break '{goal_text}' into smaller, manageable parts<br>"
            "- Schedule your first step for this week<br>"
            "- Pick one simple, concrete action to complete by Friday"
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
    
    elif type_ == "preview":
        return "NOLLM"
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
- Keep it high level, not a simple task or step 
- Keep it short (under 12 words)
- Should be breakable into 3 to 4 subtasks
- Do not phrase it like a task

Example:
Not good: Learn new job skills
Better: Complete a beginner Python programming course

Goal:
{goal_text}

Return only 3 revised versions:
- ...
- ...
- ...
"""
    return smart_wrapper(prompt, goal_text, "specific")

def suggest_measurable_fix(goal_text):
    prompt = f"""
Revise the goal to make it more measurable with minimal edits by adding a weekly milestone to it.

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
Good: I want to finish a online programming course.
Better: I want to finish a online programming course by completing at least 3 modules each week.

Goal:
{goal_text}

Return only 3 revised versions:
- ...
- ...
- ...
"""
    return smart_wrapper(prompt, goal_text, "measurable")

def suggest_achievable_fix(goal_text):
    prompt = f"""
Revise the goal to make it more achievable within 2 weeks with minimal edits. Make the scope smaller or in smaller increments.

RULE: Preserve the original wording, change no more than 3 words.

- Use simple language, avoid buzzwords like streamline or optimize.
- Keep it doable within 2 weeks
- Stay at the goal level (not tasks)
- Keep it short (under 12 words)

Not good: Learn Spanish
Better: Complete beginner Spanish course

Goal:
{goal_text}

Return only 3 revised versions:
- ...
- ...
- ...
"""
    return smart_wrapper(prompt, goal_text, "achievable")

def suggest_relevant_fix(goal_text):
    prompt = f"""
Revise the goal to make it more personally relevant with minimal edits.

RULE: Preserve the original wording, change no more than 3 words, just add suggestions of how the goal might be personally relevant to the person.

- Use simple language, avoid buzzwords like streamline or optimize.
- Add a short reason or benefit (in brackets is okay)
- Keep it short (under 12 words)
- Phrase it as a high-level goal

Example: 
- Complete a beginner Spanish course, so I can speak to my Spanish-speaking family.

Goal:
{goal_text}

Return only 3 revised versions:
- ...
- ...
- ...
"""
    return smart_wrapper(prompt, goal_text, "relevant")

def suggest_timebound_fix(goal_text):
    prompt = f"""
Revise the goal to make it more time-bound with minimal edits by adding a timeframe.

RULE: Preserve the original wording, change no more than 3 words.

- Use simple language, avoid buzzwords like streamline or optimize.
- Add a timeframe (e.g., 2 weeks, end of month), but not a specific date
- Keep it high-level (not a checklist item)
- Keep it under 12 words

Example: Finish writing my thesis by the end of the month.

Goal:
{goal_text}

Return only 3 revised versions:
- ...
- ...
- ...
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

1. Keep the summary short (1-2 sentences).
2. Focus on any progress made, even small steps.
3. If the user is struggling, highlight their effort and suggest they keep going.
4. Paraphrase rather than quote the user's exact words.

Reflection:
{reflection_text}

Return only the summary. End with a short positive note (e.g., "See you next time!" or "You're doing great,  keep it up!")
"""
    return smart_wrapper(prompt, reflection_text, "summary")


def summarize_goal_reflection(goal, alignment_answer, confidence_answer):
    prompt = f"""
You are a supportive progress coach helping users reflect on their SMART goal pursuit.

Based on the user's input below, summarize their reflection in a warm, friendly tone. 

1. Keep it short: 1-2 sentences max.
2. Mention whether their current tasks still align with the goal.
3. Acknowledge if they feel confident or uncertain.
4. End with encouragement like “Keep it up!” or “You've got this!”

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
    You help users break down a SMART goal into short, concrete weekly tasks.

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

def suggest_tasks_with_context(
    goal_text,
    reflection_answers=None,
    existing_tasks=None,
    edit_mode=None,      # "modify" | "replace" | None
    last_task=None,      # text of the task being edited (if any)
    count=3              # how many suggestions to ask for
):

    ra = reflection_answers or {}

    # --- Pull the most helpful bits from reflection answers (optional keys) ---
    def _grab(label, key):
        v = ra.get(key)
        return f"- {label}: {v.strip()}" if isinstance(v, str) and v.strip() else None

    highlights = list(filter(None, [
        _grab("Keep doing",        "now_what"),
        _grab("What helped",       "what"),
        _grab("Plan if obstacle",  "plan"),
        _grab("Obstacle",          "obstacle"),
        _grab("Task fit for next week", "task_alignment"),
    ]))

    # Add up to 2 quick per-task notes (from justification_*), if present
    justs = [
        v.strip() for k, v in ra.items()
        if isinstance(k, str) and k.startswith("justification_")
        and isinstance(v, str) and v.strip()
    ][:2]
    for j in justs:
        highlights.append(f"- Note: {j}")

    reflection_context = "\n".join(highlights) if highlights else "None"

    # --- Tasks we must NOT repeat/rephrase ---
    existing_tasks = existing_tasks or []
    existing_list = "\n".join(f"- {t}" for t in existing_tasks) if existing_tasks else "None"

    # --- Edit mode block (optional) ---
    mode_block = ""
    em = (edit_mode or "").strip().lower()
    lt = (last_task or "").strip()

    if em == "modify" and lt:
        mode_block = f"""
You are EDITING an existing weekly task.

[Current task]
{lt}
[/Current task]

Suggest exactly 3 weekly tasks with the following rules:
- Keep the same intent.
- Offer clearer wording and/or smaller scope.
- Include ONE easier/smaller variant among the suggestions.
"""
    elif em == "replace" and lt:
        mode_block = f"""
You are REPLACING an old weekly task.

[Old task]
{lt}
[/Old task]

Suggest exactly 3 weekly tasks with the following rules:
- Do NOT rephrase or reuse this old task.
"""

    # --- Build the prompt (simple, Mistral-friendly) ---
    prompt = f"""
You help users break down a SMART goal into small, concrete weekly tasks.

The user's SMART goal is:
[Goal]
{goal_text}
[/Goal]

{mode_block}
- Are specific, one clear action per line
- Under 12 words
- Achievable within one week
- Include time/quantity/duration when useful using plain text (e.g., "for 3 days", "200 words")
- Do NOT mention weekdays or weekends or any day of the week
- Do NOT use dashes to add timing
- Do NOT use parentheses (), brackets [] or braces {{}} anywhere
- Do NOT include labels or headers (no "Note", "Workaround", "Continue")
- Do NOT copy labels from the context; use the content only
- No colons ":" and no extra commentary

Tasks already added (do NOT repeat or rephrase these):
{existing_list}

Notes from the user's reflection (you may use the ideas but never copy labels like "Note:"):
{reflection_context}

Avoid:
- Rambling or multiple steps per task
- Repeating existing tasks
- Generic phrasing like "try to..." or "maybe"

Respond with only the 3 tasks, exactly in this format:
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

RULE: Give one short, friendly sentence evaluating how specific the goal is, without rewriting it.

Focus only on whether the goal names a single clear outcome.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging
- Use the tone of these samples, but write your own sentence.

Stylistic samples:
- Great focus, this goal names a clear outcome!
- This goal feels broad, consider honing in on one main result.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "measurable":
        prompt = f"""
You are a goal support assistant.

RULE: Give one short, friendly sentence evaluating how measurable the goal is, without rewriting it.

Focus only on whether there is a clear way to track progress.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging
- Use the tone of these samples, but write your own sentence.

Stylistic samples:
- Good job, this goal includes a clear progress indicator!
- Almost there, consider adding a way to measure success.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "achievable":
        prompt = f"""
You are a goal support assistant.

RULE: Give one short, friendly sentence evaluating how achievable the goal is, without rewriting it.

Focus only on whether the goal seems realistic for around 2 weeks of effort.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging
- Use the tone of these samples, but write your own sentence.

Stylistic samples:
- Nice, this goal seems doable within two weeks!
- Looks good! Make sure it fits your energy.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "relevant":
        prompt = f"""
You are a goal support assistant.

RULE: Give one short, friendly sentence evaluating if the goal states why it is relevant, without rewriting it.

Focus only on whether the goal aligns with personal values or priorities.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging
- Use the tone of these samples, but write your own sentence.

Stylistic samples:
- Excellent, this goal aligns with what matters to you!
- Good start, adding why you want to achieve this would make it even better!
- Feels a bit generic; adding your “why” could help.

[Goal]
{goal_text}
[/Goal]
"""
    elif dimension == "timebound":
        prompt = f"""
You are a goal support assistant.

RULE: Give one short, friendly sentence evaluating how time-bound the goal is, without rewriting it.

Focus only on whether the goal includes a deadline or timeframe.

Guidelines:
- Do not suggest improvements
- Do not rewrite the goal
- Keep feedback under 15 words
- Be warm and encouraging
- Use the tone of these samples, but write your own sentence.

Stylistic samples:
- Great, this goal has a clear timeframe!
- Missing a deadline; adding one will help.

[Goal]
{goal_text}
[/Goal]
"""
    else:
        return "Invalid SMART dimension."

    return smart_wrapper(prompt.strip(), goal_text, f"check_{dimension}")
