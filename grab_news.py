import json
import os
import time
import traceback
import codecs
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telepot
import cloudscraper
from post import postToTelegraph

# Load environment variables
load_dotenv()

# Constants
HOMEPAGE = "https://www.prothomalo.com/"
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SAVED_URLS_PATH = os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt')

# Initialize bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN or CHAT_ID is not set in the environment variables.")

bot = telepot.Bot(BOT_TOKEN)

# Helper Functions
def get_html(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def load_previous_slugs():
    try:
        with open(SAVED_URLS_PATH, 'r', encoding='utf-8') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []
    except UnicodeDecodeError:
        with codecs.open(SAVED_URLS_PATH, 'r', 'utf-8') as file:
            return file.read().splitlines()

def save_slugs(slugs):
    with open(SAVED_URLS_PATH, 'w', encoding='utf-8') as file:
        file.write("\n".join(slugs))

def append_slugs(slugs):
    with open(SAVED_URLS_PATH, 'a', encoding='utf-8') as file:
        for slug in slugs:
            file.write(f"{slug}\n")

def fetch_article_data(slug):
    page = get_html(slug)
    script_data = page.find_all('script')
    try:
        article_json = json.loads(script_data[2].string)
        article_body = article_json["articleBody"].replace("&lt;", "<").replace("&gt;", ">")
        image_url = article_json.get("hero-image-s3-key", "-")
        if 'https://images.prothomalo.com/' not in image_url:
            image_url = f"https://images.prothomalo.com/{image_url}"
        return article_body, image_url
    except Exception as e:
        raise ValueError(f"Error fetching article data: {e}")

# Main Function
def check_and_notify():
    data = json.loads(get_html(HOMEPAGE).find(id="static-page").string)
    articles = data["qt"]["data"]["collection"]["items"]

    # Extract article details
    new_articles = []
    for category in articles:
        for item in category.get("items", []):
            try:
                story = item["story"]
                new_articles.append({
                    "slug": story["url"],
                    "author": story["author-name"],
                    "headline": story["headline"],
                    "image": story.get("alternative", {}).get("home", {}).get("default", {}).get("hero-image", {}).get("hero-image-s3-key", "-")
                })
            except KeyError:
                continue

    previous_slugs = load_previous_slugs()

    # Filter new articles
    filtered_articles = [article for article in new_articles if article["slug"] not in previous_slugs]

    if filtered_articles:
        append_slugs([article["slug"] for article in filtered_articles])

        for article in filtered_articles:
            try:
                if any(ignored in article["slug"] for ignored in ["photo/", "entertainment/", "video/"]):
                    continue

                article_body, image_url = fetch_article_data(article["slug"])
                telegraph_link = postToTelegraph(article["headline"], article["author"], image_url, article_body, article["slug"])

                message = f"<a href='{telegraph_link['url']}'>{article['headline']} - প্রথম আলো</a>"
                bot.sendMessage(CHAT_ID, message, parse_mode='html')

                time.sleep(15)
            except Exception:
                print(traceback.format_exc())
    else:
        print("[grab_news.py] No new articles to process.")

if __name__ == "__main__":
    check_and_notify()
