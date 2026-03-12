# Playwright Basic AI Navigation

"""
Usage:
    - Navigate to the directory containing this file.
    - Run the script with: python3 ai_dev_agent.py

Description:
    - This script opens a web browser window and navigates to "getawd.com".
    - Once the page is loaded, it prints the page title.
    - After printing the title, the browser window is closed automatically.
"""

from playwright.sync_api import sync_playwright

def main():
    """
    Launches a browser, navigates to 'https://getawd.com', prints the page title, and closes the browser.
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://getawd.com")
        print(f"Page Title: {page.title()}")
        browser.close()

if __name__ == "__main__":
    main()