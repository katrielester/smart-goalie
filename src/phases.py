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
            "Do you often consciously set goals to help you achieve what you want in life?"
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
            "For this experiment, you’ll set one meaningful goal: something that will take at least two weeks to make progress on. We’ll use the SMART framework to help shape it.",
            "Let’s say someone sets this goal: 'I want to improve my job prospects by learning a new skill.'",
            "Is that goal specific enough?"
        ],
        "buttons": ["Yes", "No"],
        "next": {
            "Yes": "specific_feedback_yes",
            "No": "specific_feedback_no"
        }
    },
    "specific_feedback_yes": {
        "text": [
            "Close! It's heading in the right direction!",
            "But we can make it more specific by naming the skill or method, like: 'Complete a free transcription course.'"
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "specific_example"}
    },
    "specific_feedback_no": {
        "text": [
            "Right! It’s a bit broad. We can narrow it down by choosing one skill or course.",
            "For example: 'Complete a free transcription course.'"
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "specific_example"}
    },
    "specific_example": {
        "text": [
            "Which of these is more specific?",
            "1. I want to learn new skills.",
            "2. I want to complete a free transcription course."
        ],
        "buttons": ["1", "2"],
        "next": {
            "1": "specific_explain",
            "2": "specific_confirm"
        }
    },
    "specific_explain": {
        "text": [
            "That’s a great start, but it’s still too vague.",
            "It’s better to focus on one clear action, like completing a course on transcription."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_intro"}
    },
    "specific_confirm": {
        "text": [
            "Exactly. That version gives us a single, focused outcome.",
            "We’ll use: 'Complete a free transcription course.' going forward."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_intro"}
    },
    "measurable_intro": {
        "text": [
            "Now for M: Measurable.",
            "Does 'complete a free transcription course' clearly tell us how to track progress?"
        ],
        "buttons": ["Yes", "No"],
        "next": {
            "Yes": "measurable_almost",
            "No": "measurable_right"
        }
    },
    "measurable_almost": {
        "text": [
            "Not bad, it’s measurable by whether you finish or not.",
            "But we can be more detailed by including how many modules or lessons to complete each week."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_example"}
    },
    "measurable_right": {
        "text": [
            "Correct! Course completion is a clear, trackable outcome.",
            "Still, adding lesson or module targets makes it even stronger."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_example"}
    },
    "measurable_example": {
        "text": [
            "Which of these is more measurable?",
            "1. Complete a free transcription course.",
            "2. Complete a free transcription course with at least 3 modules this week."
        ],
        "buttons": ["1", "2"],
        "next": {
            "1": "measurable_explain",
            "2": "measurable_confirm"
        }
    },
    "measurable_explain": {
        "text": [
            "That’s measurable, but we can make it more structured by setting a weekly target.",
            "This helps track progress along the way."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "achievable_intro"}
    },
    "measurable_confirm": {
        "text": [
            "Perfect! Weekly milestones make progress easier to follow and adjust if needed."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "achievable_intro"}
    },
    "achievable_intro": {
        "text": [
            "Next is A: Achievable.",
            "Think about this goal: 'Complete a free transcription course with at least 3 modules this week.'",
            "Is that realistic for someone with other work and responsibilities?"
        ],
        "buttons": ["Yes", "No"],
        "next": {
            "Yes": "achievable_confirm",
            "No": "achievable_explain"
        }
    },
    "achievable_confirm": {
        "text": [
            "Exactly! It’s focused but doable, that’s what we want."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "relevant_intro"}
    },
    "achievable_explain": {
        "text": [
            "Good thinking! If that feels like too much, it can be scaled down.",
            "The key is to challenge yourself without making it overwhelming."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "relevant_intro"}
    },
    "relevant_intro": {
        "text": [
            "R stands for Relevant: the goal should matter to <b>you</b>.",
            "Why might someone want to complete a transcription course?"
        ],
        "buttons": [
            "To qualify for better-paying jobs",
            "To learn new freelance skills",
            "To feel more confident applying to gigs"
        ],
        "next": {
            "To qualify for better-paying jobs": "relevant_confirm",
            "To learn new freelance skills": "relevant_confirm",
            "To feel more confident applying to gigs": "relevant_confirm"
        }
    },
    "relevant_confirm": {
        "text": [
            "Exactly! When a goal connects to something personal, you're more likely to stick with it."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "time_intro"}
    },
    "time_intro": {
        "text": [
            "Lastly, T: Time-bound.",
            "We’ll add a clear timeframe, this helps build momentum and sets a finish line.",
            "Which of these timeframes would make the goal more time-bound?"
        ],
        "buttons": [
            "Complete the course within 2 weeks",
            "Finish 3 modules by this Friday",
            "Review progress after each module"
        ],
        "next": {
            "Complete the course within 2 weeks": "complete",
            "Finish 3 modules by this Friday": "complete",
            "Review progress after each module": "complete"
        }
    },
    "complete": {
        "text": [
            "Awesome! You've now seen how a vague goal becomes SMART:",
            "<b>'I want to improve my job prospects by learning a new skill.'</b>",
            "→ <b>'I want to complete a free transcription course within 2 weeks.'</b>",
            "For this study, you’ll pick one big-picture goal, just like the example above. Later, we’ll break it into 2–3 small weekly tasks to help you stay on track.",
            "You’re ready to set your own SMART goal now!",
            
        ],
        "buttons": ["Continue to goal setting"],
        "next": {"Continue to goal setting": "end"}
    },
    "end": {
        "text": ["SMART goal training complete — let’s help you set your own now!"],
        "complete": True
    }
}

goal_setting_flow = {
    "initial_goal": {
    "text": [
        "Let's get started!",
        "You’ll set just one personal goal for this 2-week experiment, so choose something you really care about.",
        "Choose a goal that takes time and effort, something you can make real progress on over two weeks.",
        "Think of it as a mini project or habit you care about. It shouldn't be something you finish in one sitting.",
        "Later, you’ll break this into 2–3 small weekly tasks. For now, focus on the <b>big picture.</b>",
        "What's one goal you'd really like to work on?"
    ],
    "input_type": "text",
    "next": "check_specific"
    },
    "check_specific": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Let’s check: is your goal specific?",
            "A specific goal clearly focuses on <b>one</b> clear outcome, not something vague like 'do better' or 'be more consistent.'"
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
            "Based on the suggestion above, try rewriting it to be more specific. Just type your updated version below.",
            "✏️ You'll be working on this for 2 weeks and breaking it into smaller tasks. So keep it focused but still broad enough for progress over time."
        ],
        "input_type": "text",
        "next": "check_measurable"
    },
    "check_measurable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now let’s see, is it measurable?",
            "Can you track your progress with something like a number, frequency, or milestone?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_achievable", "No": "fix_measurable"}
    },
    "fix_measurable": {
        "text": [
            "Let’s add a way to track progress Just a small adjustment!"
        ],
        "fix_with_llm": "measurable",
        "next": "input_measurable"
    },
    "input_measurable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Based on the suggestion above, try rewriting it to be more measurable. Just type your updated version below.",
            "💡 It should still feel like a high-level goal, not just one task, but a project or habit you'll grow over the next two weeks."
        ],
        "input_type": "text",
        "next": "check_achievable"
    },
    "check_achievable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Next up: is your goal achievable for you right now??",
            "It should feel realistic: challenging, but doable with the time and energy you have."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_relevant", "No": "fix_achievable"}
    },
    "fix_achievable": {
        "text": [
            "Alright, let’s make it a bit more manageable so you can make steady progress!"
        ],
        "fix_with_llm": "achievable",
        "next": "input_achievable"
    },
    "input_achievable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Try rewriting it to be more doable: something you can make progress on over the next two weeks."
        ],
        "input_type": "text",
        "next": "check_relevant"
    },
    "check_relevant": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now let’s check, does this goal feel personally meaningful to you?",
            "A relevant goal connects to what <b>you</b> care about, your interests, values, or current priorities."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_timebound", "No": "fix_relevant"}
    },
    "fix_relevant": {
        "text": [
            "Let’s bring in the 'why'. Why does this goal matter to you personally?"
        ],
        "fix_with_llm": "relevant",
        "next": "input_relevant"
    },
    "input_relevant": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Try rewriting it to be more personally meaningful to you. Just type your updated version below."
        ],
        "input_type": "text",
        "next": "check_timebound"
    },
    "check_timebound": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Almost done! Does your goal have a clear timeframe?",
            "A time-bound goal has a deadline, schedule, or review point, something that tells you <b>when</b> it will happen."
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "finalize_goal", "No": "fix_timebound"}
    },
    "fix_timebound": {
        "text": [
            "Let’s add a simple timeframe to help pace your progress.",
            "⏳ Reminder: You’ll work on this goal throughout the full 2-week experiment. So pick a timeframe that supports ongoing momentum."
        ],
        "fix_with_llm": "timebound",
        "next": "input_timebound"
    },
    "input_timebound": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Based on the suggestion above, try adding a timeframe to your goal. Just type your updated version below.",
            "✏️ You’ll work on this same goal throughout the 2-week experiment, so pick a timeframe that supports steady progress, even if it goes beyond 2 weeks."
        ],
        "input_type": "text",
        "next": "finalize_goal"
    },
    "finalize_goal": {
        "text": [
            "Here’s your finalized SMART goal!",
            "{current_goal}",
            "Great job, it’s looking solid now!",
            "You’ll use this goal for the full 2 weeks and soon break it into smaller weekly tasks.",
            "Ready to save it, or do you want to tweak it first?"
        ],
        "buttons": ["Save Goal", "Edit Manually"],
        "next": {"Save Goal": "save_goal", "Edit Manually": "edit_goal"}
    },
    "edit_goal": {
        "text": [
            "Please type your updated version of the goal below."
        ],
        "input_type": "text",
        "next": "finalize_edit_goal"
    },
    "finalize_edit_goal": {
        "text": [
            "Here’s your updated SMART goal!",
            "{current_goal}",
            "Ready to save it, or do you want to tweak it?"
        ],
        "buttons": ["Save Goal", "Edit Manually"],
        "next": {"Save Goal": "save_goal", "Edit Manually": "edit_goal"}
    },
    "save_goal": {
        "text": [
            "Your goal has been saved successfully!"
        ],
        "complete": True
    }
}