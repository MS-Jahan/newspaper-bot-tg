import json
import os
import time
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telepot
from scraper_utils import (
    get_html,
    load_urls_from_file,
    append_urls_to_file,
    trim_url_file,
)

# Load environment variables
load_dotenv()

# Constants
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("SCIENCE_CHAT_ID")
ERROR_CHAT_ID = os.getenv("ERROR_MESSAGE_CHAT_ID")
SAVED_URLS_FILE = "newspaper-bot-urls/ridmik-science-saved-urls.txt"
HOMEPAGE_URL = "https://ridmik.news/topic/12/technology"
URL_LIMIT = 300
URL_TRIM_COUNT = 60
SEND_DELAY = 5

# Initialize Telegram bot
bot = telepot.Bot(BOT_TOKEN)


# Utility functions
def load_saved_urls(filepath):
    # Ensure file exists
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        open(filepath, "w").close()
    return load_urls_from_file(filepath)


def save_urls(filepath, urls):
    append_urls_to_file(filepath, urls)


def trim_urls(filepath, urls):
    return trim_url_file(filepath, max_urls=URL_LIMIT, trim_count=URL_TRIM_COUNT)


def fetch_articles(homepage_url):
    webpage = get_html(homepage_url)
    script_tag = webpage.find("script", {"id": "__NEXT_DATA__"})
    if not script_tag or not script_tag.text:
        print("[grab_ridmik_science_news.py] No __NEXT_DATA__ script found")
        return []

    json_data = json.loads(script_tag.text)

    articles = []
    try:
        articles += [
            {
                "link": f"https://ridmik.news/article/{article['aid']}/{article['title'].replace(' ', '-')}",
                "title": article["title"],
            }
            for article in json_data["props"]["pageProps"].get("articles", [])
        ]
    except Exception:
        print(traceback.format_exc())

    try:
        home_articles = json_data["props"]["pageProps"].get("homeArticles", {})
        articles += [
            {
                "link": f"https://ridmik.news/article/{value['aid']}/{value['title'].replace(' ', '-')}",
                "title": value["title"],
            }
            for value in home_articles.values()
        ]
    except Exception:
        print(traceback.format_exc())

    return articles


def send_to_telegram(articles, prev_urls):
    new_urls = []
    for index, article in enumerate(articles):
        link = article["link"]
        title = article["title"]
        if link not in prev_urls:
            try:
                print(f"[grab_ridmik_science_news.py] Sending link {index + 1}: {link}")
                text = (
                    f"<a href='https://t.me/iv?url={link}&rhash=e70d349033f6bb'>"
                    f"{title} - Ridmik News</a>"
                )
                bot.sendMessage(CHAT_ID, text, parse_mode="html")
                new_urls.append(link)
                time.sleep(SEND_DELAY)
            except Exception:
                print(traceback.format_exc())
    return new_urls


# Main function
def main():
    saved_urls_path = os.path.join(os.getcwd(), SAVED_URLS_FILE)
    prev_urls = load_saved_urls(saved_urls_path)
    prev_urls = trim_urls(saved_urls_path, prev_urls)

    articles = fetch_articles(HOMEPAGE_URL)
    new_urls = send_to_telegram(articles, prev_urls)

    save_urls(saved_urls_path, new_urls)


if __name__ == "__main__":
    main()
