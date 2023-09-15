import grab_news
import grab_bbc_news
import grab_science_news
import grab_kalerkontho_science_news
import grab_ridmik_science_news
import nunotice
import keep_alive
import time, os
from dotenv import load_dotenv
import telepot
import traceback
import shutil
import gitt

# load_dotenv()

# Needed when hosted on heroku like services
# keep_alive.keep_alive()

bot = telepot.Bot(os.getenv('bot_token'))
chat_id = os.getenv('error_message_chat_id')

bot.sendMessage(chat_id, "News bot is awake! (from render.com)")

if os.path.isdir(os.getenv('NEWSPAPER_URLS_GIT_REPO')) is True:
    shutil.rmtree(os.getenv('NEWSPAPER_URLS_GIT_REPO'))


os.system(f"git clone --depth=1 https://github.com/{os.getenv('NEWSPAPER_URLS_GIT_USERNAME')}/{os.getenv('NEWSPAPER_URLS_GIT_REPO')}/")

while os.path.isdir(os.getenv('NEWSPAPER_URLS_GIT_REPO')) is False:
    print("Cloning isn't completed yet!")
    time.sleep(2)

print("Cloning is completed!")


try:
    nunotice.fetch()
except Exception:
    print(str(traceback.format_exc()))
    bot.sendMessage(chat_id, str(traceback.format_exc()))

try:
    grab_ridmik_science_news.check()
except Exception:
    print(str(traceback.format_exc()))
    bot.sendMessage(chat_id, str(traceback.format_exc()))

try:
    grab_science_news.check()
except Exception:
    print(str(traceback.format_exc()))
    bot.sendMessage(chat_id, str(traceback.format_exc()))

try:
    grab_kalerkontho_science_news.check()
except Exception:
    print(str(traceback.format_exc()))
    bot.sendMessage(chat_id, str(traceback.format_exc()))

try:
    grab_news.check()
except Exception:
    print(str(traceback.format_exc()))
    bot.sendMessage(chat_id, str(traceback.format_exc()))

try:
    grab_bbc_news.check()
except Exception:
    print(str(traceback.format_exc()))
    bot.sendMessage(chat_id, str(traceback.format_exc()))


output = gitt.gitTask()
bot.sendMessage(chat_id, output)
time.sleep(1)

print("Sent news for this time!")
bot.sendMessage(chat_id, "Sent news for this time! (from render.com)")

  
# time.sleep(60*60)