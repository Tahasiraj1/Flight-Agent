import asyncio    
from agents import Runner
from flight_agent import flight_agent
from utils import set_user_query
import streamlit as st

# --- UI Design ---

st.set_page_config(page_title="Your Personal Flight Agent", page_icon="✈️")
st.title("✈️ Your Personal Flight Agent")
st.subheader("Tell me where and when you want to fly!")

user_query = st.text_input("Enter your flight request:")

set_user_query(user_query)

if st.button("Search for Flights", use_container_width=True):
    with st.spinner("🔍 Processing your request and searching for flights..."):

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        with st.spinner("🤖 Asking the Flight Agent for the best option..."):
            result = Runner.run_sync(flight_agent, user_query)
            st.subheader("✨ Best Flight Recommendation:")
            st.markdown(f"{result.final_output}")
            print('final_output: ', result.final_output)
