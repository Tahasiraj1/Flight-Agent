from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
from utils import get_user_query
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
    instructions=f"As a travel agent, your task is to extract the best flight from the provided raw flight data based on the user query and generate a clear, concise, and informative response. Additionally, you should explain why you selected that particular flight, highlighting the criteria it meets based on the user's preferences {user_query}.",
)