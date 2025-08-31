import requests
import json
import re
import time
import threading
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import random
import socket
from urllib.parse import urlparse
import concurrent.futures
from dataclasses import dataclass
from colorama import Fore, init

init(convert=True)

@dataclass
class ProxyInfo:
    """Data class to store proxy information"""
    ip: str
    port: int
    protocol: str  # http, https, socks4, socks5
    country: Optional[str] = None
    anonymity: Optional[str] = None  # transparent, anonymous, elite
    speed: Optional[float] = None  # in seconds
    uptime: Optional[float] = None  # percentage
    last_checked: Optional[str] = None
    is_working: bool = False
    
    def __str__(self):
        return f"{self.ip}:{self.port}"
    
    def to_dict(self):
        return {
            'ip': self.ip,
            'port': self.port,
            'protocol': self.protocol,
            'country': self.country,
            'anonymity': self.anonymity,
            'speed': self.speed,
            'uptime': self.uptime,
            'last_checked': self.last_checked,
            'is_working': self.is_working
        }

class EnhancedProxyScraper:
    """Enhanced proxy scraper with multiple sources and better error handling"""
    
    def __init__(self, max_threads: int = 50, timeout: int = 10):
        self.max_threads = max_threads
        self.timeout = timeout
        self.proxies: List[ProxyInfo] = []
        self.logger = self._setup_logger()
        
        # Enhanced headers with rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Rate limiting
        self.request_delay = 0.5
        self.last_request_time = 0
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('EnhancedProxyScraper')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_headers(self) -> Dict[str, str]:
        """Get random headers for requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling and rate limiting"""
        try:
            self._rate_limit()
            headers = kwargs.get('headers', self._get_headers())
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def _parse_proxy_string(self, proxy_str: str) -> Optional[ProxyInfo]:
        """Parse proxy string and return ProxyInfo object"""
        try:
            # Handle different formats: ip:port, ip:port:protocol, etc.
            parts = proxy_str.strip().split(':')
            if len(parts) >= 2:
                ip = parts[0]
                port = int(parts[1])
                protocol = parts[2] if len(parts) > 2 else 'http'
                
                # Validate IP address
                socket.inet_aton(ip)
                
                return ProxyInfo(
                    ip=ip,
                    port=port,
                    protocol=protocol.lower()
                )
        except (ValueError, socket.error, IndexError):
            pass
        return None
    
    def scrape_geonode(self) -> List[ProxyInfo]:
        """Scrape proxies from GeoNode API"""
        proxies = []
        try:
            url = 'https://proxylist.geonode.com/api/proxy-list'
            params = {
                'limit': 500,
                'page': 1,
                'sort_by': 'lastChecked',
                'sort_type': 'desc',
                'filterUpTime': 90,
                'protocols': 'http,https,socks4,socks5'
            }
            
            response = self._make_request(url, params=params)
            if response:
                data = response.json()
                for proxy_data in data.get('data', []):
                    proxy = ProxyInfo(
                        ip=proxy_data.get('ip'),
                        port=proxy_data.get('port'),
                        protocol=proxy_data.get('protocol', 'http'),
                        country=proxy_data.get('country'),
                        anonymity=proxy_data.get('anonymityLevel'),
                        speed=proxy_data.get('speed'),
                        uptime=proxy_data.get('upTime'),
                        last_checked=proxy_data.get('lastChecked')
                    )
                    if proxy.ip and proxy.port:
                        proxies.append(proxy)
                        print(f'{Fore.GREEN}[+] Scraped: {Fore.WHITE}{proxy}')
            
        except Exception as e:
            self.logger.error(f"Error scraping GeoNode: {e}")
        
        return proxies
    
    def scrape_proxyscrape(self) -> List[ProxyInfo]:
        """Scrape proxies from ProxyScrape API"""
        proxies = []
        try:
            urls = [
                'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all&ssl=all&anonymity=all',
                'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all&ssl=all&anonymity=all'
            ]
            
            for url in urls:
                response = self._make_request(url)
                if response:
                    proxy_lines = response.text.strip().split('\n')
                    for line in proxy_lines:
                        proxy = self._parse_proxy_string(line)
                        if proxy:
                            proxies.append(proxy)
                            print(f'{Fore.GREEN}[+] Scraped: {Fore.WHITE}{proxy}')
        
        except Exception as e:
            self.logger.error(f"Error scraping ProxyScrape: {e}")
        
        return proxies
    
    def scrape_github_repos(self) -> List[ProxyInfo]:
        """Scrape proxies from various GitHub repositories"""
        proxies = []
        github_urls = [
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt',
            'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt',
            'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt',
            'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt',
            'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt',
            'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt',
            'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt'
        ]
        
        for url in github_urls:
            try:
                response = self._make_request(url)
                if response:
                    proxy_lines = response.text.strip().split('\n')
                    for line in proxy_lines:
                        proxy = self._parse_proxy_string(line)
                        if proxy:
                            proxies.append(proxy)
                            print(f'{Fore.GREEN}[+] Scraped: {Fore.WHITE}{proxy}')
                
                # Small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
        
        return proxies
    
    def scrape_proxyscan(self) -> List[ProxyInfo]:
        """Scrape proxies from ProxyScan API"""
        proxies = []
        try:
            url = 'https://www.proxyscan.io/api/proxy'
            params = {
                'last_check': 9800,
                'country': 'all',
                'uptime': 50,
                'ping': 800,
                'limit': 100,
                'type': 'http,https,socks4,socks5'
            }
            
            response = self._make_request(url, params=params)
            if response:
                proxy_data = response.json()
                for proxy_info in proxy_data:
                    proxy = ProxyInfo(
                        ip=proxy_info.get('Ip'),
                        port=proxy_info.get('Port'),
                        protocol=proxy_info.get('Type', 'http'),
                        country=proxy_info.get('Country'),
                        anonymity=proxy_info.get('Anonymity'),
                        speed=proxy_info.get('Speed'),
                        uptime=proxy_info.get('Uptime'),
                        last_checked=proxy_info.get('LastChecked')
                    )
                    if proxy.ip and proxy.port:
                        proxies.append(proxy)
                        print(f'{Fore.GREEN}[+] Scraped: {Fore.WHITE}{proxy}')
        
        except Exception as e:
            self.logger.error(f"Error scraping ProxyScan: {e}")
        
        return proxies
    
    def scrape_freeproxyworld(self) -> List[ProxyInfo]:
        """Scrape proxies from FreeProxyWorld"""
        proxies = []
        try:
            base_url = 'https://www.freeproxy.world'
            pages = range(1, 6)  # Scrape first 5 pages
            
            for page in pages:
                url = f"{base_url}/?page={page}"
                response = self._make_request(url)
                
                if response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table')
                    
                    if table:
                        rows = table.find_all('tr')[1:]  # Skip header
                        for row in rows:
                            try:
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    ip = cells[0].get_text(strip=True)
                                    port = cells[1].get_text(strip=True)
                                    protocol = cells[2].get_text(strip=True) if len(cells) > 2 else 'http'
                                    country = cells[3].get_text(strip=True) if len(cells) > 3 else None
                                    
                                    proxy = ProxyInfo(
                                        ip=ip,
                                        port=int(port),
                                        protocol=protocol.lower(),
                                        country=country
                                    )
                                    
                                    if proxy.ip and proxy.port:
                                        proxies.append(proxy)
                                        print(f'{Fore.GREEN}[+] Scraped: {Fore.WHITE}{proxy}')
                            except (ValueError, IndexError):
                                continue
                
                time.sleep(0.5)  # Delay between pages
        
        except Exception as e:
            self.logger.error(f"Error scraping FreeProxyWorld: {e}")
        
        return proxies
    
    def scrape_all_sources(self) -> List[ProxyInfo]:
        """Scrape proxies from all available sources"""
        print(f'{Fore.CYAN}[!] Starting proxy scraping...{Fore.RESET}')
        
        all_proxies = []
        
        # Define scraping functions
        scraper_functions = [
            ('GeoNode', self.scrape_geonode),
            ('ProxyScrape', self.scrape_proxyscrape),
            ('GitHub Repos', self.scrape_github_repos),
            ('ProxyScan', self.scrape_proxyscan),
            ('FreeProxyWorld', self.scrape_freeproxyworld)
        ]
        
        # Use ThreadPoolExecutor for concurrent scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_source = {
                executor.submit(func): source_name 
                for source_name, func in scraper_functions
            }
            
            for future in concurrent.futures.as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    proxies = future.result()
                    all_proxies.extend(proxies)
                    print(f'{Fore.GREEN}[+] {source_name}: Found {len(proxies)} proxies{Fore.RESET}')
                except Exception as e:
                    self.logger.error(f"Error in {source_name}: {e}")
        
        # Remove duplicates
        unique_proxies = self._remove_duplicates(all_proxies)
        
        print(f'{Fore.CYAN}[!] Total unique proxies found: {len(unique_proxies)}{Fore.RESET}')
        
        return unique_proxies
    
    def _remove_duplicates(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Remove duplicate proxies based on IP:port combination"""
        seen = set()
        unique_proxies = []
        
        for proxy in proxies:
            proxy_key = f"{proxy.ip}:{proxy.port}"
            if proxy_key not in seen:
                seen.add(proxy_key)
                unique_proxies.append(proxy)
        
        return unique_proxies
    
    def save_proxies(self, proxies: List[ProxyInfo], filename: str = 'scraped_proxies.txt'):
        """Save proxies to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            
            print(f'{Fore.GREEN}[+] Saved {len(proxies)} proxies to {filename}{Fore.RESET}')
            
        except Exception as e:
            self.logger.error(f"Error saving proxies: {e}")
    
    def save_proxies_json(self, proxies: List[ProxyInfo], filename: str = 'scraped_proxies.json'):
        """Save proxies to JSON file with detailed information"""
        try:
            proxy_data = [proxy.to_dict() for proxy in proxies]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(proxy_data, f, indent=2, ensure_ascii=False)
            
            print(f'{Fore.GREEN}[+] Saved {len(proxies)} proxies to {filename}{Fore.RESET}')
            
        except Exception as e:
            self.logger.error(f"Error saving proxies to JSON: {e}")
    
    def get_proxy_statistics(self, proxies: List[ProxyInfo]) -> Dict:
        """Get statistics about the scraped proxies"""
        stats = {
            'total': len(proxies),
            'by_protocol': {},
            'by_country': {},
            'by_anonymity': {}
        }
        
        for proxy in proxies:
            # Protocol statistics
            protocol = proxy.protocol
            stats['by_protocol'][protocol] = stats['by_protocol'].get(protocol, 0) + 1
            
            # Country statistics
            if proxy.country:
                stats['by_country'][proxy.country] = stats['by_country'].get(proxy.country, 0) + 1
            
            # Anonymity statistics
            if proxy.anonymity:
                stats['by_anonymity'][proxy.anonymity] = stats['by_anonymity'].get(proxy.anonymity, 0) + 1
        
        return stats
    
    def print_statistics(self, proxies: List[ProxyInfo]):
        """Print proxy statistics"""
        stats = self.get_proxy_statistics(proxies)
        
        print(f'\n{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
        print(f'{Fore.CYAN}[+] PROXY STATISTICS{Fore.RESET}')
        print(f'{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
        
        print(f'{Fore.GREEN}[+] Total Proxies:{Fore.WHITE} {stats["total"]:,}')
        
        print(f'\n{Fore.GREEN}[+] By Protocol:{Fore.RESET}')
        for protocol, count in stats['by_protocol'].items():
            print(f'{Fore.WHITE}   {protocol.upper()}: {count:,}')
        
        if stats['by_country']:
            print(f'\n{Fore.GREEN}[+] Top Countries:{Fore.RESET}')
            sorted_countries = sorted(stats['by_country'].items(), key=lambda x: x[1], reverse=True)[:10]
            for country, count in sorted_countries:
                print(f'{Fore.WHITE}   {country}: {count:,}')
        
        if stats['by_anonymity']:
            print(f'\n{Fore.GREEN}[+] By Anonymity:{Fore.RESET}')
            for anonymity, count in stats['by_anonymity'].items():
                print(f'{Fore.WHITE}   {anonymity}: {count:,}')
        
        print(f'{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
