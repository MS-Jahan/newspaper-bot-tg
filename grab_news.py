import json
import os
import time
import traceback
import codecs
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telepot
from post import postToTelegraph
from scraper_utils import (
    get_html,
    iter_story_items,
    load_urls_from_file,
    save_urls_to_file,
    DEFAULT_HEADERS,
)
from gitt import commit_file

# Load environment variables
load_dotenv()

# Constants
HOMEPAGE = "https://www.prothomalo.com/"
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SAVED_URLS_PATH = os.path.join(__location__, "newspaper-bot-urls/saved-urls.txt")

# Initialize bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN or CHAT_ID is not set in the environment variables.")

bot = telepot.Bot(BOT_TOKEN)


# Helper Functions
def load_previous_slugs():
    return load_urls_from_file(SAVED_URLS_PATH)


def save_slugs(slugs):
    save_urls_to_file(SAVED_URLS_PATH, slugs)


def append_slugs(slugs):
    with open(SAVED_URLS_PATH, "a", encoding="utf-8") as file:
        for slug in slugs:
            file.write(f"{slug}\n")


def fetch_article_data(slug):
    page = get_html(slug)
    script_data = page.find_all("script")
    try:
        script_content = script_data[2].string or ""
        if not script_content:
            raise ValueError("Missing article JSON")
        article_json = json.loads(script_content)
        article_body = (
            article_json["articleBody"].replace("&lt;", "<").replace("&gt;", ">")
        )
        image_url = article_json.get("hero-image-s3-key", "-")
        if "https://images.prothomalo.com/" not in image_url:
            image_url = f"https://images.prothomalo.com/{image_url}"
        return article_body, image_url
    except Exception as e:
        raise ValueError(f"Error fetching article data: {e}")


# Main Function
def check_and_notify():
    static_page = get_html(HOMEPAGE).find(id="static-page")
    if not static_page or not static_page.string:
        raise ValueError("Missing static-page data")
    data = json.loads(static_page.string)
    articles = data["qt"]["data"]["collection"]["items"]

    # Extract article details
    new_articles = []
    for story in iter_story_items(articles):
        url = story.get("url")
        if not url:
            continue
        alternative = story.get("alternative") or {}
        new_articles.append(
            {
                "slug": url,
                "author": story.get("author-name", "-"),
                "headline": story.get("headline"),
                "image": alternative.get("home", {})
                .get("default", {})
                .get("hero-image", {})
                .get("hero-image-s3-key", "-"),
            }
        )

    previous_slugs = load_previous_slugs()

    # Filter new articles
    filtered_articles = [
        article for article in new_articles if article["slug"] not in previous_slugs
    ]

    if filtered_articles:
        append_slugs([article["slug"] for article in filtered_articles])
        commit_file(SAVED_URLS_PATH, "grab_news: Added new Prothom Alo URLs")

        for article in filtered_articles:
            try:
                if any(
                    ignored in article["slug"]
                    for ignored in ["photo/", "entertainment/", "video/"]
                ):
                    continue

                article_body, image_url = fetch_article_data(article["slug"])
                telegraph_link = postToTelegraph(
                    article["headline"],
                    article["author"],
                    image_url,
                    article_body,
                    article["slug"],
                )

                message = f"<a href='{telegraph_link['url']}'>{article['headline']} - প্রথম আলো</a>"
                bot.sendMessage(CHAT_ID, message, parse_mode="html")

                time.sleep(15)
            except Exception:
                print(traceback.format_exc())
    else:
        print("[grab_news.py] No new articles to process.")


if __name__ == "__main__":
    check_and_notify()
