import json, requests, time, os, traceback
from bs4 import BeautifulSoup
from post import postToTelegraph
from dotenv import load_dotenv
import telepot
import codecs
import cloudscraper
import json
from pprint import pprint


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# load_dotenv()

def getHtml(url):
    # r = requests.get(url)
    scraper = cloudscraper.create_scraper()
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def check():
    # load_dotenv()

    bot = telepot.Bot(os.getenv('bot_token')) # Telegram Bot Token 
    chat_id = os.getenv('science_chat_id')
    error_message_chat_id = os.getenv('error_message_chat_id')

    HOMEPAGES = ["https://www.prothomalo.com/technology", "https://www.prothomalo.com/education/science-tech"]

    i = 1
    prev_urls = []
    new_urls = []

    try:
        with open(os.path.join(__location__, 'newspaper-bot-urls/pa-science-saved-urls.txt'), 'r') as my_file:
            prev_urls = my_file.read().splitlines()
    except UnicodeDecodeError:
        try:
            print(str(traceback.format_exc()))
            with codecs.open(os.path.join(__location__, 'newspaper-bot-urls/pa-science-saved-urls.txt'), 'r', 'utf8' ) as my_file:
                prev_urls = my_file.read().splitlines()
        except:
            print("removing last line from file...")
            os.system("sed -i '$ d' newspaper-bot-urls/pa-science-saved-urls.txt")
            with open(os.path.join(__location__, 'newspaper-bot-urls/pa-science-saved-urls.txt'), 'r') as my_file:
                prev_urls = my_file.read().splitlines()

    if len(prev_urls) > 1:
        if len(prev_urls) > 300:
            prev_urls = prev_urls[60:]
            with open(os.path.join(__location__, 'newspaper-bot-urls/pa-science-saved-urls.txt'), 'w') as f:
                for item in prev_urls:
                    f.write("%s\n" % item)

        for pages in HOMEPAGES:
            # print(getHtml(pages))
            htmlsoup = getHtml(pages)

            # dump to file
            with open("science_page_sample.html", "w") as f:
                f.write(str(htmlsoup))

            # send file to telegram
            bot.sendDocument(error_message_chat_id, open("science_page_sample.html", "rb"), caption="Science page sample (from render.com)")
            
            data = htmlsoup.find(id="static-page").string

            # print(data)
            data = json.loads(data)
            main = data["qt"]["data"]["collection"]["items"]

            with open("main.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            # exit()

            print(len(main))

            retry = 0

            for index, items1 in enumerate(main):
                if index == 0:
                    continue
                try:
                    if "items" in items1:
                        sub_items = items1["items"]
                    else:
                        sub_items = [items1]
                        
                    for items2 in sub_items:
                        item = items2
                        with open("test.json", "w", encoding="utf-8") as f:
                            json.dump(items2, f, indent=4)

                        sub_main = item.get("story")
                        if sub_main is None:
                            continue
                        
                        headline = sub_main.get("headline")
                        authorName = sub_main.get("author-name", "-")
                        url = sub_main.get("url")

                        if url not in prev_urls:
                            print(url)
                            main = getHtml(url)
                            scripts = main.find_all('script', {"type": "application/ld+json"}) 

                            for sc in scripts:
                                try:
                                    article = json.loads(str(sc.string))
                                    article = article["articleBody"]
                                except:
                                    continue
                            
                            try:
                                article = article.replace("&lt;", "<")
                                article = article.replace("&gt;", ">")
                                
                                image = main.find("meta",  property="og:image").attrs['content']

                                print(str(i) + " - " + headline)
                                print(url)
                                print(image)
                                # print(article)
                                # print("\n")
                                if url in prev_urls:
                                    continue
                                
                                prev_urls.append(url)
                                new_urls.append(url)
                                iv_link = postToTelegraph(headline, authorName, image, article, url)

                                text = "<a href='" + iv_link["url"] + "'>" + headline + " - প্রথম আলো" + "</a>"
                                bot.sendMessage(chat_id, text, parse_mode='html')
                            except:
                                print(traceback.format_exc())
                                print("\n\ncouldn't --> " + url + "\n\n")
                            
                            time.sleep(10)
                except:
                    print(traceback.format_exc())
                    break

        print(len(new_urls))
        if len(new_urls) > 0:
            with open(os.path.join(__location__, 'newspaper-bot-urls/pa-science-saved-urls.txt'), 'a+') as f:
                for item in new_urls:
                    f.write("%s\n" % item)

    else:
        print("File wasn't read!")

if __name__ == "__main__":
    check()
