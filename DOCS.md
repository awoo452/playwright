# Playwright Basic AI Navigation

Usage:
- Navigate to the directory containing this file.
- Run the basic navigation script with: python3 playwright_basic_nav.py

Description:
- Opens a Chromium instance and navigates to "getawd.com".
- Prints the page title, then closes the browser.

# Link + Image Audit (Playwright)

Usage:
- Run the audit script with: python3 link_audit_playwright.py

Description:
- Loads the landing page and collects links + images from the DOM.
- Checks each URL with Playwright's request client.
- Prints "BROKEN LINK" or "BROKEN IMAGE" lines for failures.
- Returns exit code 1 if any broken items are found.
