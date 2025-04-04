from agents import Runner, Agent, AsyncOpenAI, OpenAIChatCompletionsModel
import google.generativeai as genai
from google_flights_scraper import search_flights
import click
import json
import os
import re

user_query = input("Enter a user query: ")

api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("Please set the GEMINI_API_KEY environment variable")

provider = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=provider,
)

flight_agent = Agent(
    name="Flight Agent",
    model=model,
    instructions=f"As a travel agent, your task is to extract the best flight from the provided raw flight data based on the user query and generate a clear, concise, and informative response. Additionally, you should explain why you selected that particular flight, highlighting the criteria it meets based on the user's preferences {user_query}.",
)

genai.configure(api_key=api_key)
genai_model = genai.GenerativeModel("gemini-2.0-flash")

prompt = f"""
Extract structured details from this user query:
"{user_query}"

Return ONLY valid JSON with this format:
{{
    "from_city": "departure city",
    "to_city": "destination city",
    "departure_date": "YYYY-MM-DD",
    "return_date": "YYYY-MM-DD",
}}
"""
    
response = genai_model.generate_content(prompt)
# Get raw response from Gemini
raw_response = response.text.strip()

# Extract JSON using regex (if Gemini adds extra text)
match = re.search(r"\{.*\}", raw_response, re.DOTALL)
if match:
    json_text = match.group(0)
else:
    raise ValueError(f"Failed to extract JSON from Gemini response: {raw_response}")

travel_details = json.loads(json_text)

# Extract structured fields
from_city = travel_details.get("from_city")
to_city = travel_details.get("to_city")
departure_date = travel_details.get("departure_date")
return_date = travel_details.get("return_date")
    
flights_data = search_flights(from_city, to_city, departure_date, return_date)

text_output = "\n\n".join("".join(f"{key}: {value}" for key, value in flight.items()) for flight in flights_data)
result = Runner.run_sync(flight_agent, text_output)

# Print extracted data
print(f"\n🔹 Final Extracted Flight Data:\n{flights_data}\n")
print(click.style(f"\n🔹 Flight Agent Response:\n{result.final_output}\n", fg='green'))