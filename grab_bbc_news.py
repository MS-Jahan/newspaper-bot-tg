import os
import time
import traceback
import codecs
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telepot
from scraper_utils import (
    normalize_bbc_url,
    load_urls_from_file,
    save_urls_to_file,
    append_urls_to_file,
    fetch_url,
    DEFAULT_HEADERS,
)

# Load environment variables
load_dotenv()

# Constants and Globals
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ERROR_MESSAGE_CHAT_ID = os.getenv("ERROR_MESSAGE_CHAT_ID")
SAVED_URLS_FILE_NAME = os.path.join(
    __location__, "newspaper-bot-urls/bbc-saved-urls.txt"
)
BOGUS_LINKS_FILE = os.path.join(__location__, "bbc-bangla-bogus-links.txt")
CURRENT_YEAR = str(time.strftime("%Y"))

# Initialize bot
bot = telepot.Bot(BOT_TOKEN)


# Utility functions
def read_file_lines(file_path):
    return load_urls_from_file(file_path)


def write_file_lines(file_path, lines):
    save_urls_to_file(file_path, lines)


def append_file_lines(file_path, lines):
    append_urls_to_file(file_path, lines)


def get_html(url):
    # if there's no hostname in the URL, add "https://www.bbc.com" to it
    if not url.startswith("http"):
        url = f"https://www.bbc.com{url}"
    print(f"[grab_bbc_news.py] Fetching HTML from: {url}")
    response = fetch_url(url)
    return BeautifulSoup(response.text, "html.parser")


# Core logic
def process_index_pages(homepages, bogus_links, prev_urls):
    links_from_index_pages = []
    post_links = []
    post_titles = []

    for homepage in homepages:
        html_soup = get_html(homepage)
        save_html_to_file(html_soup, "bbc-bangla-index-pages.html")

        links_in_homepage = html_soup.find_all("a")

        for tag in links_in_homepage:
            raw_href = tag.get("href")
            if isinstance(raw_href, list):
                raw_href = raw_href[0] if raw_href else None
            elif not isinstance(raw_href, str):
                raw_href = None
            href = normalize_bbc_url(homepage, raw_href)
            if not href:
                continue

            if href not in bogus_links and href not in prev_urls:
                if "bbc_bangla_radio" not in href and "live/" not in href:
                    links_from_index_pages.append(href)

    links_from_index_pages = list(dict.fromkeys(links_from_index_pages))

    for link in links_from_index_pages:
        try:
            print(f"[grab_bbc_news.py] Processing link: {link}")
            soup = get_html(link)
            title_tag = soup.find("title")
            title = title_tag.text if title_tag else ""
            time_tag = soup.find("time")
            datetime_value = ""
            if time_tag:
                datetime_value = time_tag.get("datetime") or ""

            if time_tag and CURRENT_YEAR in datetime_value:
                post_links.append(link)
                post_titles.append(title)
        except Exception:
            print(f"[grab_bbc_news.py] Error processing link:")
            print(traceback.format_exc())

    return post_links, post_titles


def send_links_to_telegram(post_links, post_titles):
    new_urls = []
    for index, link in enumerate(post_links):
        try:
            text = f"<a href='https://t.me/iv?url={link}&rhash=b4f88771c2ae04'>{post_titles[index]} - বিবিসি বাংলা</a>"
            bot.sendMessage(CHAT_ID, text, parse_mode="html")
            new_urls.append(link)
            time.sleep(5)
        except Exception:
            print(traceback.format_exc())
    return new_urls


def save_html_to_file(html_soup, filename):
    file_path = os.path.join(__location__, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(html_soup))
    bot.sendDocument(ERROR_MESSAGE_CHAT_ID, open(file_path, "rb"), caption="HTML saved")


# Main function
def main():
    if not os.path.exists(SAVED_URLS_FILE_NAME):
        write_file_lines(SAVED_URLS_FILE_NAME, [])

    prev_urls = read_file_lines(SAVED_URLS_FILE_NAME)
    bogus_links = read_file_lines(BOGUS_LINKS_FILE)
    homepages = ["https://www.bbc.com/bengali"]

    post_links, post_titles = process_index_pages(homepages, bogus_links, prev_urls)

    new_urls = send_links_to_telegram(post_links, post_titles)

    append_file_lines(SAVED_URLS_FILE_NAME, new_urls)


if __name__ == "__main__":
    main()
