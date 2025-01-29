import os
import time
import traceback
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from dotenv import load_dotenv
import telepot
from helpers import *

# Load environment variables
load_dotenv()

# Constants
HEADERS = {
    'Host': 'www.nu.ac.bd',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
SAVED_URLS_FILE = "newspaper-bot-urls/nu_notices.txt"
ERROR_MESSAGE_CHAT_ID = os.getenv('ERROR_MESSAGE_CHAT_ID')
NU_CHAT_ID = os.getenv('NATIONAL_UNIVERSITY_CHAT_ID')

# Initialize bot
NU_BOT = telepot.Bot(os.getenv('BOT_TOKEN'))

# Keyword mappings
PORIKKHA_KEYWORDS = {
    ("পরীক্ষা",): "Exam",
    ("পরীক্ষার সময়সূচী", "পরীক্ষার সময়সূচি"): "Exam Schedule",
    ("ফরম পূরণ",): "Form Fillup",
    ("ফলাফল",): "Result",
}

OTHER_KEYWORDS = {
    ("১ম বর্ষ", "প্রথম বর্ষ"): "1st Year",
    ("২য় বর্ষ", "দ্বিতীয় বর্ষ"): "2nd Year",
    ("৩য় বর্ষ", "তৃতীয় বর্ষ"): "3rd Year",
    ("৪র্থ বর্ষ", "চতুর্থ বর্ষ"): "4th Year",
    ("১ম সেমিস্টার", "প্রথম সেমিস্টার"): "1st Semester",
    ("২য় সেমিস্টার", "দ্বিতীয় সেমিস্টার"): "2nd Semester",
    ("৩য় সেমিস্টার", "তৃতীয় সেমিস্টার"): "3rd Semester",
    ("৪র্থ সেমিস্টার", "চতুর্থ সেমিস্টার"): "4th Semester", 
    ("CSE", "সিএসই"): "CSE",
    ("ECE", "ইসিই"): "ECE",
    ("BBA","বিবিএ"): "BBA",
    ("Professional", "প্রফেশনাল"): "Professional",
    ("MBA", "এমবিএ"): "MBA",
    ("অনার্স", "Honours"): "Honours",
    ("মাস্টার্স", "Masters"): "Masters",
    ("ডিপ্লোমা", "Diploma"): "Diploma",
    ("সার্টিফিকেট", "Certificate"): "Certificate",
    ("বিএসসি", "BSc"): "BSc",
    ("বিকম", "BCom"): "BCom",
    ("বিএ", "BA"): "BA",
    ("পোস্ট গ্র্যাজুয়েট", "Post Graduate"): "Post Graduate",
    ("এমএ", "MA"): "MA",
    ("এমকম", "MCom"): "MCom",
    ("এমএসসি", "MSc"): "MSc",
    ("বিএড", "BEd"): "BEd",
    ("এমএড", "MEd"): "MEd",
}

# Utility functions
def load_previous_links(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def save_new_links(file_path, links):
    with open(file_path, 'a') as file:
        for link in links:
            file.write(f"{link}\n")

def send_error_message(message):
    try:
        NU_BOT.sendMessage(ERROR_MESSAGE_CHAT_ID, message)
    except Exception:
        print("Failed to send error message.")

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, headers=headers, stream=True, verify=False) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename
    
# Core functions
def fetch_html(url):
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=50, verify=False)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException:
            print(f"Attempt {attempt + 1} failed. Retrying...")
            traceback.print_exc()
            time.sleep(5)

    send_error_message("Failed to fetch HTML after multiple attempts.")
    return None

def extract_notices(soup):
    if not soup:
        return []

    notices = []
    for div in soup.find_all("div", class_="news-item"):
        anchor = div.find("a", recursive=False)
        if anchor:
            title = anchor.text.strip()
            link = f"https://{quote('www.nu.ac.bd/' + anchor['href'])}"
            notices.append((title, link))
    return notices

def process_and_send_notices(notices, prev_links):
    new_links = [link for title, link in notices if link not in prev_links]
    save_new_links(SAVED_URLS_FILE, new_links)

    for title, link in notices:
        if link in new_links:
            reply = f"<a href='{link}'>{title}</a>\n\n"
            keywords = PORIKKHA_KEYWORDS | OTHER_KEYWORDS
            reply += " ".join(f"#{val.replace(' ', '_')}" for key, val in keywords.items() if any(k in title for k in key))

            try:
                filename = download_file(link)
                sent_message = NU_BOT.sendDocument(NU_CHAT_ID, open(filename, 'rb'), caption=reply, parse_mode='html')
                print(reply)
                if any(k in title for key in PORIKKHA_KEYWORDS for k in key):
                    NU_BOT.pinChatMessage(NU_CHAT_ID, sent_message['message_id'])
                    print("Pinned message")
                os.remove(filename)
            except Exception:
                traceback.print_exc()
                NU_BOT.sendMessage(NU_CHAT_ID, reply, parse_mode='html')
            time.sleep(3)

def main():
    print("Starting NU Notice Fetcher...")
    url = "https://www.nu.ac.bd/recent-news-notice.php"
    prev_links = load_previous_links(SAVED_URLS_FILE)
    soup = fetch_html(url)
    notices = extract_notices(soup)
    process_and_send_notices(notices, prev_links)

if __name__ == "__main__":
    main()
