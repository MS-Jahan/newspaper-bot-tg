import os
import time
import traceback
import codecs
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telepot

# Load environment variables
load_dotenv()

# Constants and Globals
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ERROR_MESSAGE_CHAT_ID = os.getenv('ERROR_MESSAGE_CHAT_ID')
SAVED_URLS_FILE_NAME = os.path.join(__location__, "newspaper-bot-urls/bbc-saved-urls.txt")
BOGUS_LINKS_FILE = os.path.join(__location__, 'bbc-bangla-bogus-links.txt')
CURRENT_YEAR = str(time.strftime("%Y"))

# Initialize bot
bot = telepot.Bot(BOT_TOKEN)

# Utility functions
def read_file_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().splitlines()
    except UnicodeDecodeError:
        with codecs.open(file_path, 'r', 'utf-8') as file:
            return file.read().splitlines()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

def write_file_lines(file_path, lines):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(lines))

def append_file_lines(file_path, lines):
    with open(file_path, 'a+', encoding='utf-8') as file:
        for line in lines:
            file.write(f"{line}\n")

def get_html(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    return BeautifulSoup(response.text, 'html.parser')

# Core logic
def process_index_pages(homepages, bogus_links, prev_urls):
    links_from_index_pages = []
    post_links = []
    post_titles = []

    for homepage in homepages:
        html_soup = get_html(homepage)
        save_html_to_file(html_soup, 'bbc-bangla-index-pages.html')

        links_in_homepage = html_soup.find_all('a')

        for tag in links_in_homepage:
            href = tag.get('href', '').rstrip('/')
            if href and "bbc.co" not in href:
                href = f"https://www.bbc.com{href}"

            if href not in bogus_links and href not in prev_urls:
                if "bbc_bangla_radio" not in href and "live/" not in href:
                    links_from_index_pages.append(href)

    links_from_index_pages = list(dict.fromkeys(links_from_index_pages))

    for i, link in enumerate(links_from_index_pages):
        try:
            soup = get_html(link)
            title = soup.find("title").text
            time_tag = soup.find("time")

            if time_tag and CURRENT_YEAR in time_tag.get("datetime", ""):
                post_links.append(link)
                post_titles.append(title)
        except Exception:
            print(traceback.format_exc())

    return post_links, post_titles

def send_links_to_telegram(post_links, post_titles):
    new_urls = []
    for index, link in enumerate(post_links):
        try:
            text = f"<a href='https://t.me/iv?url={link}&rhash=b4f88771c2ae04'>{post_titles[index]} - বিবিসি বাংলা</a>"
            bot.sendMessage(CHAT_ID, text, parse_mode='html')
            new_urls.append(link)
            time.sleep(5)
        except Exception:
            print(traceback.format_exc())
    return new_urls

def save_html_to_file(html_soup, filename):
    file_path = os.path.join(__location__, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(html_soup))
    bot.sendDocument(ERROR_MESSAGE_CHAT_ID, open(file_path, 'rb'), caption="HTML saved")

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
