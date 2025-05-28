from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, FunctionTool
from utils import get_user_query
from google_flights_scraper import search_flights
from instructions import FLIGHT_AGENT_INSTRUCTIONS
import os

set_tracing_disabled(disabled=True)

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

user_query = get_user_query()

flight_agent = Agent(
    name="Flight Agent",
    model=model,
    instructions=FLIGHT_AGENT_INSTRUCTIONS,
    tools=[search_flights]
)