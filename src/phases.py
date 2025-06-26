#phases.py

smart_training_flow = {
    "intro": {
        "text": [
            "Great! I’ll walk you through how to set a strong goal and help you track your progress over time.",
            "Are you ready to get started?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "goal_intro", "No": "exit"}
    },
    "goal_intro": {
        "text": [
            "Let’s get started!",
            "First, let’s talk about goal-setting.",
            "Goal setting means deciding on something you want to achieve, and creating a plan to make it happen.",
            "It’s how we turn a vague idea into something you can actually work toward.",
            "Studies have shown that setting specific and challenging goals can significantly improve performance."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "how_often"}
    },
    "how_often": {
        "text": [
            "How often do you consciously set goals to help you achieve what you want in life?"
        ],
        "buttons": ["All the time", "Sometimes", "Not really"],
        "next": {"All the time": "smart_intro1", "Sometimes": "smart_intro1", "Not really": "smart_intro2"}
    },
    "smart_intro1": {
        "text": [
            "That's great! I'm here to help you take it to the next level."
            "To do that, we’ll use something called SMART goals. Ready to dive in?"
        ],
        "buttons": ["Let’s do this!"],
        "next": {"Let’s do this!": "smart_definition"}
    },
    "smart_intro2": {
        "text": [
            "No problem! That's exactly what I'm here for.",
            "I'll show you a method called SMART goals. Ready to dive in?"
        ],
        "buttons": ["Let’s do this!"],
        "next": {"Let’s do this!": "smart_definition"}
    },
    "smart_definition": {
        "text": [
            "SMART stands for Specific, Measurable, Achievable, Relevant, and Time-bound.",
            "Want to watch a short 1-minute animation before we continue?"
        ],
        "buttons": ["Yes, show me", "No, let's keep going"],
        "next": {
            "Yes, show me": "smart_video",
            "No, let's keep going": "specific_intro"
        }
    },
    "smart_video": {
        "text": [
            "Here’s the video:<br><a href=\"https://www.youtube.com/watch?v=yA53yhiOe04&ab_channel=FlikliTV\" target=\"_blank\" style=\"color:#4ea8ff;\">Watch: SMART Goals Explained (1 min)</a>",
            "When you’re ready, we’ll break it down together."
        ],
        "buttons": ["I'm ready"],
        "next": {"I'm ready": "specific_intro"}
    },
    "specific_intro": {
        "text": [
            "Let’s say the goal is: 'Get more healthy this year.'",
            "Is this goal specific enough?"
        ],
        "buttons": ["Yes", "No"],
        "next": {
            "Yes": "specific_feedback_yes",
            "No": "specific_feedback_no"
        }
    },
    "specific_feedback_yes": {
        "text": [
            "Not quite! A goal like 'get more healthy' is vague.",
            "We want a single clear action, like working out regularly."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "specific_example"}
    },
    "specific_feedback_no": {
        "text": [
            "Exactly! That goal is too vague.",
            "A specific goal should be just one clear action, like working out regularly."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "specific_example"}
    },
    "specific_example": {
        "text": [
            "Between these, which is more specific?",
            "1. I want to eat healthier and work out.",
            "2. I want to work out regularly."
        ],
        "buttons": ["1", "2"],
        "next": {
            "1": "specific_explain",
            "2": "specific_confirm"
        }
    },
    "specific_explain": {
        "text": [
            "That's close! But it combines two goals. Specific goals should focus on just one action.",
            "We’ll use: 'I want to work out regularly' going forward."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_intro"}
    },
    "specific_confirm": {
        "text": [
            "Exactly! One clear focus makes a goal more actionable.",
            "We’ll use: 'I want to work out regularly' going forward."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_intro"}
    },
    "measurable_intro": {
        "text": [
            "Next is M: Measurable.",
            "Does 'I want to work out regularly' tell us how often or how long?"
        ],
        "buttons": ["Yes", "No"],
        "next": {
            "Yes": "measurable_almost",
            "No": "measurable_right"
        }
    },
    "measurable_almost": {
        "text": [
            "Good guess — it's close.",
            "But we should add details like how often or how long to make it fully measurable."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_example"}
    },
    "measurable_right": {
        "text": [
            "Correct — we need specifics like frequency and duration to measure success."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_example"}
    },
    "measurable_example": {
        "text": [
            "Which of these is more measurable?",
            "1. I want to work out 3 times a week.",
            "2. I want to work out 3 times a week, at least 30 minutes each time."
        ],
        "buttons": ["1", "2"],
        "next": {
            "1": "measurable_explain",
            "2": "measurable_confirm"
        }
    },
    "measurable_explain": {
        "text": [
            "Nice! That’s measurable.",
            "We can make it even clearer by including the time spent."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "achievable_intro"}
    },
    "measurable_confirm": {
        "text": [
            "Perfect! Frequency and duration make it fully measurable."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "achievable_intro"}
    },
    "achievable_intro": {
        "text": [
            "Now A: Achievable.",
            "Think of this goal: 'Work out 3 times a week for at least 30 minutes.'",
            "Is this goal realistic given most people’s schedules?"
        ],
        "buttons": ["Yes", "No"],
        "next": {
            "Yes": "achievable_confirm",
            "No": "achievable_explain"
        }
    },
    "achievable_confirm": {
        "text": [
            "Yes! A realistic but challenging goal sets you up for success."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "relevant_intro"}
    },
    "achievable_explain": {
        "text": [
            "Good point! If a goal feels too difficult, we can make it more manageable.",
            "It’s better to start small and build up."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "relevant_intro"}
    },
    "relevant_intro": {
        "text": [
            "R is for Relevant — the goal should matter to you.",
            "Why might someone want to work out regularly?"
        ],
        "buttons": [
            "To improve health",
            "To reduce stress",
            "To feel more energetic"
        ],
        "next": {
            "To improve health": "relevant_confirm",
            "To reduce stress": "relevant_confirm",
            "To feel more energetic": "relevant_confirm"
        }
    },
    "relevant_confirm": {
        "text": [
            "Nice! Tying a goal to personal values or needs makes it more motivating."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "time_intro"}
    },
    "time_intro": {
        "text": [
            "T is for Time-bound — adding a timeframe helps you stay focused.",
            "Which of these timeframes would complete the goal?"
        ],
        "buttons": [
            "For the next 3 months",
            "Until December",
            "Review progress monthly"
        ],
        "next": {
            "For the next 3 months": "complete",
            "Until December": "complete",
            "Review progress monthly": "complete"
        }
    },
    "complete": {
        "text": [
            "Great job! You now understand how to make a goal SMART.",
            "Next, let’s set a goal that matters to YOU."
        ],
        "buttons": ["Continue to goal setting"],
        "next": {"Continue to goal setting": "end"}
    },
    "end": {
        "text": ["Training complete. You're ready to set your own SMART goal!"],
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
            "Here’s your current goal: {current_goal}",
            "Let’s check: is your goal specific enough?",
            "A specific goal clearly describes one main thing you want to achieve, not something vague like 'do better' or 'be more consistent.'"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_measurable", "No": "fix_specific"}
    },
    "fix_specific": {
        "text": [
            "No worries, let’s tweak your goal to make it a little clearer and more focused."
        ],
        "fix_with_llm": "specific",
        "next": "input_specific"
    },
    "input_specific": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Based on the suggestion above, try rewriting it to be more specific. Just type your updated version below."
        ],
        "input_type": "text",
        "next": "check_measurable"
    },
    "check_measurable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now let’s see, is your goal is measurable?",
            "This means you should be able to tell how much progress you’ve made or when it’s done, like a number, frequency, or result."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_achievable", "No": "fix_measurable"}
    },
    "fix_measurable": {
        "text": [
            "Let’s fine-tune your goal so it’s easier to track. Just a small adjustment!"
        ],
        "fix_with_llm": "measurable",
        "next": "input_measurable"
    },
    "input_measurable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Based on the suggestion above, try rewriting it to be more measurable. Just type your updated version below."
        ],
        "input_type": "text",
        "next": "check_achievable"
    },
    "check_achievable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Next up: is your goal achievable for you?",
            "An achievable goal is realistic and fits your current time, energy, and resources. Not too overwhelming, not too easy."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_relevant", "No": "fix_achievable"}
    },
    "fix_achievable": {
        "text": [
            "Alright, let’s scale it down just a bit so it feels more doable for you this week."
        ],
        "fix_with_llm": "achievable",
        "next": "input_achievable"
    },
    "input_achievable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Based on the suggestion above, try rewriting it to be more achievable. Just type your updated version below."
        ],
        "input_type": "text",
        "next": "check_relevant"
    },
    "check_relevant": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now let’s check, does your goal feel personally meaningful?",
            "A relevant goal should matter to <b>you</b>, something that connects to your values, interests, or priorities."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_timebound", "No": "fix_relevant"}
    },
    "fix_relevant": {
        "text": [
            "Let’s strengthen the connection! Why does this goal matter to you personally?"
        ],
        "fix_with_llm": "relevant",
        "next": "input_relevant"
    },
    "input_relevant": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Based on the suggestion above, try rewriting it to be more relevant. Just type your updated version below."
        ],
        "input_type": "text",
        "next": "check_timebound"
    },
    "check_timebound": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Almost done! Does your goal have a clear timeframe?",
            "A time-bound goal includes a deadline, schedule, or review point, something that tells you <b>when</b> it will happen."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "finalize_goal", "No": "fix_timebound"}
    },
    "fix_timebound": {
        "text": [
            "Let’s add a simple timeframe to give your goal more structure and momentum."
        ],
        "fix_with_llm": "timebound",
        "next": "input_timebound"
    },
    "input_timebound": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Based on the suggestion above, try rewriting it to be timebound. Just type your updated version below."
        ],
        "input_type": "text",
        "next": "finalize_goal"
    },
    "finalize_goal": {
        "text": [
            "Here’s your finalized SMART goal!",
            "{current_goal}",
            "You’ve done a great job refining your goal, it’s looking solid now!",
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