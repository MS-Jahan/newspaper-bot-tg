import os
import time
import traceback
from curl_cffi import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from dotenv import load_dotenv
import telepot
from helpers import *
from gitt import commit_file

# Load environment variables
load_dotenv()

# Constants
HEADERS = {
    "Host": "www.nu.ac.bd",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}
SAVED_URLS_FILE = "newspaper-bot-urls/nu_notices.txt"
ERROR_MESSAGE_CHAT_ID = os.getenv("ERROR_MESSAGE_CHAT_ID")
NU_CHAT_ID = os.getenv("NATIONAL_UNIVERSITY_CHAT_ID")

# Initialize bot
NU_BOT = telepot.Bot(os.getenv("BOT_TOKEN"))

# Proxy Configuration
PROXY_SERVER_URL = os.getenv("PROXY_SERVER_URL")
PROXY_API_KEY = os.getenv("PROXY_API_KEY")

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
    ("BBA", "বিবিএ"): "BBA",
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
    print(f"[nunotice.py] Loading previously processed links from: {file_path}")
    try:
        with open(file_path, "r") as file:
            links = [line.strip() for line in file.read().splitlines()]
            print(f"[nunotice.py] Successfully loaded {len(links)} links")
            if links:
                print(f"[nunotice.py] First few links: {', '.join(links[:3])}")
                if len(links) > 3:
                    print(f"[nunotice.py] ... and {len(links) - 3} more")
            return links
    except FileNotFoundError:
        print(f"[nunotice.py] File not found: {file_path}. Creating a new list.")
        return []
    except Exception as e:
        print(f"[nunotice.py] Error loading links from {file_path}: {str(e)}")
        return []


def save_new_links(file_path, links):
    print(f"[nunotice.py] Saving {len(links)} new links to: {file_path}")
    try:
        with open(file_path, "a") as file:
            for i, link in enumerate(links):
                file.write(f"{link}\n")
                if i < 3:  # Only log the first few links
                    print(f"[nunotice.py] Saved link {i + 1}: {link}")
            if len(links) > 3:
                print(f"[nunotice.py] ... and {len(links) - 3} more links saved")
        print(f"[nunotice.py] Successfully saved all {len(links)} links to {file_path}")
    except Exception as e:
        print(f"[nunotice.py] Error saving links to {file_path}: {str(e)}")


def send_error_message(message):
    try:
        NU_BOT.sendMessage(ERROR_MESSAGE_CHAT_ID, message)
    except Exception:
        print("[nunotice.py] Failed to send error message.")


def make_request(url, headers=None, impersonate="chrome", timeout=60, verify=False, stream=False):
    """
    Makes a request either directly or via the configured proxy server.
    """
    if PROXY_SERVER_URL:
        print(f"[nunotice.py] Routing request for {url} through proxy: {PROXY_SERVER_URL}")
        try:
            payload = {
                "url": url,
                "headers": headers,
                "impersonate": impersonate,
                "timeout": timeout,
                "verify": verify,
                "stream": stream
            }
            proxy_headers = {}
            if PROXY_API_KEY:
                proxy_headers['X-API-KEY'] = PROXY_API_KEY

            response = requests.post(
                f"{PROXY_SERVER_URL}/fetch",
                json=payload,
                headers=proxy_headers,
                timeout=timeout + 10,  # Add buffer for proxy overhead
                stream=stream
            )
            
            # If proxy fails (500), it returns {"error": ...}
            if response.status_code == 500 and response.headers.get('content-type') == 'application/json':
                try:
                    # If streaming, we might need to read a bit to see error, 
                    # but typically 500 responses aren't huge streams.
                    # safer to just let it be or read if not streaming.
                    pass 
                except:
                    pass
            
            return response
        except Exception as e:
            print(f"[nunotice.py] Error communicating with proxy server: {e}")
            raise
    else:
        return requests.get(
            url,
            headers=headers,
            impersonate=impersonate,
            timeout=timeout,
            verify=verify,
            stream=stream
        )

