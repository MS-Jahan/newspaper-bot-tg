import os
import json
import traceback
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telepot
from post import postToTelegraph

# Constants
BASE_URL = "https://www.kalerkantho.com"
TECHNEWS_URL = f"{BASE_URL}/online/info-tech"
SAVED_URLS_FILE_NAME = "newspaper-bot-urls/kk-science-saved-urls.txt"
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Utility Functions
def get_html(url):
    """Fetches and parses the HTML content of a given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def load_saved_urls(file_path):
    """Loads previously saved URLs from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().splitlines()
    except (UnicodeDecodeError, FileNotFoundError):
        print("[grab_kalerkontho_science_news.py] Error reading saved URLs file. Attempting fallback handling.")
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().splitlines()
        except Exception as e:
            print(f"[grab_kalerkontho_science_news.py] Failed to read saved URLs file: {e}")
            return []

def save_urls(file_path, urls):
    """Saves a list of URLs to a file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(f"{url}\n")

def append_urls(file_path, urls):
    """Appends new URLs to the saved file."""
    with open(file_path, 'a', encoding='utf-8') as file:
        for url in urls:
            file.write(f"{url}\n")

def clean_article_text(article_text):
    """Cleans and formats the article text."""
    return (
        article_text
        .replace("\u0026amp;", "&")
        .replace("nbsp;", " ")
        .replace("\u0026lt;/p\u0026gt;", "</p>")
        .replace("\u0026lt;p\u0026gt;", "<p>")
    )

# Main Function
def check_tech_news():
    load_dotenv()

    bot = telepot.Bot(os.getenv('BOT_TOKEN'))
    chat_id = os.getenv('SCIENCE_CHAT_ID')
    saved_urls_file_path = os.path.join(__location__, SAVED_URLS_FILE_NAME)

    prev_urls = load_saved_urls(saved_urls_file_path)
    new_urls = []
    new_titles = []

    if prev_urls:
        try:
            soup = get_html(TECHNEWS_URL)
            links = soup.find_all("a")

            for element in links:
                href = element.get("href", "")
                if len(href) > 24 and "/online/info-tech/" in href:
                    full_url = f"{BASE_URL}{href}"
                    if full_url not in prev_urls:
                        try:
                            title_text = element.find("h4").text
                            new_urls.append(full_url)
                            new_titles.append(title_text)
                        except AttributeError:
                            print("[grab_kalerkontho_science_news.py] Invalid link format.")

            # Trim saved URLs if necessary
            if len(prev_urls) > 300:
                prev_urls = prev_urls[60:]
                save_urls(saved_urls_file_path, prev_urls)

            # Process new URLs
            for i, link in enumerate(new_urls):
                if link not in prev_urls:
                    try:
                        webpage = get_html(link)
                        image = webpage.find("meta", property="og:image").get("content")
                        headline = webpage.find("title").text
                        json_data = json.loads(webpage.find("script", {"id": "__NEXT_DATA__"}).text)
                        author_name = json_data["props"]["pageProps"]["details"]["n_author"]
                        article = clean_article_text(json_data["props"]["pageProps"]["details"]["n_details"])

                        iv_link = postToTelegraph(headline, author_name, image, article, link)

                        text = f"<a href='{iv_link['url']}'>{headline} - কালের কণ্ঠ</a>"
                        bot.sendMessage(chat_id, text, parse_mode='html')
                    except Exception as e:
                        print(f"[grab_kalerkontho_science_news.py] Error processing link {link}: {traceback.format_exc()}")

            # Save new URLs
            if new_urls:
                append_urls(saved_urls_file_path, new_urls)

        except Exception as e:
            print(f"[grab_kalerkontho_science_news.py] Failed to fetch or process tech news: {traceback.format_exc()}")
    else:
        print("[grab_kalerkontho_science_news.py] No saved URLs found or failed to load.")

if __name__ == "__main__":
    check_tech_news()
