import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
from agents import Runner
from flight_agent import flight_agent
from utils import set_user_query
from google_flights_scraper import search_flights
from utils import query_parser
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
            from_city, to_city, departure_date, return_date = query_parser(user_query)
        except ValueError as e:
            st.error(f"Error: {str(e)}")
            st.stop()
        
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
