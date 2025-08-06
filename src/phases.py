#phases.py

smart_training_flow = {
    "intro": {
        "text": [
            "Great! I’ll walk you through how to set a strong goal and help you track your progress over time.",
            "Are you ready to get started?"
        ],
        "buttons": ["Yes"],
        "next": {"Yes": "goal_intro"}
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
            "That's great! I'm here to help you take it to the next level.",
            "To do that, we’ll use something called SMART goals. Ready to dive in?"
        ],
        "buttons": ["Let’s do this!"],
        "next": {"Let’s do this!": "smart_intro"}
    },
    "smart_intro2": {
        "text": [
            "No problem! That's exactly what I'm here for.",
            "I'll show you a method called SMART goals. Ready to dive in?"
        ],
        "buttons": ["Let’s do this!"],
        "next": {"Let’s do this!": "smart_intro"}
    },
    "smart_intro": {
    "text": [
        "SMART stands for Specific, Measurable, Achievable, Relevant, and Time-bound.",
        "Watch this short 1-minute video before we continue:",
        "<a href=\"https://www.youtube.com/watch?v=yA53yhiOe04&ab_channel=FlikliTV\" target=\"_blank\" style=\"color:#4ea8ff;\">Watch: SMART Goals Explained</a>"
    ],
    "buttons": ["I've watched it"],
    "next": {"I've watched it": "study_scope"}
    },
    "study_scope": {
    "text": [
        "SMART works for any deadline, but in this study, you’ll set a goal to work on for the next <b>two weeks</b>.",
        "Let’s dive in!"
    ],
    "buttons": ["Let’s go"],
    "next": {"Let’s go": "specific_intro"}
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
            "Correct! Course completion is not a clear, trackable outcome.",
            "Adding lesson or module targets makes it even stronger."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "measurable_example"}
    },
    "measurable_example": {
        "text": [
            "Which of these is more measurable?",
            "1. Complete a free transcription course.",
            "2. Complete a free transcription course with at least 3 modules each week."
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
            "Think about this goal: 'Complete a free transcription course with at least 3 modules each week.'",
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
            "T is for Time-bound: every SMART goal needs a clear finish line!",
            "You don’t need to rewrite your whole goal—just pick a phrasing that spans two weeks, or sets a weekly milestone.",
            "Example base goal: <i>Complete a free transcription course</i>",
            "Which of these is properly time-bound for our 2-week experiment?"
        ],
        "buttons": [
            "Complete the course within two weeks",
            "Finish 3 modules each week",
            "Review progress after each module"
        ],
        "next": {
            "Complete the course within two weeks": "time_feedback_yes",
            "Finish 3 modules each week":     "time_feedback_yes",
            "Review progress after each module": "time_feedback_no"
        }
    },
    "time_feedback_no": {
        "text": [
            "Not quite—remember: your goal needs either a two-week deadline or a weekly milestone over two weeks.",
            "Let’s try again."
        ],
        "buttons": ["Back to choices"],
        "next": {"Back to choices": "time_intro"}
    },
    "time_feedback_yes": {
        "text": [
            "Exactly! That’s all it takes—just picking a two-week deadline or a weekly target.",
            "You’re ready for the recap."
        ],
        "buttons": ["Continue"],
        "next": {"Continue": "complete"}
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
        "text": ["SMART goal training complete, let’s help you set your own now!"],
        "complete": True
    }
}

