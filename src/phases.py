#phases.py
smart_intro_text = """
SMART is a framework that helps you set better goals:

- **Specific**: What exactly do you want to accomplish?
- **Measurable**: How will you know it's done?
- **Achievable**: Is it realistic for you?
- **Relevant**: Does it matter to your current life or work?
- **Time-bound**: What’s your timeline?

Let’s try it together!
"""

weekly_reflection_prompts = [
    "Which goal(s) did you work on this week?",
    "How would you rate your progress? (0–100%)",
    "What obstacles did you encounter?",
    "What strategies worked well?",
    "What will you do next week?"
]


smart_training_flow = {
    "intro": {
        "text": [
            "Great! Now, I'm going to teach you about goal-setting, help you to set goals of your own, and monitor your progress.",
            "Are you ready to get started?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "get_name", "No": "exit"}
    },
    "get_name": {
        "text": ["Sounds good! First, how should I call you?"],
        "input_type": "text",
        "next": "goal_intro"
    },
    "goal_intro": {
        "text": [
            "Then let’s get started {user_name}!",
            "First, let’s talk about goal-setting.",
            "Goal setting means deciding on something you want to achieve, and creating a plan to make it happen.",
            "It’s the first step in turning the invisible into the visible—turning wishful thinking into an actionable plan.",
            "Studies have shown that setting specific and challenging goals can significantly improve performance."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "how_often"}
    },
    "how_often": {
        "text": [
            "How often do you consciously set goals to help you achieve what you want in life?"
        ],
        "buttons": ["Often", "Sometimes", "Never"],
        "next": {"Often": "smart_intro1", "Sometimes": "smart_intro1", "Never": "smart_intro2"}
    },
    "smart_intro1": {
        "text": [
            "That's great! I'm here to help you set goals even better."
            "To do this, we’ll use the SMART goal criteria. Ready to dive in?"
        ],
        "buttons": ["Let’s do this!"],
        "next": {"Let’s do this!": "smart_definition"}
    },
    "smart_intro2": {
        "text": [
            "No problem! I’m here to show you how to set goals that actually work.",
            "To do this, we’ll use the SMART goal criteria. Ready to dive in?"
        ],
        "buttons": ["Let’s do this!"],
        "next": {"Let’s do this!": "smart_definition"}
    },
    "smart_definition": {
        "text": [
            "SMART is an acronym to guide you in crafting great goals:",
            "- Specific",
            "- Measurable",
            "- Achievable",
            "- Relevant",
            "- Time-bound",
            "If your goal ticks all five, you’re much more likely to succeed.",
            "Watch this video to learn more about SMART goals:<br><br><a href=\"https://www.youtube.com/watch?v=yA53yhiOe04&ab_channel=FlikliTV\" target=\"_blank\" style=\"color:#4ea8ff;\">Achieve More by Setting SMART Goals (YouTube)</a>"
        ],
        "buttons": ["I watched the video"],
        "next": {
            "I watched the video": "specific_intro"
        }
    },
    "specific_intro": {
        "text": [
            "Let’s try out each part of SMART using a sample goal.",
            "Let’s say the goal is: 'Get more healthy this year.'",
            "Do you think this goal is specific?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "specific_feedback_yes", "No": "specific_feedback_no"}
    },
    "specific_feedback_yes": {
        "text": [
            "I see why you might think that! It's a good start, but to be truly specific, a goal should narrow down to just one clear focus.",
            "Let’s see how we can sharpen it!"
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "specific_options"}
    },
    "specific_feedback_no": {
        "text": [
            "Exactly! The goal still needs adjustment.",
            "Let’s explore how we can make it more specific."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "specific_options"}
    },
    "specific_options": {
        "text": [
            "Which of these is a better example of a specific goal?",
            "1. I would like to eat more healthily and work out more regularly.",
            "2. I would like to work out regularly."
        ],
        "buttons": ["1", "2"],
        "next": {"1": "specific_rationale_1", "2": "specific_rationale_2"}
    },
    "specific_rationale_1": {
        "text": [
            "This is better, but it lists more than one goal.",
            "A specific goal should only focus on one objective.",
            "Let’s use: 'I would like to work out regularly' as our example moving forward."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_intro"}
    },
    "specific_rationale_2": {
        "text": [
            "You are correct! A specific goal should focus on one clear outcome.",
            "Let’s use: 'I would like to work out regularly' as our example moving forward."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_intro"}
    },
    "measurable_intro": {
        "text": [
            "Now let’s look at M: Measurable.",
            "Measurable means you can track progress and know when the goal is achieved.",
            "Is 'I would like to work out regularly' measurable?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "measurable_feedback_yes", "No": "measurable_feedback_no"}
    },
    "measurable_feedback_yes": {
        "text": [
            "Good thinking, you're close!",
            "But to be fully measurable, the goal should clearly state how we'll track success, like frequency or amount."

        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_options"}
    },
    "measurable_feedback_no": {
        "text": [
            "That’s right! We need to specify how often or how long.",
            "This makes tracking your progress much easier."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_options"}
    },
    "measurable_options": {
        "text": [
            "Which of these is the better example of a measurable goal?",
            "1. I would like to work out three times a week.",
            "2. I would like to work out three times a week, at least 30 minutes each time."
        ],
        "buttons": ["1", "2"],
        "next": {"1": "measurable_rationale_1", "2": "measurable_rationale_2"}
    },
    "measurable_rationale_1": {
        "text": [
            "Good start! That’s measurable.",
            "But we can strengthen it by adding duration."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "achievable_intro"}
    },
    "measurable_rationale_2": {
        "text": [
            "Perfect! Frequency and duration make the goal fully measurable."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "achievable_intro"}
    },
    "achievable_intro": {
    "text": [
        "Now let’s move on to A: Achievable.",
        "Our current goal is: 'I would like to work out three times a week, at least 30 minutes each time.'",
        "Think about your current situation — your time, energy, and schedule.",
        "On a scale from 0 (impossible) to 5 (very easy), how achievable does this goal feel to you?"
        ],
    "buttons": ["0", "1", "2", "3", "4", "5"],
    "next": {
        "0": "achievable_low",
        "1": "achievable_low",
        "2": "achievable_low",
        "3": "achievable_good",
        "4": "achievable_good",
        "5": "achievable_good"
        },
    },
    "achievable_low": {
    "text": [
        "Thanks for being honest!",
        "If a goal feels very difficult, that's a sign it may need to be broken down into smaller, more achievable steps."
    ],
    "buttons": ["Continue"],
    "next": {"Continue": "relevant_intro"}
    },
    "achievable_good": {
        "text": [
            "Awesome!",
            "When a goal feels realistic yet motivating, you're setting yourself up for success."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "relevant_intro"}
    },
    #RELEVANT
    "relevant_intro": {
        "text": [
            "Now let’s move to R: Relevant.",
            "The goal should matter to you personally—it should align with your values and interests.",
            "Our current goal is: 'I would like to work out three times a week, at least 30 minutes each time.'",
            "Does this goal express why it’s important to you?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "relevant_explain_anyway", "No": "relevant_prompt"}
    },
    "relevant_explain_anyway": {
        "text": [
            "Good that you're thinking about relevance!",
            "Even so, let’s make it stronger: try adding why it matters to you personally. For example: 'to improve my health' or 'to boost my energy.'",
            "Please type it below."
        ],
        "input_type": "text",
        "next": "time_intro"
    },
    "relevant_prompt": {
        "text": [
            "No worries. To make your goal stronger, try adding why it matters to you personally.",
            "For example: 'to improve my health' or 'to feel more energetic.'",
            "Please type it below."
        ],
        "input_type": "text",
        "next": "relevant_echo"
    },
    "relevant_echo": {
        "text": [
            "Awesome! Here's your updated goal:",
            "{full_goal}",
            "Looks great! Now let's move on to the final step: Time-bound."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "time_intro"}
    },
    # TIME-BOUND
    "time_intro": {
        "text": [
            "Finally, T for Time-bound!",
            "Here's your updated goal so far:",
            "{full_goal}",
            "For some goals — like building a habit — time-bound doesn't always mean a final deadline.",
            "It could mean deciding how long you'll continue the habit or when you'll review your progress.",
            "For example: 'for the next 3 months' or 'review progress after 1 month.'"
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "time_check"}
    },

    "time_check": {
        "text": [
            "Does your goal include a timeframe — like how long you’ll continue it or when you’ll check your progress?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "time_add_anyway", "No": "time_prompt"}
    },

    "time_add_anyway": {
        "text": [
            "Great that you’re thinking about it!",
            "Let’s make it even stronger — add a clear timeframe or review point to your goal.",
            "Please type your updated goal including the timeframe below."
        ],
        "input_type": "text",
        "next": "complete"
    },

    "time_prompt": {
        "text": [
            "No problem — let’s strengthen your goal by adding a timeframe or a review point.",
            "For example: 'for the next 3 months' or 'review my progress after 1 month.'",
            "Type your updated goal including that information below."
        ],
        "input_type": "text",
        "next": "complete"
    },
    "complete": {
        "text": [
            "Great job! You now understand the SMART criteria and how to use it to make powerful goals.",
            "Let’s move on to creating your own!"
        ],
        "buttons": ["Continue to goal setting"],
        "next": {"Continue to goal setting": "end"}
    },
    "end": {
        "text": ["Training complete. You're ready to set SMART goals!"],
        "complete": True
    },
    "exit": {
        "text": ["No worries! Come back anytime you’re ready."]
    }
}

goal_setting_flow = {
    "initial_goal": {
    "text": [
        "Let's get started!",
        "You’ll only set one goal for this experiment, so pick something you really care about.",
        "It doesn’t have to be finished in two weeks, but it should be something you’re motivated to start or move forward.",
        "Think of it as a short-term project or outcome — something meaningful that can be broken into 2–3 smaller tasks this week.",
        "Please type the goal you would like to achieve."
    ],
    "input_type": "text",
    "next": "check_specific"
    },
    "check_specific": {
        "text": [
            "Is your goal specific enough?",
            "A specific goal focuses on one clear outcome."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_measurable", "No": "fix_specific"}
    },
    "fix_specific": {
        "text": [
            "Let me help you make it more specific..."
        ],
        "fix_with_llm": "specific",
        "next": "input_specific"
    },
    "input_specific": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now, based on the suggestion above, please type your improved version of the goal."
        ],
        "input_type": "text",
        "next": "check_measurable"
    },
    "check_measurable": {
        "text": [
            "Is your goal measurable?",
            "A measurable goal lets you track progress clearly."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_achievable", "No": "fix_measurable"}
    },
    "fix_measurable": {
        "text": [
            "Let's make your goal more measurable..."
        ],
        "fix_with_llm": "measurable",
        "next": "input_measurable"
    },
    "input_measurable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now, based on the suggestion above, please type your improved version of the goal."
        ],
        "input_type": "text",
        "next": "check_achievable"
    },
    "check_achievable": {
        "text": [
            "Is your goal achievable for you?",
            "An achievable goal should be realistic given your situation."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_relevant", "No": "fix_achievable"}
    },
    "fix_achievable": {
        "text": [
            "Let's adjust your goal to be more achievable..."
        ],
        "fix_with_llm": "achievable",
        "next": "input_achievable"
    },
    "input_achievable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now, based on the suggestion above, please type your improved version of the goal."
        ],
        "input_type": "text",
        "next": "check_relevant"
    },
    "check_relevant": {
        "text": [
            "Is your goal relevant to your personal life, career, or values?",
            "A relevant goal should matter to you personally."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_timebound", "No": "fix_relevant"}
    },
    "fix_relevant": {
        "text": [
            "Let's make your goal clearly relevant to you..."
        ],
        "fix_with_llm": "relevant",
        "next": "input_relevant"
    },
    "input_relevant": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now, based on the suggestion above, please type your improved version of the goal."
        ],
        "input_type": "text",
        "next": "check_timebound"
    },
    "check_timebound": {
        "text": [
            "Does your goal have a clear timeframe or deadline?",
            "Adding a timeline helps you stay focused."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "finalize_goal", "No": "fix_timebound"}
    },
    "fix_timebound": {
        "text": [
            "Let's add a realistic timeframe to your goal..."
        ],
        "fix_with_llm": "timebound",
        "next": "input_timebound"
    },
    "input_timebound": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now, based on the suggestion above, please type your improved version of the goal."
        ],
        "input_type": "text",
        "next": "finalize_goal"
    },
    "finalize_goal": {
        "text": [
            "Here’s your finalized SMART goal!",
            "{current_goal}",
            "Would you like to save it or make manual edits?"
        ],
        "buttons": ["Save Goal", "Edit Manually"],
        "next": {"Save Goal": "save_goal", "Edit Manually": "edit_goal"}
    },
    "edit_goal": {
        "text": [
            "Please type your edited version of the SMART goal."
        ],
        "input_type": "text",
        "next": "save_goal"
    },
    "save_goal": {
        "text": [
            "Your goal has been saved successfully!"
        ],
        "complete": True
    }
}