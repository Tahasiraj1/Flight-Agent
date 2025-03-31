from playwright.sync_api import sync_playwright
import time


def search_flights(from_city, to_city, departure_date, return_date):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open Google Flights
        page.goto("https://www.google.com/travel/flights")
        page.wait_for_selector("input[aria-label='Where from?']")
        
        # Enter Departure City
        from_input = from_input = page.locator("input[aria-label='Where from?']")
        time.sleep(1)
        from_input.fill(from_city)
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)      

        # Enter Destination City
        to_input = page.locator("input[aria-label='Where to?']")
        time.sleep(1)
        to_input.fill(to_city)
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)

        # Click on Departure Date Picker
        page.click("div[aria-label='Departure']")
        time.sleep(1)
        page.click(f"div[data-day='{departure_date}']")
        time.sleep(1)

        # Click on Return Date Picker
        page.click("div[aria-label='Return']")
        time.sleep(1)
        page.click(f"div[data-day='{return_date}']")
        time.sleep(1)

        # Click Done button
        page.click("button[aria-label='Done']")
        time.sleep(1)

        # Click Search
        page.keyboard.press("Enter")
        print("🔍 Searching for flights...")

        # Wait for results to load
        page.wait_for_selector("div[role='main']", timeout=15000)
        print("✅ Flights loaded successfully!")

        # 🛑 Wait until flight prices appear
        page.wait_for_selector('div[aria-label*="$"]', timeout=15000)  

        # ✅ Extract flight details
        flight_prices = page.locator('div[aria-label*="$"]').all_inner_texts()
        airline_names = page.locator('div[aria-label*="Operated by"]').all_inner_texts()
        flight_durations = page.locator('div[aria-label*="hour"]').all_inner_texts()

        # 🖨 Print extracted data
        print("\n✈️ Flight Prices:")
        print(flight_prices)

        print("\n🏷 Airline Names:")
        print(airline_names)

        print("\n⏳ Flight Durations:")
        print(flight_durations)

        # Close browser
        browser.close()

        # Return data for further use
        return {
            "prices": flight_prices,
            "airlines": airline_names,
            "durations": flight_durations
        }


# Run the scraper
flights_data = search_flights("New York", "Bangkok", "2025-05-01", "2025-05-15")

# Check extracted data
print("\n🔹 Final Extracted Flight Data:", flights_data)
