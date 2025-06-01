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
    print("[helpers.py] Performing healthcheck ping...")
    URL = f"https://hc-ping.com/{os.getenv('HC_PING_ID')}"
    try:
        print(f"[helpers.py] Sending healthcheck ping to: {URL}")
        r = requests.get(URL)
        print(f"[helpers.py] Healthcheck ping response: {r.status_code} ({r.reason})")
        return r.status_code == 200
    except Exception as e:
        print(f"[helpers.py] Error sending healthcheck ping: {str(e)}")
        return False

def get_http_proxy():
    print("[helpers.py] Fetching HTTP proxies...")
    proxy_url = "https://raw.githubusercontent.com/fahimscirex/proxybd/refs/heads/master/proxylist/http.txt"
    try:
        print(f"[helpers.py] Sending request to: {proxy_url}")
        response = requests.get(proxy_url)
        print(f"[helpers.py] Response status code: {response.status_code}")
        response.raise_for_status()
        
        proxies = response.text.split("\n")
        proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
        print(f"[helpers.py] Successfully fetched {len(proxies)} HTTP proxies")
        for i, proxy in enumerate(proxies[:5]):
            print(f"[helpers.py] Sample proxy {i+1}: {proxy}")
        if len(proxies) > 5:
            print(f"[helpers.py] ... and {len(proxies)-5} more")
        return proxies
    except Exception as e:
        print(f"[helpers.py] Error fetching HTTP proxies: {str(e)}")
        return []

def get_socks4_proxy():
    print("[helpers.py] Fetching SOCKS4 proxies...")
    proxy_url = "https://raw.githubusercontent.com/fahimscirex/proxybd/refs/heads/master/proxylist/socks4.txt"
    try:
        print(f"[helpers.py] Sending request to: {proxy_url}")
        response = requests.get(proxy_url)
        print(f"[helpers.py] Response status code: {response.status_code}")
        response.raise_for_status()
        
        proxies = response.text.split("\n")
        proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
        print(f"[helpers.py] Successfully fetched {len(proxies)} SOCKS4 proxies")
        for i, proxy in enumerate(proxies[:5]):
            print(f"[helpers.py] Sample proxy {i+1}: {proxy}")
        if len(proxies) > 5:
            print(f"[helpers.py] ... and {len(proxies)-5} more")
        return proxies
    except Exception as e:
        print(f"[helpers.py] Error fetching SOCKS4 proxies: {str(e)}")
        return []

def get_socks5_proxy():
    print("[helpers.py] Fetching SOCKS5 proxies...")
    proxy_url = "https://raw.githubusercontent.com/fahimscirex/proxybd/refs/heads/master/proxylist/socks5.txt"
    try:
        print(f"[helpers.py] Sending request to: {proxy_url}")
        response = requests.get(proxy_url)
        print(f"[helpers.py] Response status code: {response.status_code}")
        response.raise_for_status()
        
        proxies = response.text.split("\n")
        proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
        print(f"[helpers.py] Successfully fetched {len(proxies)} SOCKS5 proxies")
        for i, proxy in enumerate(proxies[:5]):
            print(f"[helpers.py] Sample proxy {i+1}: {proxy}")
        if len(proxies) > 5:
            print(f"[helpers.py] ... and {len(proxies)-5} more")
        return proxies
    except Exception as e:
        print(f"[helpers.py] Error fetching SOCKS5 proxies: {str(e)}")
        return []

# using threadpool, check if the proxies are working
def check_proxies(proxy_arr):
    def is_proxy_working(proxy):
        try:
            response = requests.head("https://www.nu.ac.bd/recent-news-notice.php", headers=headers, proxies={"http": proxy, "https": proxy}, timeout=5)
            if response.status_code == 200:
                return response.text
        except:
            return None

    with ThreadPool(20) as pool:
        results = pool.map(is_proxy_working, proxy_arr)

    working_proxies = [proxy for proxy, result in zip(proxy_arr, results) if result]
    print(f"[helpers.py] Working proxies: {len(working_proxies)}")
    return working_proxies
    
def get_proxyscrape_proxies():
    proxies = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=bd&proxy_format=protocolipport&format=text").text.split("\n")
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
    print(f"[helpers.py] Found {len(proxies)} proxies")
    print(proxies)
    return proxies

def get_nu_html():
    # using the proxies, do a get request
    proxies = get_http_proxy()
    proxies += ["socks4://" + proxy for proxy in get_socks4_proxy()]
    proxies += ["socks5://" + proxy for proxy in get_socks5_proxy()]
    proxies += get_proxyscrape_proxies()

    print(f"[helpers.py] Total {len(proxies)} proxies")

    retry = 0

    # proxies = check_proxies(proxies)

    html = []

    while retry <= 3:
        html = check_proxies(proxies)
        print(f"[helpers.py] Got {len(html)} htmls")
        if len(html) > 0:
            print(html[0])
            soup = BeautifulSoup(html[0], 'html.parser')
            return soup
        else:
            retry += 1

if __name__ == "__main__":
    print(get_nu_html())