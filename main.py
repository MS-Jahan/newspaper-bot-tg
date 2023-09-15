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
from threading import Thread

# load_dotenv()

# Needed when hosted on heroku like services
# keep_alive.keep_alive()

bot = telepot.Bot(os.getenv('BOT_TOKEN'))
chat_id = os.getenv('ERROR_MESSAGE_CHAT_ID')

bot.sendMessage(chat_id, "News bot is awake! (from Github Actions)")

if os.path.isdir(os.getenv('NEWSPAPER_URLS_GIT_REPO')) is True:
    shutil.rmtree(os.getenv('NEWSPAPER_URLS_GIT_REPO'))


os.system(f"git clone --depth=1 https://github.com/{os.getenv('NEWSPAPER_URLS_GIT_USERNAME')}/{os.getenv('NEWSPAPER_URLS_GIT_REPO')}/")

while os.path.isdir(os.getenv('NEWSPAPER_URLS_GIT_REPO')) is False:
    print("Cloning isn't completed yet!")
    time.sleep(2)

print("Cloning is completed!")

THREADS = []

def run_function(func):
    try:
        # nunotice.fetch()
        func()
    except Exception:
        print(str(traceback.format_exc()))
        bot.sendMessage(chat_id, str(traceback.format_exc()))


THREADS.append(Thread(target=run_function, args=(nunotice.fetch,)))
THREADS.append(Thread(target=run_function, args=(grab_ridmik_science_news.check,)))
THREADS.append(Thread(target=run_function, args=(grab_science_news.check,)))
THREADS.append(Thread(target=run_function, args=(grab_kalerkontho_science_news.check,)))
THREADS.append(Thread(target=run_function, args=(grab_news.check,)))
THREADS.append(Thread(target=run_function, args=(grab_bbc_news.check,)))


# THREADS.append(Thread(target=grab_ridmik_science_news.check))
# THREADS.append(Thread(target=grab_science_news.check))
# THREADS.append(Thread(target=grab_kalerkontho_science_news.check))
# THREADS.append(Thread(target=grab_news.check))
# THREADS.append(Thread(target=grab_bbc_news.check))

for thread in THREADS:
    thread.start()

for thread in THREADS:
    thread.join()


output = gitt.gitTask()
bot.sendMessage(chat_id, output)
time.sleep(1)

print("Sent news for this time!")
bot.sendMessage(chat_id, "Sent news for this time! (from Github Actions)")

  
# time.sleep(60*60)
