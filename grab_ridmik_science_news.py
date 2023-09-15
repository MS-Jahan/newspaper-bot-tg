import json, os, time, requests, traceback
from bs4 import BeautifulSoup
from post import postToTelegraph
from dotenv import load_dotenv
import telepot
import codecs
import cloudscraper
from dotenv import load_dotenv

# load_dotenv()

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
bot = telepot.Bot(os.getenv('bot_token'))
chat_id = os.getenv('science_chat_id')
error_message_chat_id = os.getenv('error_message_chat_id')
SAVED_URLS_FILE_NAME = "newspaper-bot-urls/ridmik-science-saved-urls.txt"
current_year = str(time.strftime("%Y"))
prev_urls = []

def getHtml(url):
    # r = requests.get(url)
    scraper = cloudscraper.create_scraper()
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def check():
    if os.path.exists(os.path.join(__location__, SAVED_URLS_FILE_NAME)) == False:
        with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'w') as f:
            f.write("")
            
    try:
        with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'r') as my_file:
            prev_urls = my_file.read().splitlines()
    except UnicodeDecodeError:
        try:
            print(str(traceback.format_exc()))
            with codecs.open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'r', 'utf8' ) as my_file:
                prev_urls = my_file.read().splitlines()
        except:
            print("removing last line from file...")
            os.system("sed -i '$ d' " + SAVED_URLS_FILE_NAME)
            with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'r') as my_file:
                prev_urls = my_file.read().splitlines()

    if len(prev_urls) > 300:
        prev_urls = prev_urls[60:]
        with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'w') as f:
            for item in prev_urls:
                f.write("%s\n" % item)

    def nl():
        showNl = False
        if showNl == True:
            print('\n')

    def debug(tag=None, msg=None):
        showMsg = False
        if showMsg == True:
            if tag is not None:
                print(tag)
            if msg is not None:
                print(msg)

    def getHtml(url):
        # r = requests.get(url)
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    HOMEPAGES = ["https://ridmik.news/topic/12/technology"]

    post_links = []
    post_titles = []                     # Actual post urls


    webpage = getHtml(HOMEPAGES[0])
    json_data = json.loads(webpage.find("script", {"id": "__NEXT_DATA__"}).text)
    try:
        for article in json_data["props"]["pageProps"]["articles"]:
            post_links.append("https://ridmik.news/article/" + article["aid"] + "/" + article["title"].replace(" ", "-"))
            post_titles.append(article["title"])
    except:
        print(traceback.format_exc())
    

    try:
        home_articles = json_data["props"]["pageProps"]["homeArticles"]
        for key, value in home_articles.items():
            post_links.append("https://ridmik.news/article/" + value["aid"] + "/" + value["title"].replace(" ", "-"))
            post_titles.append(value["title"])
    except:
        print(traceback.format_exc())
    

    print(len(post_links))
    # for i in post_links:
    #     print(i)

    new_urls = []
    # Send to Telegram
    i = 1
    for index, link in enumerate(post_links):
        if link not in prev_urls:
            try:
                print(str(i) + ". Sending link: ", link)
                text = "<a href='" + "https://t.me/iv?url=" + link + "&rhash=e70d349033f6bb" + "'>" + post_titles[index] + " - Ridmik News" + "</a>"
                bot.sendMessage(chat_id, text, parse_mode='html')
                new_urls.append(link)
                time.sleep(5)
                i += 1
            except:
                print(traceback.format_exc())

    # Add post urls to file
    with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'a+') as f:
        for link in new_urls:
            f.write("%s\n" % link)

if __name__ == "__main__":
    check()