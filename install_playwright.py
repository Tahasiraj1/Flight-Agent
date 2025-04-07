import os
from playwright.sync_api import sync_playwright

def install_playwright_browsers():
    if not os.path.exists('/root/.cache/ms-playwright'):
        print("Installing Playwright browsers...")
        with sync_playwright() as p:
            p.install()

if __name__ == "__main__":
    install_playwright_browsers()
