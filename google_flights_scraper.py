from playwright.sync_api import sync_playwright
import time

# Extract all the flights from the provided HTML
def extract_best_flights(page):
    """Extracts the top 3 best flights from the provided HTML."""
    flights = []
    
    # Wait for flights to load
    page.wait_for_selector("ul.Rk10dc > li.pIav2d", timeout=15000)
    
    # Locate all flight elements
    flight_elements = page.locator("ul.Rk10dc > li.pIav2d").all()
    print(f"✅ Found {len(flight_elements)} flights!")

    for element in flight_elements:  # Extract all flights
        flight = {}
        try:
            # Extract price
            price_element = element.locator("div.BVAVmf span[aria-label]").first
            flight["price"] = price_element.get_attribute("aria-label") if price_element else "N/A"
        except:
            flight["price"] = "Price not found"

        try:
            # Extract airline
            airline_element = element.locator("span.h1fkLb").first
            flight["airline"] = airline_element.text_content().strip() if airline_element else "Airline not found"
        except:
            flight["airline"] = "Airline not found"

        try:
            # Extract departure time
            departure_time_element = element.locator("div[aria-label^='Departure time']")
            flight["departure_time"] = departure_time_element.text_content().strip() if departure_time_element else "Departure time not found"
        except:
            flight["departure_time"] = "Departure time not found"

        try:
            # Extract arrival time
            arrival_time_element = element.locator("div[aria-label^='Arrival time']")
            flight["arrival_time"] = arrival_time_element.text_content().strip() if arrival_time_element else "Arrival time not found"
        except:
            flight["arrival_time"] = "Arrival time not found"

        try:
            # Extract duration
            duration_element = element.locator("div[aria-label^='Total duration']")
            flight["duration"] = duration_element.text_content().strip() if duration_element else "Duration not found"
        except:
            flight["duration"] = "Duration not found"

        try:
            # Extract stops
            stops_element = element.locator("span.VG3hNb")
            flight["stops"] = stops_element.text_content().strip() if stops_element else "Stops not found"
        except:
            flight["stops"] = "Stops not found"
        try:
            # Extract Layover
            layover_element = element.locator("div.tvtJdb.eoY5cb.y52p7d").first()
            flight["layover"] = layover_element.inner_text().strip() if layover_element else "Layover not found"
        except:
            flight["layover"] = "Layover not found"

        flights.append(flight)

    return flights

# Automatically search for flights
def search_flights(from_city, to_city, departure_date, return_date):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open Google Flights
        page.goto("https://www.google.com/travel/flights")
        page.wait_for_selector("input[aria-label='Where from?']")
        
        # Enter Departure City
        from_input = page.locator("input[aria-label='Where from?']")
        from_input.fill(from_city)
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)      

        # Enter Destination City
        to_input = page.locator("input[aria-label^='Where to']")
        to_input.fill(to_city)
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)

        # Click on Departure Date Picker
        departure_input = page.locator("input[aria-label^='Departure']").first
        departure_input.fill(departure_date)
        time.sleep(1)

        # Click on Return Date Picker
        return_input = page.locator("input[aria-label^='Return']").first
        return_input.fill(return_date)
        time.sleep(1)
        return_input.fill(return_date)

        # Click Done button
        page.click("button[aria-label='Search']")
        time.sleep(1)

        # Click Search
        page.keyboard.press("Enter")
        print("🔍 Searching for flights...")

        # Wait for results to load
        page.wait_for_selector("div[role='main']", timeout=15000)
        print("✅ Flights loaded successfully!")

        best_flights = extract_best_flights(page)

        # Close browser
        browser.close()

        # Return data for further use
        return best_flights
