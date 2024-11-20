import requests
import os
from bs4 import BeautifulSoup
# imprt threapool
from multiprocessing.pool import ThreadPool
import traceback

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
            response = requests.get("https://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
            return response.status_code == 200
        except:
            return False

    with ThreadPool(10) as pool:
        results = pool.map(is_proxy_working, proxy_arr)

    working_proxies = [proxy for proxy, is_working in zip(proxy_arr, results) if is_working]
    print(f"Found {len(working_proxies)} working proxies")
    return working_proxies
    


def get_nu_html():
    # using the proxies, do a get request
    proxies = get_http_proxy()
    proxies += ["socks4://" + proxy for proxy in get_socks4_proxy()]
    proxies += ["socks5://" + proxy for proxy in get_socks5_proxy()]
    print(f"Total {len(proxies)} proxies")

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    retry = 0

    # proxies = check_proxies(proxies)

    while retry <= 3:
        for i, proxy in enumerate(proxies):
            try:
                response = requests.get("https://www.nu.ac.bd/recent-news-notice.php", headers=headers, proxies={"http": proxy, "https": proxy}, timeout=5)
                print(response.status_code)
                # save response to file
                with open(f"response_{i}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                soup = BeautifulSoup(response.text, 'html.parser')
                check_nu_working()
                retry = 4
                return soup
            except Exception as e:
                print(traceback.format_exc())
                print(f"Failed to connect using {proxy}. Error: {e}")
                continue
        retry += 1

if __name__ == "__main__":
    get_nu_html()