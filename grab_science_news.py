import os
import json
import time
import traceback
import codecs
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import telepot
import cloudscraper
from post import postToTelegraph

# Load environment variables
load_dotenv()

# Constants
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
URLS_FILE = os.path.join(__location__, 'newspaper-bot-urls/pa-science-saved-urls.txt')
HOMEPAGES = [
    "https://www.prothomalo.com/technology",
    "https://www.prothomalo.com/education/science-tech"
]

# Initialize bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('SCIENCE_CHAT_ID')
ERROR_MESSAGE_CHAT_ID = os.getenv('ERROR_MESSAGE_CHAT_ID')
bot = telepot.Bot(BOT_TOKEN)

def get_html(url):
    """Fetch and parse HTML from a URL using cloudscraper."""
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def load_previous_urls():
    """Load previously processed URLs from file."""
    try:
        with open(URLS_FILE, 'r') as file:
            return file.read().splitlines()
    except UnicodeDecodeError:
        with codecs.open(URLS_FILE, 'r', 'utf8') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def save_urls(urls):
    """Save a list of URLs to file."""
    with open(URLS_FILE, 'w') as file:
        for url in urls:
            file.write(f"{url}\n")

def append_new_urls(urls):
    """Append new URLs to the file."""
    with open(URLS_FILE, 'a+') as file:
        for url in urls:
            file.write(f"{url}\n")

def process_article(article):
    """Extract article details and post to Telegram."""
    headline = article.get("headline")
    author_name = article.get("author-name", "-")
    url = article.get("url")

    if not url:
        return None

    page_content = get_html(url)
    scripts = page_content.find_all('script', {"type": "application/ld+json"})

    for script in scripts:
        try:
            data = json.loads(script.string)
            article_body = data.get("articleBody", "")
        except (json.JSONDecodeError, AttributeError):
            continue

    article_body = article_body.replace("&lt;", "<").replace("&gt;", ">")
    image_url = page_content.find("meta", property="og:image").get("content", "")

    telegraph_response = postToTelegraph(headline, author_name, image_url, article_body, url)
    telegraph_url = telegraph_response.get("url")

    if telegraph_url:
        text = f"<a href='{telegraph_url}'>{headline} - প্রথম আলো</a>"
        bot.sendMessage(CHAT_ID, text, parse_mode='html')

    return url

def process_homepage(homepage, prev_urls):
    """Process articles from a homepage."""
    new_urls = []
    html_soup = get_html(homepage)

    try:
        data = json.loads(html_soup.find(id="static-page").string)
        articles = data["qt"]["data"]["collection"]["items"]
    except (AttributeError, json.JSONDecodeError):
        bot.sendDocument(ERROR_MESSAGE_CHAT_ID, open("science_page_sample.html", "rb"), caption="Error parsing homepage data.")
        return []

    for article in articles:
        story = article.get("story") or {}
        url = process_article(story)

        if url and url not in prev_urls:
            new_urls.append(url)

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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        bot.sendMessage(ERROR_MESSAGE_CHAT_ID, f"Error: {str(e)}")