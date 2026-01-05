# SMART Goalie
AI-powered SMART Goal-Setting & Progress-Monitoring Chatbot (Streamlit, Python, Mistral)

![App preview](docs/screenshots/preview.png)

SMART Goalie is an LLM-powered chatbot that guides crowdworkers through SMART goal setting, weekly task planning, and structured progress monitoring via twice-weekly reflection prompts. It was built as part of an MSc thesis project and designed to support a longitudinal study experience with database-backed session persistence and logging. Study is available [here](https://resolver.tudelft.nl/uuid:cd50217a-3eda-44e4-824c-090b2ecca45d).

## What's in this repo
- Streamlit chatbot app for SMART onboarding (goal + up to 3 tasks)
- Treatment flow: twice-weekly guided reflections (WOOP / What-SoWhat-NowWhat)
- PostgreSQL persistence (goals, tasks, reflections, chat context)
- Logging for study/evaluation

## Run locally
```bash
pip install -r requirements.txt
streamlit run src/streamlit_app.py
