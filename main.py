from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

api_key = os.getenv('GEMINI_API_KEY')
if api_key is None:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

class TravelRequest(BaseModel):
    user_query: str
    

@app.post("/parse-query/")
def parse_query(request: TravelRequest):
    """Extracts structured travel details from user input using Gemini."""
    
    prompt = f"""
    Extract structured details from this user query:
    "{request.user_query}"
    
    Return JSON format:
    {{
        "from": "departure city",
        "to": "destination city",
        "departure_date": "YYYY-MM-DD",
        "return_date": "YYYY-MM-DD",
        "budget_per_night": "integer",
        "accommodation_preferences": "list",
        "flight_preferences": "list",
        "activities": "list"
    }}
    """
    
    response = model.generate_content(prompt)
    return response.text
    