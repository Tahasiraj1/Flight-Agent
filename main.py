from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from google_flights_scraper import search_flights, flight_agent
from agents import Runner
import re
import json
import os

app = FastAPI()

api_key = os.getenv('GEMINI_API_KEY')
if api_key is None:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

class TravelRequest(BaseModel):
    user_query: str
    

@app.post("/search-flights/")
def parse_query(request: TravelRequest):
    """Extracts structured travel details from user input using Gemini."""
    
    prompt = f"""
    Extract structured details from this user query:
    "{request.user_query}"
    
    Return ONLY valid JSON with this format:
    {{
        "from_city": "departure city",
        "to_city": "destination city",
        "departure_date": "YYYY-MM-DD",
        "return_date": "YYYY-MM-DD",
    }}
    """
    
    response = model.generate_content(prompt)
    # Get raw response from Gemini
    raw_response = response.text.strip()

    # Extract JSON using regex (if Gemini adds extra text)
    match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if match:
        json_text = match.group(0)
    else:
        raise ValueError(f"Failed to extract JSON from Gemini response: {raw_response}")
    print(json_text)

    # Convert JSON string to dictionary
    try:
        travel_details = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}\nResponse was: {json_text}")
    
    
    required_keys = ['from_city', 'to_city', 'departure_date', 'return_date']
    if not all(key in travel_details for key in required_keys):
        raise HTTPException(status_code=400, detail="Missing required travel details.")
    
    print("--------------------------")
    print(travel_details['from_city'])
    print(travel_details["to_city"])
    print(travel_details["departure_date"])
    print(travel_details["return_date"])
    print("--------------------------")
    
    flights_data = search_flights(
        travel_details["from_city"], 
        travel_details["to_city"], 
        travel_details["departure_date"], 
        travel_details["return_date"]
    )
    
     # Convert flights_data into a readable format
    text_output = "\n\n".join(
        "".join(f"{key}: {value}" for key, value in flight.items()) 
        for flight in flights_data
    )

    # Run the flight agent to process the extracted data
    result = Runner.run_sync(flight_agent, text_output)

    return {
        "user_query": request.user_query,
        "extracted_details": travel_details,
        "flights": flights_data,
        "agent_response": result.final_output,
        "raw_response": raw_response
    }