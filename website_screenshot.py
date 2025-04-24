from playwright.sync_api import sync_playwright
import os
from urllib.parse import urljoin, urlparse
import time

def take_screenshots(playwright, base_url, output_dir, visited=None):
    if visited is None:
        visited = set()

    # Launch the browser
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    def save_screenshot(url, filename):
        try:
            # Navigate to the URL with a timeout
            page.goto(url, timeout=30000)  # 30 seconds timeout
            page.wait_for_load_state("networkidle", timeout=30000)

            # Incrementally scroll to trigger lazy-loaded elements
            scroll_height = page.evaluate("document.body.scrollHeight")
            while True:
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(1)
                new_scroll_height = page.evaluate("document.body.scrollHeight")
                if new_scroll_height == scroll_height:
                    break
                scroll_height = new_scroll_height

            # Hide the chatbot (adjust the selector based on the chatbot's HTML structure)
            page.evaluate("""
                const chatbot = document.querySelector('chatway--container has-loaded'); 
                if (chatbot) {
                    chatbot.style.display = 'none';
                }
            """)

            # Ensure all images are loaded
            page.evaluate("""
                (async () => {
                    const images = Array.from(document.images);
                    await Promise.all(images.map(img => {
                        if (!img.complete) {
                            return new Promise(resolve => img.onload = resolve);
                        }
                        return Promise.resolve();
                    }));
                })();
            """)

            # Take a full-page screenshot
            page.screenshot(path=os.path.join(output_dir, filename), full_page=True)
            print(f"Screenshot saved: {filename}")

        except Exception as e:
            print(f"Error processing {url}: {e}")

    def get_links():
        return [
            urljoin(base_url, link.get_attribute("href"))
            for link in page.query_selector_all("a[href]")
        ]

    # Visit the base URL
    visited.add(base_url)
    os.makedirs(output_dir, exist_ok=True)
    save_screenshot(base_url, "homepage.png")

    # Extract and visit links
    for link in get_links():
        if link not in visited and urlparse(link).netloc == urlparse(base_url).netloc:
            visited.add(link)
            filename = f"{urlparse(link).path.strip('/').replace('/', '_') or 'index'}.png"
            save_screenshot(link, filename)

    # Close the browser
    browser.close()

with sync_playwright() as playwright:
    take_screenshots(
        playwright,
        base_url="https://bfl.org.bt/",
        output_dir="C:/Users/Creative/Desktop/Bhutan For Life Website Case Study"
    )
