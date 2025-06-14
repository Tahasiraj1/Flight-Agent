# ✈️ Flights Agent

A natural language-powered flight assistant that automates browser actions using Playwright to find and suggest flights based on user intent.

## 🧠 What It Does
- Parses flight-related requests using LLM
- Automates browser with Playwright to scrape/book flights
- Outputs recommended results to user

## 🛠️ Stack
- Python
- Playwright
- OpenAI Agents SDK
- Gemini LLM
- Streamlit (UI)

## 🧪 Example Prompt
> "I want to fly from New York to Bangkok, departing on July 1st, 2025, and returning on July 15th, 2025."

## 📦 Setup
```bash
git clone https://github.com/Tahasiraj1/Flight-Agent
cd flights-agent
pip install -r requirements.txt
streamlit run main.py
