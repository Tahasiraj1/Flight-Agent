import install_playwright
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
from agents import Runner, Agent, AsyncOpenAI, OpenAIChatCompletionsModel
import google.generativeai as genai
from google_flights_scraper import search_flights
import streamlit as st
import json
import os
import re

install_playwright.install()
# --- UI Design ---

st.set_page_config(page_title="Your Personal Flight Agent", page_icon="✈️")
st.title("✈️ Your Personal Flight Agent")
st.subheader("Tell me where and when you want to fly!")

user_query = st.text_input("Enter your flight request:")


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

if st.button("Search for Flights", use_container_width=True):
    with st.spinner("🔍 Processing your request and searching for flights..."):
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
        
        with st.spinner(f"✈️ Searching for flights from {from_city} to {to_city} on {departure_date}..."):
            flights_data = search_flights(from_city, to_city, departure_date, return_date)
            
            if flights_data:
                st.success(f"✅ Found {len(flights_data)} flights!")
                text_output = "\n\n".join("".join(f"{key}: {value}" for key, value in flight.items()) for flight in flights_data)

                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                with st.spinner("🤖 Asking the Flight Agent for the best option..."):
                    result = Runner.run_sync(flight_agent, text_output)
                    st.subheader("✨ Best Flight Recommendation:")
                    st.markdown(f"{result.final_output}")

                with st.expander("Detailed Flight Data"):
                    st.write(flights_data)
            else:
                st.warning("No flights found for the specified criteria.")
