import json, requests, time, os, traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telepot
import codecs
from post import postToTelegraph

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

TECHNEWS_URL = "https://www.kalerkantho.com/online/info-tech"
SAVED_URLS_FILE_NAME = "newspaper-bot-urls/kk-science-saved-urls.txt"

print(os.path.join(__location__, SAVED_URLS_FILE_NAME))

def getHtml(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def check():
    global TECHNEWS_URL, SAVED_URLS_FILE_NAME
    # load_dotenv()

    bot = telepot.Bot(os.getenv('bot_token')) # Telegram Bot Token 
    chat_id = os.getenv('science_chat_id')


    print(TECHNEWS_URL, SAVED_URLS_FILE_NAME)

    i = 1
    prev_urls = []
    new_urls = []
    new_titles = []

    print(os.path.join(__location__, SAVED_URLS_FILE_NAME))

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
            os.system("sed -i '$ d' newspaper-bot-urls/kk-science-saved-urls.txt")
            with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'r') as my_file:
                prev_urls = my_file.read().splitlines()

    if len(prev_urls) > 1:
        data = getHtml(TECHNEWS_URL)
        # data = data.find("div", {"class": "print_edition_left"})
        data = data.find_all("a")

        print(len(data))

        for element in data:
            if len(element["href"]) > 24:
                got_url = "https://www.kalerkantho.com" + element["href"]
                if got_url not in prev_urls and "/online/info-tech/" in got_url:
                    new_urls.append(got_url)
                    print(got_url)
                    try:
                        title_text = element.find("h4").text
                        new_titles.append(title_text)
                    except:
                        print("Bogus Link\n")
                        del new_urls[-1]
        
        # print(prev_urls)
        print("\n\n")
        # print(new_urls)

        print(len(new_urls))

        if len(prev_urls) > 300:
            prev_urls = prev_urls[60:]
            with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'w') as f:
                for item in prev_urls:
                    f.write("%s\n" % item)
        
        for i, link in enumerate(new_urls):
            if link not in prev_urls:
                print(link)

                try:
                    webpage = getHtml(link)                    
                    image = webpage.find("meta",  property="og:image").attrs['content']
                    headline = webpage.find("title").text
                    json_data = json.loads(webpage.find("script", {"id": "__NEXT_DATA__"}).text)
                    authorName = json_data["props"]["pageProps"]["details"]["n_author"]
                    article = json_data["props"]["pageProps"]["details"]["n_details"] \
                    .replace("\u0026amp;", "").replace("nbsp;", "").replace("\u0026lt;/p\u0026gt;", "</p>").replace("\u0026lt;p\u0026gt;", "<p>")

                    print(article)

                    iv_link = postToTelegraph(headline, authorName, image, article, link)

                    text = "<a href='" + iv_link["url"] + "'>" + headline + " - কালের কণ্ঠ" + "</a>"
                    bot.sendMessage(chat_id, text, parse_mode='html')
                except:
                    print(traceback.format_exc())
                    print("\n\ncouldn't --> " + link + "\n\n")
                break

        if len(new_urls) > 0:
            with open(os.path.join(__location__, SAVED_URLS_FILE_NAME), 'a+') as f:
                for link in new_urls:
                    f.write("%s\n" % link)

    else:
        print("File wasn't read!")

if __name__ == "__main__":
    check()