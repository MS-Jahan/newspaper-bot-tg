import requests
import os
from bs4 import BeautifulSoup
# imprt threapool
from multiprocessing.pool import ThreadPool
import traceback

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def check_nu_working():
    URL = f"https://hc-ping.com/{os.getenv('HC_PING_ID')}"
    r = requests.get(URL)
    print("hc-ping", r.status_code)

def get_http_proxy():
    proxies = requests.get("https://raw.githubusercontent.com/fahimscirex/proxybd/refs/heads/master/proxylist/http.txt").text.split("\n")
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
    print(f"Found {len(proxies)} proxies")
    print(proxies)
    return proxies

def get_socks4_proxy():
    proxies = requests.get("https://raw.githubusercontent.com/fahimscirex/proxybd/refs/heads/master/proxylist/socks4.txt").text.split("\n")
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
    print(f"Found {len(proxies)} proxies")
    print(proxies)
    return proxies

def get_socks5_proxy():
    proxies = requests.get("https://raw.githubusercontent.com/fahimscirex/proxybd/refs/heads/master/proxylist/socks5.txt").text.split("\n")
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
    print(f"Found {len(proxies)} proxies")
    print(proxies)
    return proxies

# using threadpool, check if the proxies are working
def check_proxies(proxy_arr):
    def is_proxy_working(proxy):
        try:
            response = requests.get("https://www.nu.ac.bd/recent-news-notice.php", headers=headers, proxies={"http": proxy, "https": proxy}, timeout=5)
            if response.status_code == 200:
                return response.text
        except:
            return None

    with ThreadPool(20) as pool:
        results = pool.map(is_proxy_working, proxy_arr)

    working_html = [result for result in results if result]
    print(f"Found {len(working_html)} working proxies with valid HTML")
    return working_html
    
def get_proxyscrape_proxies():
    proxies = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=bd&proxy_format=protocolipport&format=text").text.split("\n")
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
    print(f"Found {len(proxies)} proxies")
    print(proxies)
    return proxies

def get_nu_html():
    # using the proxies, do a get request
    proxies = get_http_proxy()
    proxies += ["socks4://" + proxy for proxy in get_socks4_proxy()]
    proxies += ["socks5://" + proxy for proxy in get_socks5_proxy()]

    proxies += get_proxyscrape_proxies()

    print(f"Total {len(proxies)} proxies")

    retry = 0

    # proxies = check_proxies(proxies)

    html = []

    while retry <= 3:
        html = check_proxies(proxies)
        print(f"Got {len(html)} htmls")
        if len(html) > 0:
            soup = BeautifulSoup(html[0], 'html.parser')
            return soup
        else:
            retry += 1

if __name__ == "__main__":
    get_nu_html()