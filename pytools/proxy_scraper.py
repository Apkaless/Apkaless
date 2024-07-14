from bs4 import BeautifulSoup as bs
import requests
import re
import json
from colorama import Fore, init
import os
from threading import Thread
import time


class SCRAPER:
    init(convert=True)
    white = Fore.WHITE
    green = Fore.GREEN

    proxies = []

    timeout = 10

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    def __init__(self) -> None:
        pass

    def proxy_1(self):

        proxies = []

        url = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc'

        try:

            res = requests.get(url, headers=SCRAPER.headers, timeout=SCRAPER.timeout)

            for inp in res.json()['data']:
                ip = inp['ip']
                port = inp['port']

                proxy = ip + ':' + port

                print(f'{SCRAPER.green}[+] Scraped: {SCRAPER.white}{proxy}')

                SCRAPER.proxies.append(proxy)
        except:
            pass

        url = 'https://www.proxyscan.io/api/proxy?last_check=9800&country=fr,us,ru&uptime=50&ping=800&limit=20&type=socks4,socks5,http,https'

        for i in range(1, 10):

            try:

                res = requests.get(url, SCRAPER.headers, timeout=SCRAPER.timeout)

                for jd in res.json():
                    ip = jd['Ip']

                    port = jd['Port']

                    proxy = ip + ':' + port

                    print(f'{SCRAPER.green}[+] Scraped: {SCRAPER.white}{proxy}')

                    SCRAPER.proxies.append(proxy)
            except:
                pass

        return proxies

    def proxy_2(self):

        try:

            proxies = []

            urls = ['https://free-proxy-list.net/', 'https://hidemyna.me/en/proxy-list/']

            for url in urls:

                res = requests.get(url, headers=SCRAPER.headers, timeout=SCRAPER.timeout)

                res = json.dumps(res.text)

                sp = bs(res, 'html.parser')

                table = sp.find('table')

                trs = table.find_all('tr')

                for tds in trs[1:]:
                    ip = tds.find_all('td')[0].getText()

                    port = tds.find_all('td')[1].getText()

                    proxy = ip + ':' + port

                    print(f'{SCRAPER.green}[+] Scraped: {SCRAPER.white}{proxy}')

                    SCRAPER.proxies.append(proxy)

            url = 'https://proxyhub.me/'

            for n in range(1, 100):

                res = requests.get(url, headers=SCRAPER.headers, cookies={'page': str(n), 'anonymity': 'all'},
                                   timeout=SCRAPER.timeout)

                res = json.dumps(res.text)

                sp = bs(res, 'html.parser')

                table = sp.find('table')

                trs = table.find_all('tr')

                for tds in trs[1:]:
                    ip = tds.find_all('td')[0].getText()

                    port = tds.find_all('td')[1].getText()

                    proxy = ip + ':' + port

                    print(f'{SCRAPER.green}[+] Scraped: {SCRAPER.white}{proxy}')

                    SCRAPER.proxies.append(proxy)

            return proxies

        except:
            pass

    def proxyScraper(self):

        try:

            proxies = []

            urls = [
                'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                'https://proxy-daily.com/', 'https://spys.me/proxy.txt', 'https://rootjazz.com/proxies/proxies.txt',
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://www.proxy-list.download/api/v1/get?type=https', 'https://proxyspace.pro/https.txt',
                'https://proxyspace.pro/http.txt',
                'https://proxylist.live/nodes/free_1.php?page=1&showall=1', 'https://openproxylist.xyz/http.txt',
                'https://openproxy.space/list/http', 'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt',
                'https://raw.githubusercontent.com/andigwandi/free-proxy/main/proxy_list.txt',
                'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt',
                'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt',
                'https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt',
                'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt',
                'https://raw.githubusercontent.com/caliphdev/Proxy-List/master/http.txt',
                'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
                'https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt',
                'https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt',
                'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt',
                'https://rootjazz.com/proxies/proxies.txt',
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://raw.githubusercontent.com/ToShukKr/rProxyList/main/proxy-list.txt',
                'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt',
                'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt',
                'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt',
                'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt',
                'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt',
                'https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt',
                'https://raw.githubusercontent.com/HyperBeats/proxy-list/main/socks4.txt',
                'https://raw.githubusercontent.com/iptotal/free-proxy-list/master/socks4.txt',
                'https://raw.githubusercontent.com/NotUnko/autoproxies/main/socks4.txt',
                'https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt',
                'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt']

            for url in urls:

                res = requests.get(url, headers=SCRAPER.headers, timeout=SCRAPER.timeout)

                scraped_proxies = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', res.text)

                SCRAPER.proxies.extend(scraped_proxies)

                for i in proxies:
                    print(f'{SCRAPER.green}[+] Scraped: {SCRAPER.white}{i}')

            return proxies

        except:
            pass

    def proxyScraper_2(self):

        proxies = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }

        urls = ['https://www.freeproxy.world/',
                'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=2',
                'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=3',
                'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=4',
                'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=5']

        for url in urls:

            try:

                res = requests.get(url, headers=headers, timeout=SCRAPER.timeout)

                res = json.dumps(res.text)

                sp = bs(res, 'html.parser')

                table = sp.find('table')

                trs = table.find_all('tr')

                for tds in trs[2:]:

                    try:

                        ip = tds.find_all('td')[0].getText()

                        port = tds.find_all('td')[1].getText()

                        proxy = ip + ':' + port

                        proxy = proxy.split('\\n')

                        full_proxy = proxy[1] + ':' + proxy[3]

                        print(f'{SCRAPER.green}[+] Scraped: {SCRAPER.white}{full_proxy}')

                        SCRAPER.proxies.append(full_proxy)

                    except:
                        pass
            except:
                pass

        return proxies


