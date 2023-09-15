from html_telegraph_poster import TelegraphPoster
from html_telegraph_poster.upload_images import upload_image
from dotenv import load_dotenv
import os
from datetime import datetime
import pytz, traceback, requests

# load_dotenv()



# print(os.getenv('TELEGRAPH_ACCESS_TOKEN'))
def postToTelegraph(postTitle, authorName, imgUrl, postHtml, actual_article_url):
    t = TelegraphPoster(access_token=os.getenv('TELEGRAPH_ACCESS_TOKEN'))
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    response = requests.get(imgUrl)
    if response.status_code == 200:
        with open(os.path.join(__location__, 'file_img.jpg'), 'wb') as f:
            f.write(response.content)

        try:
            imgUrl = upload_image(os.path.join(__location__, 'file_img.jpg'))
        except:
            print(traceback.format_exc())
            # imgUrl = "-"
    else:
        print("error - " + str(response.status_code))

    print("image from telegraph: " + imgUrl)
    
    UTC = pytz.utc
    timeZ_Dhaka = pytz.timezone('Asia/Dhaka')
    bdTime = datetime.now(timeZ_Dhaka)
    

    postUrl = t.post(title=postTitle, author=authorName, text="<img src='" + imgUrl + "'/>" + postHtml + "<br/><br/><a href='" + actual_article_url + "'>Goto Actual News Page</a><p>Scrape Time: " + str(bdTime) + "</p>")
    
    return postUrl

# from html_telegraph_poster.upload_images import upload_image

# # upload file
# # upload_image("file_path.jpg")

# #upload url
# print(upload_image("https://images.prothomalo.com/prothomalo-bangla/2021-02/fc77831d-da89-4e26-8a0e-54edd60f751f/5.jpeg"))

