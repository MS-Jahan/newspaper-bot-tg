import requests
import os

def check_nu_working():
    URL = f"https://hc-ping.com/{os.getenv('HC_PING_ID')}"
    r = requests.get(URL)
    print("hc-ping", r.status_code)



if __name__ == "__main__":
    check_nu_working()