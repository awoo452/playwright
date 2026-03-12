from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/chromium",
        headless=False,
        args=[
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-features=VizDisplayCompositor"
            ]
    )

    context = browser.new_context()

    context.route("**/*.{png,jpg,jpeg,svg,gif}", lambda route: route.abort())
    
    page = context.new_page()

    print("Opening page...")

    page.goto("https://getawd.com", wait_until="domcontentloaded")

    print("Title:", page.title())

    browser.close()