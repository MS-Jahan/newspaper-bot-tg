import json, os, time, requests, traceback
from bs4 import BeautifulSoup
from post import postToTelegraph
from dotenv import load_dotenv
import telepot
import codecs
import cloudscraper


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# print(os.path.isfile(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt')))

def check():    
    # load_dotenv()
    HOMEPAGE = "https://www.prothomalo.com/"


    bot = telepot.Bot(os.getenv('BOT_TOKEN'))
    chat_id = os.getenv('CHAT_ID')

    def getHtml(url):
        # r = requests.get(url)
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    # print(soup.title.text)

    data = getHtml(HOMEPAGE).find(id="static-page").string

    # print(data)

    # with open("homepage_sample.json", "r") as f:
    #     data = f.read()

    data = json.loads(data)
    main = data["qt"]["data"]["collection"]["items"]


    data_arr = []


    for ii in main:
        first_items = ii["items"]
        for jj in first_items:
            try:
                temp = {}
                
                temp["slug"] = jj["story"]["url"]
                temp["author-name"] = jj["story"]["author-name"]
                temp["headline"] = jj["story"]["headline"]
                try:
                    v = jj["story"]["alternative"]["home"]["default"]["hero-image"]["hero-image-s3-key"]
                except:
                    v = "-"
                temp["image"] = v

                data_arr.append(temp)
            except:
                pass


    prev_slugs = []

    print(os.path.isdir(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt')))

    try:
        with open(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt'), 'r') as my_file:
            prev_slugs = my_file.read().splitlines()
    except UnicodeDecodeError:
        try:
            print(str(traceback.format_exc()))
            with codecs.open(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt'), 'r', 'utf8' ) as my_file:
                prev_slugs = my_file.read().splitlines()
        except:
            print("removing last line from file...")
            os.system("sed -i '$ d' newspaper-bot-urls/saved-urls.txt")
            with open(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt'), 'r') as my_file:
                prev_slugs = my_file.read().splitlines()
    
    if len(prev_slugs) > 1:

        if len(prev_slugs) > 1000:
            prev_slugs = prev_slugs[100:]
            with open(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt'), 'w') as f:
                for item in prev_slugs:
                    f.write("%s\n" % item)

        # print(prev_slugs)

        # prev_slugs = list(dict.fromkeys(prev_slugs))

        new_data_arr = []

        for item in data_arr:
            if item not in new_data_arr:
                new_data_arr.append(item)



        # for i in range(len(new_data_arr)):
        #     # print(new_data_arr[i]["slug"])
        #     try:
        #         if new_data_arr[i]["slug"] in prev_slugs:
        #             new_data_arr.pop(i)
        #             print("\ndeleted --> " + str(new_data_arr[i]))
        #     except IndexError:
        #         break

        i = -1
        arr_length = len(new_data_arr)

        while i < arr_length-1:
            i += 1
            try:
                if new_data_arr[i]["slug"] in prev_slugs:
                    new_data_arr.pop(i)
                    # print("\ndeleted --> " + str(new_data_arr[i]))
                    i -= 1
                    arr_length = len(new_data_arr)
            except IndexError:
                # print("breaked --> index error")
                break

        with open(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt'), 'a+') as f:
            for item in new_data_arr:
                f.write("%s\n" % item["slug"])

        print(len(new_data_arr))

        print("\n\n")

        
        # for i in prev_slugs:
        #     print(i)
        #     # print("\n")
        # print('\n')
        # for i in new_data_arr:
        #     print(i['slug'])


        # if(len(new_data_arr) > 0):
        #     fileD = m.find('saved-urls.txt')
        #     m.delete(fileD[0])
        #     print("Deleted")
        #     fileD = m.upload(os.path.join(__location__, 'newspaper-bot-urls/saved-urls.txt'))
        #     print("Uploaded")

        i = 0

        for item in new_data_arr:
            print(item["slug"])
            i += 1
            if "photo/" in item["slug"]:
                pass
            elif "entertainment/" in item["slug"]:
                pass
            elif "video/" in item["slug"]:
                pass
            else:
                try:
                    main = getHtml(item["slug"])
                    scripts = main.find_all('script')

                    try:
                        article = json.loads(scripts[2].string)
                    except:
                        article = json.loads(str(scripts[2].string))

                    article = article["articleBody"]
                    article = article.replace("&lt;", "<")
                    article = article.replace("&gt;", ">")
                    if item["image"] == '-':
                        item["image"] = main.find("meta",  property="og:image").attrs['content']
                    
                    if 'https://images.prothomalo.com/' not in item["image"]:
                        item["image"] = "https://images.prothomalo.com/" + item["image"]

                    print(item["headline"])
                    print(item["author-name"])
                    print(item["image"])
                    # print(article)
                    print(HOMEPAGE + item["slug"])
                    iv_link = postToTelegraph(item["headline"], item["author-name"], item["image"], article, item["slug"])
                    # iv_link = json.loads(iv_link)
                    print(iv_link)
                    print('\n')

                    text = "<a href='" + iv_link["url"] + "'>" + item["headline"] + " - প্রথম আলো" + "</a>"
                    bot.sendMessage(chat_id, text, parse_mode='html')
                except:
                    print(traceback.format_exc())

                time.sleep(15)
    else:
        print("File wasn't read!")

# check() # ---