from __future__ import annotations

import sys
from typing import Iterable, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

TARGET_URL = "https://getawd.com/services"
EXECUTABLE_PATH = "/usr/bin/chromium"
HEADLESS = True
TIMEOUT_MS = 15_000

IGNORE_SCHEMES = {"mailto", "tel", "javascript", "data"}


def normalize_url(base_url: str, raw: str) -> Optional[str]:
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None

    parsed = urlparse(raw)
    if parsed.scheme in IGNORE_SCHEMES:
        return None

    if parsed.scheme in {"http", "https"}:
        return raw

    return urljoin(base_url, raw)


def parse_srcset(srcset: str) -> List[str]:
    urls: List[str] = []
    for part in srcset.split(","):
        candidate = part.strip().split(" ", 1)[0]
        if candidate:
            urls.append(candidate)
    return urls


def dedupe(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def collect_page_urls(page_url: str, links: Iterable[str], images: Iterable[str]) -> Tuple[List[str], List[str]]:
    normalized_links = [normalize_url(page_url, href) for href in links]
    normalized_images = [normalize_url(page_url, src) for src in images]

    link_urls = dedupe([u for u in normalized_links if u])
    image_urls = dedupe([u for u in normalized_images if u])

    return link_urls, image_urls


def check_urls(request, urls: Iterable[str], label: str) -> List[Tuple[str, Optional[int]]]:
    broken: List[Tuple[str, Optional[int]]] = []
    for url in urls:
        try:
            response = request.get(url, timeout=TIMEOUT_MS)
            status = response.status
        except Exception:
            status = None

        if status is None or status >= 400:
            broken.append((url, status))
            status_text = "no response" if status is None else str(status)
            print(f"BROKEN {label} [{status_text}] {url}")

    return broken


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=EXECUTABLE_PATH,
            headless=HEADLESS,
            args=["--disable-gpu"],
        )
        context = browser.new_context()
        page = context.new_page()

        print(f"Opening {TARGET_URL} ...")
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        link_hrefs = page.eval_on_selector_all(
            "a[href]",
            "elements => elements.map(el => el.getAttribute('href'))",
        )

        img_srcs = page.eval_on_selector_all(
            "img[src]",
            "elements => elements.map(el => el.getAttribute('src'))",
        )

        img_srcsets = page.eval_on_selector_all(
            "img[srcset]",
            "elements => elements.map(el => el.getAttribute('srcset'))",
        )

        srcset_urls: List[str] = []
        for srcset in img_srcsets:
            if not srcset:
                continue
            srcset_urls.extend(parse_srcset(srcset))

        link_urls, image_urls = collect_page_urls(
            TARGET_URL,
            link_hrefs,
            [*img_srcs, *srcset_urls],
        )

        print(f"Checking {len(link_urls)} links and {len(image_urls)} images...")
        broken_links = check_urls(context.request, link_urls, "LINK")
        broken_images = check_urls(context.request, image_urls, "IMAGE")

        browser.close()

    if broken_links or broken_images:
        total = len(broken_links) + len(broken_images)
        print(f"Found {total} broken items.")
        return 1

    print("No broken links or images found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