def download_file(url):
    local_filename = url.split("/")[-1]
    print(f"[nunotice.py] Downloading file from {url}")
    print(f"[nunotice.py] Saving as {local_filename}")
    try:
        response = make_request(
            url,
            headers=HEADERS,
            impersonate="chrome",
            timeout=60,
            verify=False,
            stream=True
        )
        print(f"[nunotice.py] Download response status: {response.status_code}")
        response.raise_for_status()
        
        with open(local_filename, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        print(f"[nunotice.py] Download completed: {local_filename} ({downloaded / 1024:.2f} KB)")
        return local_filename
    except Exception as e:
        print(f"[nunotice.py] Error downloading file: {str(e)}")
        raise


# Core functions
def fetch_html(url):
    retries = 3
    max_content_size = 0.5 * 1024 * 1024  # 0.5 MB

    for attempt in range(retries):
        try:
            print(f"[nunotice.py] Attempt {attempt + 1}/{retries} to fetch {url}")
            response = make_request(
                url,
                headers=HEADERS,
                impersonate="chrome",
                timeout=60,
                verify=False,
                stream=True
            )
            print(f"[nunotice.py] Response status code: {response.status_code}")
            response.raise_for_status()

            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk
                    if len(content) >= max_content_size:
                        print(f"[nunotice.py] Content reached {len(content)} bytes, stopping download.")
                        break
            
            print(f"[nunotice.py] Downloaded {len(content) / 1024:.2f} KB")
            html_content = content.decode('utf-8', errors='ignore')

            print(
                f"[nunotice.py] Successfully fetched content (size: {len(html_content)} chars)"
            )
            return BeautifulSoup(html_content, "html.parser")
        except requests.RequestsError as e:
            print(f"[nunotice.py] Attempt {attempt + 1} failed. Error: {str(e)}")
            time.sleep(5)
        except Exception as e:
            print(f"[nunotice.py] Attempt {attempt + 1} failed. Error: {str(e)}")
            time.sleep(5)

    send_error_message("Failed to fetch HTML after multiple attempts.")
    return None


def extract_notices(soup):
    if not soup:
        print("[nunotice.py] No HTML content to parse")
        return []

    print("[nunotice.py] Extracting notices from HTML")
    notices = []
    news_items = soup.find_all("div", class_="news-item")
    print(f"[nunotice.py] Found {len(news_items)} news item divs")

    for i, div in enumerate(news_items):
        anchor = div.find("a", recursive=False)
        if anchor:
            title = anchor.text.strip()
            link = f"https://{quote('www.nu.ac.bd/' + anchor['href'].strip())}"
            print(
                f"[nunotice.py] Notice {i + 1}: {title[:50]}{'...' if len(title) > 50 else ''}"
            )
            notices.append((title, link))
        else:
            print(f"[nunotice.py] Notice {i + 1}: No anchor tag found")

    print(f"[nunotice.py] Successfully extracted {len(notices)} notices")
    return notices


def process_and_send_notices(notices, prev_links):
    # print 1st 3 links from both notices and prev_links
    print(
        f"[nunotice.py] First 3 notices links: {[link for title, link in notices[:3]]}"
    )
    print(f"[nunotice.py] First 3 prev_links: {list(prev_links)[:3]}")

    new_links = [link for title, link in notices if link not in prev_links]
    print(f"[nunotice.py] Found {len(new_links)} new notices to process")

    # Limit to latest 100 notices to avoid spamming
    new_links = new_links[:100]
    if len(new_links) == 100:
        print("[nunotice.py] Limited to 100 latest notices to avoid spamming")

    if new_links:
        save_new_links(SAVED_URLS_FILE, new_links)
        commit_file(SAVED_URLS_FILE, "nunotice: Added new NU notice URLs")

    for i, (title, link) in enumerate(notices):
        if link in new_links:
            print(f"[nunotice.py] Processing notice {i + 1}/{len(notices)}: {title}")
            reply = f"<a href='{link}'>{title}</a>\n\n"
            keywords = PORIKKHA_KEYWORDS | OTHER_KEYWORDS
            hashtags = [
                f"#{val.replace(' ', '_')}"
                for key, val in keywords.items()
                if any(k in title for k in key)
            ]
            print(
                f"[nunotice.py] Detected keywords: {', '.join(hashtags) if hashtags else 'None'}"
            )
            reply += " ".join(hashtags)
            print(f"[nunotice.py] Reply: {reply}")
            try:
                print(f"[nunotice.py] Attempting to download and send document: {link}")
                filename = download_file(link)
                print(f"[nunotice.py] Sending document to chat {NU_CHAT_ID}")
                sent_message = NU_BOT.sendDocument(
                    NU_CHAT_ID, open(filename, "rb"), caption=reply, parse_mode="html"
                )
                print(
                    f"[nunotice.py] Document sent successfully with message ID: {sent_message['message_id']}"
                )

                if any(k in title for key in PORIKKHA_KEYWORDS for k in key):
                    print(
                        f"[nunotice.py] Notice contains exam-related keyword, pinning message"
                    )
                    NU_BOT.pinChatMessage(NU_CHAT_ID, sent_message["message_id"])
                    print("[nunotice.py] Message pinned successfully")

                print(f"[nunotice.py] Removing temporary file: {filename}")
                os.remove(filename)
                print("[nunotice.py] File removed successfully")
            except Exception as e:
                print(f"[nunotice.py] Error sending document: {str(e)}")
                traceback.print_exc()
                print(f"[nunotice.py] Falling back to text message")
                NU_BOT.sendMessage(NU_CHAT_ID, reply, parse_mode="html")
                print("[nunotice.py] Text message sent successfully")

            print(f"[nunotice.py] Waiting 3 seconds before processing next notice...")
            time.sleep(3)


def main():
    print("[nunotice.py] Starting NU Notice Fetcher...")
    url = "https://www.nu.ac.bd/recent-news-notice.php"
    print(f"[nunotice.py] Fetching notices from: {url}")
    prev_links = load_previous_links(SAVED_URLS_FILE)
    print(f"[nunotice.py] Loaded {len(prev_links)} previously processed links")
    soup = fetch_html(url)
    if soup:
        print("[nunotice.py] Successfully fetched and parsed HTML")
    notices = extract_notices(soup)
    print(f"[nunotice.py] Found {len(notices)} notices in total")
    process_and_send_notices(notices, prev_links)


if __name__ == "__main__":
    main()
