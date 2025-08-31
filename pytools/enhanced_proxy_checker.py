import requests
import socket
import time
import threading
import concurrent.futures
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import urllib3
from colorama import Fore, init
import socks
import urllib.request
from urllib.parse import urlparse

init(convert=True)
# Suppress all urllib3 warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.MaxRetryError)
urllib3.disable_warnings(urllib3.exceptions.ConnectionError)
urllib3.disable_warnings(urllib3.exceptions.TimeoutError)
urllib3.disable_warnings(urllib3.exceptions.ProtocolError)
urllib3.disable_warnings(urllib3.exceptions.ReadTimeoutError)
urllib3.disable_warnings(urllib3.exceptions.ConnectTimeoutError)

# Suppress connection pool warnings
import warnings
warnings.filterwarnings('ignore', message='.*Connection pool is full.*')
warnings.filterwarnings('ignore', message='.*discarding connection.*')
warnings.filterwarnings('ignore', message='.*urllib3.*')
warnings.filterwarnings('ignore', message='.*connectionpool.*')
warnings.filterwarnings('ignore', message='.*pool.*')

@dataclass
class ProxyTestResult:
    """Data class to store proxy test results"""
    proxy: str
    protocol: str
    is_working: bool
    response_time: Optional[float] = None
    country: Optional[str] = None
    anonymity: Optional[str] = None
    error_message: Optional[str] = None
    test_url: str = "https://httpbin.org/ip"
    
    def to_dict(self):
        return asdict(self)

