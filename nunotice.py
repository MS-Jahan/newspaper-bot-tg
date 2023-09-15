import requests, os
from bs4 import BeautifulSoup
from urllib.parse import quote
from dotenv import load_dotenv
import telepot
import time
import traceback

from helpers import *

headers = {
    'Host': 'www.nu.ac.bd',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'
}

# load_dotenv()

# bot = telepot.Bot(os.getenv('prodipto_bot_token'))
nu_bot = telepot.Bot(os.getenv('bot_token'))
chat_id = str(os.getenv('prodipto_shatash_chat_id'))
nu_chat_id = str(os.getenv('national_university_chat_id'))
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SAVED_URLS_FILE_NAME = "newspaper-bot-urls/nu_notices.txt"
absolute_path = os.path.join(__location__, SAVED_URLS_FILE_NAME)
error_message_chat_id = os.getenv('error_message_chat_id')

# print(os.getenv('prodipto_bot_token'), os.getenv('prodipto_shatash_chat_id'))

def getHtml(url):
    retry = 0

    while retry <= 3:
        try:
            global headers
            r = requests.get(url, headers=headers, verify=False, timeout=50)
            nu_bot.sendMessage(error_message_chat_id, "Scraped NU website. Got status " + str(r.status_code) + "!")
            with open("nu.html", "w") as f:
                f.write(r.text)
            nu_bot.sendDocument(error_message_chat_id, open("nu.html", 'rb'))
            soup = BeautifulSoup(r.text, 'html.parser')
            check_nu_working()
            return soup
        except:
            retry += 1
            print("Failed to get Webstie html")
            print(traceback.format_exc())
            time.sleep(5)

    nu_bot.sendMessage(error_message_chat_id, "Couldn't scrape NU website.")


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

def fetch():
    global bot, chat_id
    print("Fetching html page...")
    html_data = getHtml("https://www.nu.ac.bd/recent-news-notice.php")
    # print(html_data)
    all_divs = html_data.find_all("div", {"class": "news-item"})
    print(len(all_divs))

    prev_links = []
    new_links = {}

    with open(absolute_path, "r") as f:
        prev_links = f.read().splitlines()
    
    i = 1
    for div in all_divs:
        anchor_tag = div.findChildren("a" , recursive=False)
        # print(anchor_tag)
        # print(type(anchor_tag))
        notice_title = anchor_tag[0].text
        notice_link = "https://" + quote("www.nu.ac.bd/" + anchor_tag[0]['href'])
        if notice_link not in prev_links:
            new_links[str(i)] = [str(notice_title), notice_link]
        
        # print(notice_link, notice_title)
        i += 1
    


    with open(absolute_path, 'a+') as f:
        for link in new_links:
            f.write("%s\n" % new_links[link][1])


    for key in new_links:
        notice_title = new_links[key][0]
        notice_link = new_links[key][1]
        reply = "Notice from NU Website: " + "<a href='" + notice_link + "'>" + notice_title + "</a>"
        print(reply)
        # bot.sendMessage(chat_id, reply, parse_mode='html')
        reply = "<a href='" + notice_link + "'>" + notice_title + "</a>"
        ###
        try:
            filename = download_file(notice_link)
            nu_bot.sendDocument(nu_chat_id, open(filename, 'rb'), caption=reply, parse_mode='html')
            try:
                os.remove(filename)
            except:
                print("Could not remove file")
        except:
            traceback.print_exc()
            nu_bot.sendMessage(nu_chat_id, reply, parse_mode='html')
        
        time.sleep(3)

if __name__ == "__main__":
    getHtml("https://www.nu.ac.bd/recent-news-notice.php")

# fetch()
