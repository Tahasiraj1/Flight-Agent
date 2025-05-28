import google.generativeai as genai
import json
import re
import os

user_query = None


def set_user_query(query: str) -> str:
    global user_query
    user_query = query


def get_user_query() -> str:
    global user_query
    return user_query


api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("Please set the GEMINI_API_KEY environment variable")


def query_parser(user_query: str):
    """Parse the user query and extract the relevant information"""
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
        raise ValueError(
            f"Failed to extract JSON from Gemini response: {raw_response}")

    travel_details = json.loads(json_text)

    # Extract structured fields
    from_city = travel_details.get("from_city")
    to_city = travel_details.get("to_city")
    departure_date = travel_details.get("departure_date")
    return_date = travel_details.get("return_date")

    return from_city, to_city, departure_date, return_date