class EnhancedProxyChecker:
    """Enhanced proxy checker with speed testing and detailed validation"""
    
    def __init__(self, max_threads: int = 200, timeout: int = 5, output_directory: str = 'working_proxies'):
        self.max_threads = max_threads
        self.timeout = timeout
        self.output_directory = output_directory
        self.logger = self._setup_logger()
        
        # Create output directory if it doesn't exist
        try:
            import os
            os.makedirs(self.output_directory, exist_ok=True)
        except:
            pass
        
        # Test URLs for different protocols
        self.test_urls = {
            'http': 'http://httpbin.org/ip',
            'https': 'https://httpbin.org/ip',
            'socks4': 'https://httpbin.org/ip',
            'socks5': 'https://httpbin.org/ip'
        }
        
        # Create session for connection pooling with optimized settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Configure connection pooling to reduce warnings
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=1
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Country cache to avoid repeated API calls
        self.country_cache = {}
        
        # Statistics
        self.stats = {
            'total_tested': 0,
            'working': 0,
            'failed': 0,
            'by_protocol': {},
            'by_country': {},
            'fastest_proxies': []
        }
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('EnhancedProxyChecker')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        # Suppress urllib3 logging
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
        logging.getLogger('urllib3.util.retry').setLevel(logging.ERROR)
        logging.getLogger('urllib3.util.connection').setLevel(logging.ERROR)
        
        return logger
    
    def _append_single_working_proxy(self, result: ProxyTestResult):
        """Immediately append a single working proxy to relevant text files"""
        try:
            import os
            import threading
            
            # Use threading to avoid blocking the main checking process
            def save_proxy():
                try:
                    # Append to all working proxies file
                    with open(f'{self.output_directory}/all_working.txt', 'a', encoding='utf-8') as f:
                        f.write(f"{result.proxy}\n")
                    
                    # Append to protocol-specific file
                    protocol_file = f'{self.output_directory}/{result.protocol}_proxies.txt'
                    with open(protocol_file, 'a', encoding='utf-8') as f:
                        f.write(f"{result.proxy}\n")
                    
                    # Append to speed-specific file
                    if result.response_time:
                        if result.response_time < 1:
                            speed_file = f'{self.output_directory}/fast_proxies.txt'
                        elif result.response_time < 3:
                            speed_file = f'{self.output_directory}/medium_proxies.txt'
                        else:
                            speed_file = f'{self.output_directory}/slow_proxies.txt'
                        
                        with open(speed_file, 'a', encoding='utf-8') as f:
                            f.write(f"{result.proxy}\n")
                    
                    # Append to country-specific file if country is known
                    if result.country:
                        country_file = f'{self.output_directory}/{result.country}_proxies.txt'
                        with open(country_file, 'a', encoding='utf-8') as f:
                            f.write(f"{result.proxy}\n")
                    
                                         # Suppress print to avoid spam - working proxies are already shown in main progress
                    
                except Exception as e:
                    self.logger.error(f"Error saving working proxy {result.proxy}: {e}")
            
            # Start saving in a separate thread to avoid blocking
            thread = threading.Thread(target=save_proxy)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error in _append_single_working_proxy: {e}")
    
    def _parse_proxy(self, proxy_str: str) -> Tuple[str, int, str]:
        """Parse proxy string and return (ip, port, protocol)"""
        try:
            parts = proxy_str.strip().split(':')
            if len(parts) >= 2:
                ip = parts[0]
                port = int(parts[1])
                protocol = parts[2] if len(parts) > 2 else 'http'
                return ip, port, protocol
        except (ValueError, IndexError):
            pass
        return None, None, None
    
    def _test_http_proxy(self, proxy: str, timeout: int) -> ProxyTestResult:
        """Test HTTP/HTTPS proxy with optimized session"""
        ip, port, protocol = self._parse_proxy(proxy)
        if not ip or not port:
            return ProxyTestResult(proxy, 'unknown', False, error_message="Invalid proxy format")
        
        test_url = self.test_urls.get(protocol, self.test_urls['http'])
        
        proxies = {
            'http': f'http://{ip}:{port}',
            'https': f'http://{ip}:{port}'
        }
        
        try:
            start_time = time.time()
            # Use session for connection pooling and faster requests
            response = self.session.get(
                test_url,
                proxies=proxies,
                timeout=(timeout//2, timeout),  # (connect_timeout, read_timeout)
                verify=False
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Try to get country info
                country = self._get_proxy_country(ip)
                return ProxyTestResult(
                    proxy=proxy,
                    protocol=protocol,
                    is_working=True,
                    response_time=response_time,
                    country=country
                )
            else:
                return ProxyTestResult(
                    proxy=proxy,
                    protocol=protocol,
                    is_working=False,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            return ProxyTestResult(
                proxy=proxy,
                protocol=protocol,
                is_working=False,
                error_message="Timeout"
            )
        except requests.exceptions.ProxyError:
            return ProxyTestResult(
                proxy=proxy,
                protocol=protocol,
                is_working=False,
                error_message="Proxy error"
            )
        except Exception as e:
            return ProxyTestResult(
                proxy=proxy,
                protocol=protocol,
                is_working=False,
                error_message=str(e)
            )
    
    def _test_socks_proxy(self, proxy: str, timeout: int, socks_type: str) -> ProxyTestResult:
        """Test SOCKS proxy (SOCKS4 or SOCKS5)"""
        ip, port, protocol = self._parse_proxy(proxy)
        if not ip or not port:
            return ProxyTestResult(proxy, 'unknown', False, error_message="Invalid proxy format")
        
        test_url = self.test_urls['https']
        
        try:
            # Configure SOCKS proxy
            if socks_type == 'socks4':
                socks.set_default_proxy(socks.SOCKS4, ip, port)
            else:
                socks.set_default_proxy(socks.SOCKS5, ip, port)
            
            socket.socket = socks.socksocket
            
            start_time = time.time()
            response = self.session.get(
                test_url,
                timeout=(timeout//2, timeout),  # (connect_timeout, read_timeout)
                verify=False
            )
            response_time = time.time() - start_time
            
            # Reset socket
            socket.socket = socket.socket
            
            if response.status_code == 200:
                country = self._get_proxy_country(ip)
                return ProxyTestResult(
                    proxy=proxy,
                    protocol=socks_type,
                    is_working=True,
                    response_time=response_time,
                    country=country
                )
            else:
                return ProxyTestResult(
                    proxy=proxy,
                    protocol=socks_type,
                    is_working=False,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            # Reset socket on error
            socket.socket = socket.socket
            return ProxyTestResult(
                proxy=proxy,
                protocol=socks_type,
                is_working=False,
                error_message=str(e)
            )
    
    def _get_proxy_country(self, ip: str) -> Optional[str]:
        """Get country information for IP address with caching"""
        # Check cache first
        if ip in self.country_cache:
            return self.country_cache[ip]
        
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=3)
            if response.status_code == 200:
                data = response.json()
                country = data.get('country')
                # Cache the result
                self.country_cache[ip] = country
                return country
        except:
            pass
        
        # Cache None result to avoid repeated failed requests
        self.country_cache[ip] = None
        return None
    
    def _test_proxy_all_protocols(self, proxy: str) -> List[ProxyTestResult]:
        """Test proxy with all supported protocols in parallel"""
        import concurrent.futures
        
        def test_http():
            return self._test_http_proxy(proxy, self.timeout)
        
        def test_socks4():
            return self._test_socks_proxy(proxy, self.timeout, 'socks4')
        
        def test_socks5():
            return self._test_socks_proxy(proxy, self.timeout, 'socks5')
        
        # Test all protocols in parallel with shorter timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_protocol = {
                executor.submit(test_http): 'http',
                executor.submit(test_socks4): 'socks4',
                executor.submit(test_socks5): 'socks5'
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_protocol, timeout=self.timeout):
                try:
                    result = future.result(timeout=1)  # Quick timeout for individual tests
                    results.append(result)
                    
                    # Early termination: if we find a working proxy, cancel other tests
                    if result.is_working:
                        for f in future_to_protocol:
                            if f != future:
                                f.cancel()
                        break
                        
                except concurrent.futures.TimeoutError:
                    # Test timed out, continue with others
                    continue
                except Exception as e:
                    # Test failed, continue with others
                    continue
        
        return results
    
    def check_proxy(self, proxy: str) -> ProxyTestResult:
        """Check a single proxy and return the best working result"""
        results = self._test_proxy_all_protocols(proxy)
        
        # Find the best working result (prefer faster ones)
        working_results = [r for r in results if r.is_working]
        
        if working_results:
            # Return the fastest working proxy
            best_result = min(working_results, key=lambda x: x.response_time or float('inf'))
            return best_result
        else:
            # Return the first failed result
            return results[0]
    
    def check_proxies_batch(self, proxies: List[str], show_progress: bool = True) -> List[ProxyTestResult]:
        """Check multiple proxies concurrently with optimized performance and safe cancellation"""
        print(f'{Fore.CYAN}[!] Starting proxy validation...{Fore.RESET}')
        print(f'{Fore.CYAN}[!] Testing {len(proxies)} proxies with {self.max_threads} threads{Fore.RESET}')
        print(f'{Fore.CYAN}[!] Working proxies will be saved immediately to {self.output_directory}/{Fore.RESET}')
        print(f'{Fore.YELLOW}[!] Press Ctrl+C to safely stop the checker{Fore.RESET}')
        
        results = []
        completed = 0
        working_count = 0
        cancelled = False
        
        def check_with_progress(proxy):
            nonlocal completed, working_count
            try:
                result = self.check_proxy(proxy)
                completed += 1
                
                if show_progress and result.is_working:
                    working_count += 1
                    print(f'{Fore.GREEN}[+] Working: {Fore.WHITE}{proxy} ({result.protocol}) - {result.response_time:.2f}s{Fore.RESET}')
                    # Immediately save working proxy
                    self._append_single_working_proxy(result)
                
                # Show progress every 10 proxies
                if completed % 10 == 0:
                    print(f'{Fore.YELLOW}[!] Progress: {completed}/{len(proxies)} tested, {working_count} working{Fore.RESET}')
                
                return result
            except Exception as e:
                # Silently handle errors, just return failed result
                completed += 1
                return ProxyTestResult(
                    proxy=proxy,
                    protocol='unknown',
                    is_working=False,
                    error_message="Check failed"
                )
        
        # Use ThreadPoolExecutor with optimized settings
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_threads,
            thread_name_prefix="ProxyChecker"
        )
        
        try:
            # Submit all tasks at once for better performance
            future_to_proxy = {executor.submit(check_with_progress, proxy): proxy for proxy in proxies}
            
            # Process completed futures with timeout
            for future in concurrent.futures.as_completed(future_to_proxy, timeout=300):  # 5 min max
                try:
                    result = future.result(timeout=30)  # 30s timeout per result
                    results.append(result)
                except concurrent.futures.TimeoutError:
                    proxy = future_to_proxy[future]
                    results.append(ProxyTestResult(
                        proxy=proxy,
                        protocol='unknown',
                        is_working=False,
                        error_message="Timeout"
                    ))
                except Exception as e:
                    proxy = future_to_proxy[future]
                    results.append(ProxyTestResult(
                        proxy=proxy,
                        protocol='unknown',
                        is_working=False,
                        error_message="Check failed"
                    ))
                    
        except KeyboardInterrupt:
            print(f'\n{Fore.YELLOW}[!] Cancellation requested. Stopping proxy checker safely...{Fore.RESET}')
            cancelled = True
            
            # Cancel all pending futures
            for future in future_to_proxy:
                future.cancel()
            
            # Wait for running tasks to complete (with timeout)
            try:
                for future in concurrent.futures.as_completed(future_to_proxy, timeout=10):
                    try:
                        result = future.result(timeout=5)
                        results.append(result)
                    except:
                        pass
            except concurrent.futures.TimeoutError:
                print(f'{Fore.YELLOW}[!] Some tasks were forcefully terminated{Fore.RESET}')
            
            print(f'{Fore.GREEN}[+] Safely cancelled. {completed} proxies tested, {working_count} working{Fore.RESET}')
            
        finally:
            # Always shutdown the executor
            executor.shutdown(wait=False)
        
        if not cancelled:
            print(f'{Fore.GREEN}[+] Completed: {completed} proxies tested, {working_count} working{Fore.RESET}')
        
        return results
    
    def categorize_proxies(self, results: List[ProxyTestResult]) -> Dict:
        """Categorize proxies by protocol, country, and speed"""
        categories = {
            'working': [],
            'failed': [],
            'by_protocol': {'http': [], 'https': [], 'socks4': [], 'socks5': []},
            'by_country': {},
            'by_speed': {
                'fast': [],      # < 1 second
                'medium': [],    # 1-3 seconds
                'slow': []       # > 3 seconds
            }
        }
        
        for result in results:
            if result.is_working:
                categories['working'].append(result)
                
                # Categorize by protocol
                if result.protocol in categories['by_protocol']:
                    categories['by_protocol'][result.protocol].append(result)
                
                # Categorize by country
                if result.country:
                    if result.country not in categories['by_country']:
                        categories['by_country'][result.country] = []
                    categories['by_country'][result.country].append(result)
                
                # Categorize by speed
                if result.response_time:
                    if result.response_time < 1:
                        categories['by_speed']['fast'].append(result)
                    elif result.response_time < 3:
                        categories['by_speed']['medium'].append(result)
                    else:
                        categories['by_speed']['slow'].append(result)
            else:
                categories['failed'].append(result)
        
        return categories
    
    def save_detailed_json_report(self, results: List[ProxyTestResult]):
        """Save detailed JSON report of all checked proxies (working and failed)"""
        import os
        
        try:
            os.makedirs(self.output_directory, exist_ok=True)
        except:
            pass
        
        # Save detailed results as JSON (all proxies - working and failed)
        report_file = f'{self.output_directory}/detailed_results.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump([result.to_dict() for result in results], f, indent=2, ensure_ascii=False)
        
        print(f'{Fore.GREEN}[+] Detailed JSON report saved to {report_file}{Fore.RESET}')
        print(f'{Fore.CYAN}[!] Note: Working proxies were already saved immediately during checking{Fore.RESET}')
    
    def print_statistics(self, results: List[ProxyTestResult]):
        """Print detailed statistics about proxy checking results"""
        categories = self.categorize_proxies(results)
        
        total = len(results)
        working = len(categories['working'])
        failed = len(categories['failed'])
        
        print(f'\n{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
        print(f'{Fore.CYAN}[+] PROXY VALIDATION STATISTICS{Fore.RESET}')
        print(f'{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
        
        print(f'{Fore.GREEN}[+] Total Tested:{Fore.WHITE} {total:,}')
        print(f'{Fore.GREEN}[+] Working:{Fore.WHITE} {working:,} ({working/total*100:.1f}%)')
        print(f'{Fore.GREEN}[+] Failed:{Fore.WHITE} {failed:,} ({failed/total*100:.1f}%)')
        
        print(f'\n{Fore.GREEN}[+] By Protocol:{Fore.RESET}')
        for protocol, proxies in categories['by_protocol'].items():
            if proxies:
                avg_speed = sum(p.response_time or 0 for p in proxies) / len(proxies)
                print(f'{Fore.WHITE}   {protocol.upper()}: {len(proxies):,} (avg: {avg_speed:.2f}s)')
        
        print(f'\n{Fore.GREEN}[+] By Speed:{Fore.RESET}')
        for speed, proxies in categories['by_speed'].items():
            if proxies:
                print(f'{Fore.WHITE}   {speed.capitalize()}: {len(proxies):,}')
        
        if categories['by_country']:
            print(f'\n{Fore.GREEN}[+] Top Countries:{Fore.RESET}')
            sorted_countries = sorted(categories['by_country'].items(), key=lambda x: len(x[1]), reverse=True)[:10]
            for country, proxies in sorted_countries:
                print(f'{Fore.WHITE}   {country}: {len(proxies):,}')
        
        # Show fastest proxies
        if categories['by_speed']['fast']:
            print(f'\n{Fore.GREEN}[+] Fastest Proxies (Top 5):{Fore.RESET}')
            fastest = sorted(categories['by_speed']['fast'], key=lambda x: x.response_time or float('inf'))[:5]
            for i, proxy in enumerate(fastest, 1):
                print(f'{Fore.WHITE}   {i}. {proxy.proxy} ({proxy.protocol}) - {proxy.response_time:.2f}s')
        
        print(f'{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
    
    def load_proxies_from_file(self, filename: str) -> List[str]:
        """Load proxies from a text file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f if line.strip()]
            return proxies
        except Exception as e:
            self.logger.error(f"Error loading proxies from {filename}: {e}")
            return []
    
    def validate_proxy_format(self, proxy: str) -> bool:
        """Validate proxy format"""
        try:
            ip, port, _ = self._parse_proxy(proxy)
            if not ip or not port:
                return False
            
            # Validate IP address
            socket.inet_aton(ip)
            
            # Validate port
            if not (1 <= port <= 65535):
                return False
            
            return True
        except:
            return False
    
    def filter_proxies_by_country(self, results: List[ProxyTestResult], countries: List[str]) -> List[ProxyTestResult]:
        """Filter proxies by country"""
        return [r for r in results if r.is_working and r.country in countries]
    
    def filter_proxies_by_speed(self, results: List[ProxyTestResult], max_speed: float) -> List[ProxyTestResult]:
        """Filter proxies by maximum response time"""
        return [r for r in results if r.is_working and r.response_time and r.response_time <= max_speed]
    
    def get_proxy_rotation_list(self, results: List[ProxyTestResult], max_proxies: int = 100) -> List[str]:
        """Get a list of proxies for rotation, prioritizing speed and reliability"""
        working = [r for r in results if r.is_working]
        
        # Sort by speed
        working.sort(key=lambda x: x.response_time or float('inf'))
        
        # Take the fastest proxies
        return [r.proxy for r in working[:max_proxies]]
