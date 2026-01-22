import os
import json
import time
import traceback
import codecs
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import telepot
from post import postToTelegraph
from scraper_utils import (
    get_html,
    iter_story_items,
    load_urls_from_file,
    save_urls_to_file,
    append_urls_to_file,
    DEFAULT_HEADERS,
)
from gitt import commit_file

# Load environment variables
load_dotenv()

# Constants
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
URLS_FILE = os.path.join(__location__, "newspaper-bot-urls/pa-science-saved-urls.txt")
HOMEPAGES = [
    "https://www.prothomalo.com/technology",
    "https://www.prothomalo.com/education/science-tech",
]

# Initialize bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("SCIENCE_CHAT_ID")
ERROR_MESSAGE_CHAT_ID = os.getenv("ERROR_MESSAGE_CHAT_ID")
bot = telepot.Bot(BOT_TOKEN)


def load_previous_urls():
    """Load previously processed URLs from file."""
    return load_urls_from_file(URLS_FILE)


def save_urls(urls):
    """Save a list of URLs to file."""
    save_urls_to_file(URLS_FILE, urls)


def append_new_urls(urls):
    """Append new URLs to the file."""
    append_urls_to_file(URLS_FILE, urls)


def process_article(headline, author_name, url):
    """Extract article details and post to Telegram."""
    page_content = get_html(url)
    scripts = page_content.find_all("script", {"type": "application/ld+json"})
    article_body = ""

    for script in scripts:
        try:
            script_content = script.string or ""
            if not script_content:
                continue
            data = json.loads(script_content)
            article_body = data.get("articleBody", "")
        except (json.JSONDecodeError, AttributeError):
            continue

    article_body = article_body.replace("&lt;", "<").replace("&gt;", ">")
    image_tag = page_content.find("meta", property="og:image")
    image_url = image_tag.get("content", "") if image_tag else ""

    # print(headline, author_name, image_url, article_body, url)

    telegraph_response = postToTelegraph(
        headline, author_name, image_url, article_body, url
    )
    telegraph_url = telegraph_response.get("url")

    print(telegraph_url)

    if telegraph_url:
        text = f"<a href='{telegraph_url}'>{headline} - প্রথম আলো</a>"
        bot.sendMessage(CHAT_ID, text, parse_mode="html")

    return url


def process_homepage(homepage, prev_urls):
    """Process articles from a homepage."""
    new_urls = []
    html_soup = get_html(homepage)

    try:
        static_page = html_soup.find(id="static-page")
        if not static_page or not static_page.string:
            raise ValueError("Missing static-page data")
        data = json.loads(static_page.string)
        articles = data["qt"]["data"]["collection"]["items"]
    except (AttributeError, json.JSONDecodeError):
        bot.sendDocument(
            ERROR_MESSAGE_CHAT_ID,
            open("science_page_sample.html", "rb"),
            caption="Error parsing homepage data.",
        )
        return []

    for story in iter_story_items(articles):
        try:
            url = story.get("url")
            headline = story.get("headline")
            author_name = story.get("author-name", "-")

            print("[grab_science_news.py] url: ", url)

            if not url:
                continue

            if url not in prev_urls:
                url = process_article(headline, author_name, url)
                new_urls.append(url)
                time.sleep(2)
        except Exception:
            traceback.print_exc()
            continue

    return new_urls


def main():
    prev_urls = load_previous_urls()

    if len(prev_urls) > 300:
        prev_urls = prev_urls[-240:]  # Keep only the latest 240 entries
        save_urls(prev_urls)

    all_new_urls = []

    for homepage in HOMEPAGES:
        new_urls = process_homepage(homepage, prev_urls)
        all_new_urls.extend(new_urls)
        time.sleep(10)

    if all_new_urls:
        append_new_urls(all_new_urls)
        commit_file(URLS_FILE, "grab_science_news: Added new PA science URLs")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        bot.sendMessage(ERROR_MESSAGE_CHAT_ID, f"Error: {str(e)}")