def intro():
    red = Fore.RED
    green = Fore.GREEN
    yellow = Fore.YELLOW
    white = Fore.WHITE
    cyan = Fore.CYAN
    print(fr'''{cyan}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   

                          ____                           _____                                
                         / __ \_________  _  ____  __   / ___/______________ _____  ___  _____
                        / /_/ / ___/ __ \| |/_/ / / /   \__ \/ ___/ ___/ __ `/ __ \/ _ \/ ___/
                       / ____/ /  / /_/ />  </ /_/ /   ___/ / /__/ /  / /_/ / /_/ /  __/ /    
                      /_/   /_/   \____/_/|_|\__, /   /____/\___/_/   \__,_/ .___/\___/_/     
                                            /____/                        /_/                 
                                                                                                                                                                                                                                                                                
 
                            {red}|    {cyan}[+] {white}Name        {cyan}: {green}Proxy Scraper                  {red}|
                            {red}|                                                     {red}|
                            {red}|    {cyan}[+] {white}Instagram   {cyan}: {green}Apkalees                       {red}| 
                            {red}|                                                     {red}| 
                            {red}|    {cyan}[+] {white}Github      {cyan}: {green}https://github.com/apkaless    {red}| 
                            {red}|                                                     {red}|
                            {red}|    {cyan}[+] {white}Nationality {cyan}: {green}Iraq                           {red}|

                                      
''')


# if __name__ == '__main__':
#
#     white = Fore.WHITE
#     green = Fore.GREEN
#     red = Fore.RED
#
#     intro()
#
#     input(f'\n{green}[+] {white}Press {green}ENTER {white}To Start Scrapping ... ')
#
#     os.system('cls')
#
#     threads = []
#
#     for i in range(1):
#         th1 = Thread(target=SCRAPER.proxy_1)
#
#         th2 = Thread(target=SCRAPER.proxy_2)
#
#         th3 = Thread(target=SCRAPER.proxyScraper)
#
#         th4 = Thread(target=SCRAPER.proxyScraper_2)
#
#         th1.start()
#         threads.append(th1)
#         time.sleep(1)
#         th2.start()
#         threads.append(th2)
#         time.sleep(1)
#         th3.start()
#         threads.append(th3)
#         time.sleep(1)
#         th4.start()
#         threads.append(th4)
#         time.sleep(1)
#
#     for thread in threads:
#         thread.join()
#
#     try:
#
#         proxies = SCRAPER.proxies
#
#         b = len(proxies)
#
#         new: list = [prx for prx in dict.fromkeys(proxies)]
#
#         a = len(new)
#
#     except Exception as e:
#         print(e)
#         pass
#
#     for proxy in new:
#         with open('Scraped_proxies.txt', 'a') as file:
#             file.writelines([proxy, '\n'])
#             file.close()
#
#     print(
#         f'\n{green}[+] Total Proxies: {white}{b}\n{green}[+]{red} {b - a} Duplicated Proxies {green}Has Been Removed.\n{green}[+] Saved Into: {white}Scraped_proxies.txt')
#     input(f'\n{green}[+] {white}Press Enter To Quit ...')
#     exit(0)
