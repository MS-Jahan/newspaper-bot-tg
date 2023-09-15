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
bot = telepot.Bot(os.getenv('BOT_TOKEN'))
chat_id = os.getenv('CHAT_ID')
error_message_chat_id = os.getenv('ERROR_MESSAGE_CHAT_ID')
SAVED_URLS_FILE_NAME = "newspaper-bot-urls/bbc-saved-urls.txt"
current_year = str(time.strftime("%Y"))
prev_urls = []
bogus_links_path = os.path.join(__location__, 'bbc-bangla-bogus-links.txt')


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

    HOMEPAGES = ["https://www.bbc.com/bengali"]

    links_from_index_pages = []         # Urls found from index pages. Can be posts or other index pages.
    index_pages_urls = []               # Urls that cantains no actual post but index.
    post_links = []
    post_titles = []                     # Actual post urls

    for link in HOMEPAGES:
        index_pages_urls.append(link)

    with open(bogus_links_path, "r") as f:
        BOGUS_LINKS = f.read().splitlines()

    debug("Bogus links:")
    for link in BOGUS_LINKS:
        debug(link)
    nl()
    nl()

    index_pages_urls_length = len(index_pages_urls)

    for url in index_pages_urls:
        print("index_pages_url length", str(len(index_pages_urls)))

        htmlsoup = getHtml(url)

        # save to file
        with open(os.path.join(__location__, 'bbc-bangla-index-pages.html'), 'w') as f:
            f.write(str(htmlsoup))
        
        # send file to telegram
        bot.sendDocument(error_message_chat_id, open(os.path.join(__location__, 'bbc-bangla-index-pages.html'), 'rb'), caption="from render.com")

        links_in_homepage = htmlsoup.find_all('a')

        for a_tag in links_in_homepage:
            debug(a_tag['href'])
            if a_tag['href'][-1] == "/":
                a_tag['href'] = a_tag['href'][:-1]
            if "bbc.co" not in a_tag['href']:
                a_tag['href'] = "https://www.bbc.com" + a_tag['href']
            debug("edited: ", a_tag['href'])
            nl()
        
            if a_tag['href'] not in BOGUS_LINKS:
                debug("Not bogus")
                nl()
                if "bbc_bangla_radio" not in a_tag['href'] and "live/" not in a_tag['href']:
                    links_from_index_pages.append(a_tag['href'])
            else:
                debug("Bogus")
        
        links_from_index_pages = list(dict.fromkeys(links_from_index_pages))
        
        print(len(links_from_index_pages))
        i = 1
        for i, link in enumerate(links_from_index_pages):
            try:
                print(str(i) + ". Checking link", link)
                if link not in prev_urls:
                    soup = getHtml(link)
                    temp = soup.find_all(attrs={"data-e2e" : "top-stories-heading"})
                    title_text = soup.find("title").text
                    timeD = soup.find("time").attrs
                    print("\ntimeD", timeD)
                    
                    if len(temp) > 0:
                        if "/bengali" in link and len(soup.find_all("iframe")) == 0 and current_year in timeD["datetime"]:
                            post_links.append(link)
                            post_titles.append(title_text)
                            print("post\n")
                            post_links = list(dict.fromkeys(post_links))
                            post_titles = list(dict.fromkeys(post_titles))
                    else:
                        if "/bengali" in link and len(soup.find_all("iframe")) == 0 and current_year in timeD["datetime"]:
                            index_pages_urls.append(link)
                            print("### index\n")
                            index_pages_urls = list(dict.fromkeys(index_pages_urls))
            except:
                print(str(traceback.format_exc()))
                pass
        try:
            index_pages_urls.remove("https://www.bbc.com/bengali")
        except:
            pass

    print(len(index_pages_urls))
    # for i in index_pages_urls:
    #     print(i)

    # print('\n\n')

    print(len(post_links))
    # for i in post_links:
    #     print(i)

    new_urls = []
    # Send to Telegram
    i = 1
    for index, link in enumerate(post_links):
        try:
            print(str(i) + ". Sending link: ", link)
            text = "<a href='" + "https://t.me/iv?url=" + link + "&rhash=b4f88771c2ae04" + "'>" + post_titles[index] + " - বিবিসি বাংলা" + "</a>"
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