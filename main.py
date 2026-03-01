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

load_dotenv()

# Needed when hosted on heroku like services
# keep_alive.keep_alive()

bot = telepot.Bot(os.getenv("BOT_TOKEN"))
chat_id = os.getenv("ERROR_MESSAGE_CHAT_ID")

bot.sendMessage(chat_id, "News bot is awake! (from Github Actions)")

if os.path.isdir(os.getenv("NEWSPAPER_URLS_GIT_REPO")) is True:
    shutil.rmtree(os.getenv("NEWSPAPER_URLS_GIT_REPO"))


os.system(
    f"git clone --depth=1 https://github.com/{os.getenv('NEWSPAPER_URLS_GIT_USERNAME')}/{os.getenv('NEWSPAPER_URLS_GIT_REPO')}/"
)

while os.path.isdir(os.getenv("NEWSPAPER_URLS_GIT_REPO")) is False:
    print("[main.py] Cloning isn't completed yet!")
    time.sleep(2)

print("[main.py] Cloning is completed!")

THREADS = []
THREAD_NAMES = {}  # Dictionary to store thread names


def run_function(func):
    func_name = func.__name__ if hasattr(func, "__name__") else func.__module__
    print(f"[main.py] Starting execution of function: {func_name}")
    try:
        # nunotice.fetch()
        func()
        print(f"[main.py] Successfully completed function: {func_name}")
    except Exception:
        error_msg = str(traceback.format_exc())
        print(f"[main.py] Error in function {func_name}:")
        print(error_msg)
        try:
            bot.sendMessage(chat_id, f"Error in {func_name}:\n{error_msg}")
        except Exception as send_err:
            print(f"[main.py] Failed to send error notification: {send_err}")


def create_thread(func, name):
    """Create a thread and store its name"""
    thread = Thread(target=run_function, args=(func,))
    THREADS.append(thread)
    THREAD_NAMES[thread] = name
    return thread


print("[main.py] Setting up threads for news fetching...")

# Create threads with descriptive names
create_thread(grab_science_news.main, "Science News")
create_thread(grab_kalerkontho_science_news.check_tech_news, "Kalerkontho Tech News")
create_thread(grab_news.check_and_notify, "General News")
create_thread(grab_bbc_news.main, "BBC News")
create_thread(nunotice.main, "Nunotice")

print(f"[main.py] Starting {len(THREADS)} threads...")
for i, thread in enumerate(THREADS, 1):
    name = THREAD_NAMES[thread]
    print(f"[main.py] Starting thread {i}/{len(THREADS)} ({name})")
    thread.start()

print("[main.py] All threads started, waiting for completion...")
for i, thread in enumerate(THREADS, 1):
    name = THREAD_NAMES[thread]
    print(f"[main.py] Waiting for thread {i}/{len(THREADS)} ({name}) to complete")
    thread.join()
    print(f"[main.py] Thread {i}/{len(THREADS)} ({name}) completed")

print("[main.py] All threads have completed execution")

# Note: Each scraper now commits its own URL changes immediately after saving.
# The final gitTask() is kept as a safety net to catch any uncommitted changes.
print("[main.py] Running final git sync (catches any uncommitted changes)...")
output = gitt.gitTask()
if output and "No changes" not in output and "Nothing to commit" not in output:
    print("[main.py] Final git sync result:")
    print(output)
else:
    print("[main.py] No additional changes to commit (scrapers already committed)")

print("[main.py] All tasks completed for this execution cycle!")
print("[main.py] Sending completion notification...")
try:
    bot.sendMessage(chat_id, "Sent news for this time! (from Github Actions)")
    print(f"[main.py] Completion notification sent to chat {chat_id}")
except Exception as e:
    print(f"[main.py] Failed to send completion notification: {e}")
print("[main.py] News bot execution cycle finished successfully")


# time.sleep(60*60)
