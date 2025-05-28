from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError, Error as PlaywrightError
from agents import function_tool

async def extract_best_flights(page):
    """Extracts all flights from Google Flights page"""
    flights = []

    try:
        # Wait for flights to load
        await page.wait_for_selector("ul.Rk10dc > li.pIav2d", timeout=15000)
        
        # Locate all flight elements
        flight_elements = await  page.locator("ul.Rk10dc > li.pIav2d").all()
        print(f"✅ Found {len(flight_elements)} flights!")

        for element in flight_elements:  # Extract all flights
            flight = {}
            try:
                # Extract price
                price_element = element.locator("div.BVAVmf span[aria-label]").first
                flight["price"] = await price_element.get_attribute("aria-label") if price_element else "N/A"
            except Exception as e:
                print(f"Error in extracting price: {str(e)}")
                flight["price"] = "Price not found"

            try:
                # Extract airline
                airline_element = element.locator("span.h1fkLb").first
                flight["airline"] = (await airline_element.text_content()).strip() if airline_element else "Airline not found"
            except Exception as e:
                print(f"Error in extracting airline: {str(e)}")
                flight["airline"] = "Airline not found"

            try:
                # Extract departure time
                departure_time_element = element.locator("div[aria-label^='Departure time']")
                flight["departure_time"] = (await departure_time_element.text_content()).strip() if departure_time_element else "Departure time not found"
            except Exception as e:
                print(f"Error in extracting departure time: {str(e)}")
                flight["departure_time"] = "Departure time not found"

            try:
                # Extract arrival time
                arrival_time_element = element.locator("div[aria-label^='Arrival time']")
                flight["arrival_time"] = (await arrival_time_element.text_content()).strip() if arrival_time_element else "Arrival time not found"
            except Exception as e:
                print(f"Error in extracting arrival time: {str(e)}")
                flight["arrival_time"] = "Arrival time not found"

            try:
                # Extract duration
                duration_element = element.locator("div[aria-label^='Total duration']")
                flight["duration"] = (await duration_element.text_content()).strip() if duration_element else "Duration not found"
            except Exception as e:
                print(f"Error in extracting duration: {str(e)}")
                flight["duration"] = "Duration not found"

            try:
                # Extract stops
                stops_element = element.locator("span.VG3hNb")
                flight["stops"] = (await stops_element.text_content()).strip() if stops_element else "Stops not found"
            except Exception as e:
                print(f"Error in extracting stops: {str(e)}")
                flight["stops"] = "Stops not found"
            try:
                # Extract Layover
                layover_element = element.locator("div.tvtJdb.eoY5cb.y52p7d").first()
                flight["layover"] = (await layover_element.inner_text()).strip() if layover_element else "Layover not found"
            except Exception as e:
                print(f"Error in extracting layover: {str(e)}")
                flight["layover"] = "Layover not found"

            flights.append(flight)
        return flights
    except Exception as e:
        print(f"Error in extract_best_flights: {str(e)}")
        return [{"error": f"Failed to extract flights: {str(e)}"}]

@function_tool
async def search_flights(from_city: str, to_city: str, departure_date: str, return_date: str) -> list:
    """
    Search for flights based on the given criteria.

    Args:
        from_city: The departure city (e.g., "New York").
        to_city: The destination city (e.g., "Bangkok").
        departure_date: The departure date in YYYY-MM-DD format (e.g., "2025-06-01").
        return_date: The return date in YYYY-MM-DD format (e.g., "2025-06-15").

    Returns:
        A list of flight dictionaries containing price, airline, departure time, arrival time, duration, stops, and layover.
    """
    print(f"Received: from_city={from_city}, to_city={to_city}, departure_date={departure_date}, return_date={return_date}")
    try:
        async with async_playwright() as p:
            print("Launching Chromium browser...")
            browser = await p.chromium.launch(headless=False)  # Headless to avoid display issues
            page = await browser.new_page()
            print("Navigating to Google Flights...")
            await page.goto("https://www.google.com/travel/flights")
            await page.wait_for_selector("input[aria-label='Where from?']", timeout=15000)
            
            # Enter Departure City
            print("Filling departure city...")
            from_input = page.locator("input[aria-label='Where from?']")
            await from_input.fill(from_city)
            await page.wait_for_timeout(1000)
            await page.keyboard.press("ArrowDown")
            await page.wait_for_timeout(1000)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)

            # Enter Destination City
            print("Filling destination city...")
            to_input = page.locator("input[aria-label^='Where to']")
            await to_input.fill(to_city)
            await page.wait_for_timeout(1000)
            await page.keyboard.press("ArrowDown")
            await page.wait_for_timeout(1000)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)

            # Enter Departure Date
            print("Filling departure date...")
            departure_input = page.locator("input[aria-label^='Departure']").first
            await departure_input.fill(departure_date)
            await page.wait_for_timeout(1000)

            # Enter Return Date
            print("Filling return date...")
            return_input = page.locator("input[aria-label^='Return']").first
            await return_input.fill(return_date)
            await page.wait_for_timeout(1000)
            await return_input.fill(return_date)
            await page.wait_for_timeout(1000)

            # Click Search
            print("Submitting search...")
            await page.click("button[aria-label='Search']")
            await page.wait_for_timeout(1000)
            await page.keyboard.press("Enter")
            print("🔍 Searching for flights...")

            # Wait for results
            print("Waiting for results...")
            await page.wait_for_selector("div[role='main']", timeout=15000)
            print("✅ Flights loaded successfully!")

            flights_data = await extract_best_flights(page)
            await browser.close()
            return flights_data
    except TimeoutError as e:
        print(f"Playwright TimeoutError: {str(e)}")
        return [{"error": f"Timeout while scraping flights: {str(e)}"}]
    except PlaywrightError as e:
        print(f"Playwright Error: {str(e)}")
        return [{"error": f"Playwright error: {str(e)}"}]
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return [{"error": f"Unexpected error: {str(e)}"}]