goal_setting_flow = {
    "initial_goal": {
    "text": [
        "Let’s get started! You will set just <b>one personal goal</b> for this 2-week experiment, something that takes time and effort, not just a one-off task.",
        "Think of it as a mini project or meaningful habit: something you’ll work toward steadily and break down into smaller steps later.",
        "✨ What’s one thing you’d genuinely like to make progress on over the next two weeks?"
    ],
    "input_type": "text",
    "next": "check_specific"
    },
    "check_specific": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Is it <b>specific</b>: focused on one clear outcome, not something vague like “be better” or “get things done”?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_measurable", "No": "fix_specific"}
    },
    "fix_specific": {
        "text": [
            "No worries, let’s tweak your goal to make it a little clearer and more focused.<br> Here are a few ways you might make it more specific:"
        ],
        "fix_with_llm": "specific",
        "next": "input_specific"
    },
    "input_specific": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Try rewriting your goal to make it more specific, using the suggestion above as a guide.",
            "✏️ You'll be working on this for 2 weeks, so keep it focused, but broad enough to break into smaller tasks later."
        ],
        "input_type": "text",
        "next": "check_measurable"
    },
    "check_measurable": {
        "text": [
            "Here’s your current goal: {current_goal}",
            "Now, is it <b>measurable</b>? <br> Can you track your progress with something like a number, frequency, or milestone?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "check_achievable", "No": "fix_measurable"}
    },
    "fix_measurable": {
        "text": [
            "Let’s add a way to track progress, just a small adjustment! <br> Here are a few ways you might make it more measurable:"
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
            "Alright, let’s make it a bit more manageable so you can make steady progress! <br> Here are a few ways you might make it more achievable:"
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
            "Let’s add a simple timeframe to help pace your progress. <br> Here are a few ways you can tweak the goal:",
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

goal_setting_flow_score = {
    "initial_goal": {
        "text": [
            "</b>🔸 Goal Setting 🔸</b>",
            "Let’s get started! You’ll choose one goal to focus on for the next 2 weeks.",
            "Think of something meaningful you’d like to work toward. Not a quick task, but a mini project or habit.",
            "<b>👉 Please type your goal below to continue.</b>"
        ],
        "input_type": "text",
        "next": "check_specific"
    },

    "check_specific": {
        "text": [
            "Let’s check how <b>specific</b> it is..."
        ],
        "llm_feedback": "specific",
        "next": "specific_improve_decision"
    },

    "specific_improve_decision": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "{llm_feedback}",
            "Would you like to improve this before we continue?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "fix_specific", "No": "check_measurable"}
    },

    "fix_specific": {
        "text": [
            "Here are a few ways to make your goal more specific:"
        ],
        "fix_with_llm": "specific",
        "next": "input_specific"
    },

    "input_specific": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "<b>Try rewriting your goal using the suggestions above.</b>",
            "✏️ You'll be working on this for 2 weeks, so keep it focused, but broad enough to break into smaller tasks later."
        ],
        "input_type": "text",
        "next": "check_measurable"
    },

    "check_measurable": {
        "text": [
            "Now let’s see if your goal is <b>measurable</b>.",
            "Can you track progress in some way, like frequency, quantity, or milestones?"
        ],
        "llm_feedback": "measurable",
        "next": "measurable_improve_decision"
    },

    "measurable_improve_decision": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "{llm_feedback}",
            "Would you like to improve this part?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "fix_measurable", "No": "check_achievable"}
    },

    "fix_measurable": {
        "text": [
            "Here are a few ways to make your goal more measurable:"
        ],
        "fix_with_llm": "measurable",
        "next": "input_measurable"
    },

    "input_measurable": {
        "text": [
            "📝 Here's your current goal: <i>{current_goal}</i>",
            "<b>Try rewriting your goal to include a way to measure progress.</b>",
            "Still keep it broad enough to span the full 2 weeks."
        ],
        "input_type": "text",
        "next": "check_achievable"
    },

    "check_achievable": {
        "text": [
            "Let’s check if this feels <b>achievable</b> for you right now.",
            "It should feel realistic, something you can work on steadily over 2 weeks."
        ],
        "llm_feedback": "achievable",
        "next": "achievable_improve_decision"
    },

    "achievable_improve_decision": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "{llm_feedback}",
            "Want to adjust this part before moving on?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "fix_achievable", "No": "check_relevant"}
    },

    "fix_achievable": {
        "text": [
            "Here are a few ways to make your goal more achievable:"
        ],
        "fix_with_llm": "achievable",
        "next": "input_achievable"
    },

    "input_achievable": {
        "text": [
            "<b>Try rewriting your goal to feel more doable over the next two weeks.</b>",
            "📝 Your current goal: <i>{current_goal}</i>"
        ],
        "input_type": "text",
        "next": "check_relevant"
    },

    "check_relevant": {
        "text": [
            "Now let’s check if this goal feels relevant to you.",
            "Does it connect to something you care about or want to improve right now?"
        ],
        "llm_feedback": "relevant",
        "next": "relevant_improve_decision"
    },

    "relevant_improve_decision": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "{llm_feedback}",
            "Would you like to make this feel more personal?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "fix_relevant", "No": "check_timebound"}
    },

    "fix_relevant": {
        "text": [
            "Here are a few ways to make your goal feel more personally meaningful:"
        ],
        "fix_with_llm": "relevant",
        "next": "input_relevant"
    },

    "input_relevant": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "<b>Try updating your goal so it connects more clearly to your values or priorities.</b>"
        ],
        "input_type": "text",
        "next": "check_timebound"
    },

    "check_timebound": {
        "text": [
            "Almost done! Let’s make sure your goal has a timeframe.",
            "Does it include a timeline, deadline, or pace for steady progress?"
        ],
        "llm_feedback": "timebound",
        "next": "timebound_improve_decision"
    },

    "timebound_improve_decision": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "{llm_feedback}",
            "Would you like to add or adjust the timeframe?"
        ],
        "buttons": ["Yes", "No"],
        "next": {"Yes": "fix_timebound", "No": "finalize_goal"}
    },

    "fix_timebound": {
        "text": [
            "Here are a few ways to add a simple timeframe to your goal:"
        ],
        "fix_with_llm": "timebound",
        "next": "input_timebound"
    },

    "input_timebound": {
        "text": [
            "📝 Your current goal: <i>{current_goal}</i>",
            "<b>Try rewriting your goal with a timeframe that fits the 2-week period.</b>"
        ],
        "input_type": "text",
        "next": "finalize_goal"
    },

    "finalize_goal": {
        "text": [
            "👍 Here’s your finalized goal:",
            "{current_goal}"
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
            "Here’s your updated goal:",
            "{current_goal}"
        ],
        "buttons": ["Save Goal", "Edit Manually"],
        "next": {"Save Goal": "save_goal", "Edit Manually": "edit_goal"}
    },

    "save_goal": {
        "text": [
            "Your goal has been saved! Great work."
        ],
        "complete": True
    }
} 