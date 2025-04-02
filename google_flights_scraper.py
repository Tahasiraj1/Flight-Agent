from playwright.sync_api import sync_playwright
import time

def extract_best_flights(page):
    """Extracts the top 3 best flights from the provided HTML."""
    
    # Wait for the flight list to load
    page.wait_for_selector("ul.Rk10dc > li.pIav2d", timeout=15000)
    
    flight_elements = page.locator("ul.Rk10dc > li.pIav2d").all()
    
    for i in flight_elements[:1]:
        flight = i.inner_text()
        
    return flight


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
        


# Run the scraper
flights_data = search_flights("New York", "Bangkok", "2025-05-01", "2025-05-15")

# Check extracted data
print(f"\n🔹 Final Extracted Flight Data:\n{flights_data}\n", )