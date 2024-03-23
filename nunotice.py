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

porikkha_keywords = {
    ("পরীক্ষা",): "Exam",
    ("পরীক্ষার সময়সূচী", "পরীক্ষার সময়সূচি"): "Exam Schedule",
    ("ফরম পূরণ",): "Form Fillup",
    ("ফলাফল",): "Result",
}

other_keywords = {
    ("১ম বর্ষ", "প্রথম বর্ষ"): "1st Year",
    ("২য় বর্ষ", "দ্বিতীয় বর্ষ"): "2nd Year",
    ("৩য় বর্ষ", "তৃতীয় বর্ষ"): "3rd Year",
    ("৪র্থ বর্ষ", "চতুর্থ বর্ষ"): "4th Year",
    ("১ম সেমিস্টার", "প্রথম সেমিস্টার"): "1st Semester",
    ("২য় সেমিস্টার", "দ্বিতীয় সেমিস্টার"): "2nd Semester",
    ("৩য় সেমিস্টার", "তৃতীয় সেমিস্টার"): "3rd Semester",
    ("৪র্থ সেমিস্টার", "চতুর্থ সেমিস্টার"): "4th Semester", 
    ("CSE",): "CSE",
    ("ECE",): "ECE",
    ("BBA",): "BBA",
    ("Professional",): "Professional"
}



# load_dotenv()

# bot = telepot.Bot(os.getenv('PRODIPTO_BOT_TOKEN'))
nu_bot = telepot.Bot(os.getenv('BOT_TOKEN'))
chat_id = str(os.getenv('PRODIPTO_SHATASH_CHAT_ID'))
nu_chat_id = str(os.getenv('NATIONAL_UNIVERSITY_CHAT_ID'))
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SAVED_URLS_FILE_NAME = "newspaper-bot-urls/nu_notices.txt"
absolute_path = os.path.join(__location__, SAVED_URLS_FILE_NAME)
error_message_chat_id = os.getenv('ERROR_MESSAGE_CHAT_ID')

# print(os.getenv('PRODIPTO_BOT_TOKEN'), os.getenv('PRODIPTO_SHATASH_CHAT_ID'))

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
        reply = "<a href='" + notice_link + "'>" + notice_title + "</a>\n\n"

        # if notice_title contains any of the other_keywords, then add the keywords as hashtags
        all_keywords  = porikkha_keywords | other_keywords
        for keywords_list, translation in all_keywords.items():
            for keyword in keywords_list:
                if keyword in notice_title:
                    reply += "#" + translation + " "


        ###
        try:
            filename = download_file(notice_link)
            sent = nu_bot.sendDocument(nu_chat_id, open(filename, 'rb'), caption=reply, parse_mode='html')

            # if notice_title contains any of the porikkha_keywords, then pin the message
            for keywords_list, translation in porikkha_keywords.items():
                if any(keyword in notice_title for keyword in keywords_list):
                    nu_bot.pinChatMessage(nu_chat_id, sent['message_id'])

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
