import os
import time
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from colorama import Fore, init
from .enhanced_proxy_scraper import EnhancedProxyScraper, ProxyInfo
from .enhanced_proxy_checker import EnhancedProxyChecker, ProxyTestResult

init(convert=True)

class ProxyManager:
    """Comprehensive proxy management system"""
    
    def __init__(self, max_scraper_threads: int = 50, max_checker_threads: int = 200, timeout: int = 5):
        self.scraper = EnhancedProxyScraper(max_threads=max_scraper_threads, timeout=timeout)
        
        # Configuration
        self.config = {
            'auto_save': True,
            'save_format': 'both',  # 'txt', 'json', 'both'
            'output_directory': 'proxy_results',
            'min_working_proxies': 10,
            'max_proxies_to_check': 2000  # Increased for faster processing
        }
        
        # Initialize checker with optimized settings
        self.checker = EnhancedProxyChecker(
            max_threads=max_checker_threads, 
            timeout=timeout, 
            output_directory=self.config['output_directory']
        )
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ProxyManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def full_proxy_workflow(self, check_proxies: bool = True, save_results: bool = True) -> Dict:
        """Complete proxy workflow: scrape -> check -> save"""
        print(f'{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Fore.RESET}')
        print(f'{Fore.CYAN}║                                  PROXY MANAGER                              ║{Fore.RESET}')
        print(f'{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Fore.RESET}\n')
        
        start_time = time.time()
        results = {
            'scraped_proxies': [],
            'checked_proxies': [],
            'working_proxies': [],
            'statistics': {},
            'execution_time': 0
        }
        
        try:
            # Step 1: Scrape proxies
            print(f'{Fore.YELLOW}[!] Step 1: Scraping proxies from multiple sources...{Fore.RESET}')
            scraped_proxies = self.scraper.scrape_all_sources()
            results['scraped_proxies'] = scraped_proxies
            
            if not scraped_proxies:
                print(f'{Fore.RED}[-] No proxies found. Exiting.{Fore.RESET}')
                return results
            
            # Show scraping statistics
            self.scraper.print_statistics(scraped_proxies)
            
            # Save scraped proxies to the configured output directory
            output_dir = self.config['output_directory']
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            scraped_file = f'{output_dir}/scraped_proxies_{timestamp}.txt'
            self.scraper.save_proxies(scraped_proxies, scraped_file)
            
            # Step 2: Check proxies (optional)
            if check_proxies:
                print(f'\n{Fore.YELLOW}[!] Step 2: Validating proxies...{Fore.RESET}')
                
                # Limit number of proxies to check if too many
                proxies_to_check = scraped_proxies[:self.config['max_proxies_to_check']]
                if len(scraped_proxies) > self.config['max_proxies_to_check']:
                    print(f'{Fore.YELLOW}[!] Limiting check to {self.config["max_proxies_to_check"]} proxies{Fore.RESET}')
                
                # Convert ProxyInfo objects to strings for checking
                proxy_strings = [str(proxy) for proxy in proxies_to_check]
                
                try:
                    # Check proxies
                    checked_results = self.checker.check_proxies_batch(proxy_strings)
                    results['checked_proxies'] = checked_results
                    
                    # Filter working proxies
                    working_results = [r for r in checked_results if r.is_working]
                    results['working_proxies'] = working_results
                    
                    # Show checking statistics
                    self.checker.print_statistics(checked_results)
                    
                    # Step 3: Save results (optional)
                    if save_results and working_results:
                        print(f'\n{Fore.YELLOW}[!] Step 3: Saving results...{Fore.RESET}')
                        self.save_comprehensive_results(scraped_proxies, checked_results, working_results)
                        
                except KeyboardInterrupt:
                    print(f'\n{Fore.YELLOW}[!] Proxy checking was cancelled by user{Fore.RESET}')
                    # Still save what we have so far
                    if results['checked_proxies']:
                        working_results = [r for r in results['checked_proxies'] if r.is_working]
                        results['working_proxies'] = working_results
                        if working_results:
                            print(f'{Fore.GREEN}[+] Saving {len(working_results)} working proxies found so far...{Fore.RESET}')
                            self.save_comprehensive_results(scraped_proxies, results['checked_proxies'], working_results)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            results['execution_time'] = execution_time
            
            print(f'\n{Fore.GREEN}[+] Workflow completed in {execution_time:.2f} seconds{Fore.RESET}')
            
            return results
            
        except KeyboardInterrupt:
            print(f'\n{Fore.YELLOW}[!] Proxy workflow was cancelled by user{Fore.RESET}')
            execution_time = time.time() - start_time
            results['execution_time'] = execution_time
            return results
        except Exception as e:
            self.logger.error(f"Error in proxy workflow: {e}")
            print(f'{Fore.RED}[-] Error in proxy workflow: {e}{Fore.RESET}')
            return results
    
    def save_comprehensive_results(self, scraped_proxies: List[ProxyInfo], 
                                  checked_results: List[ProxyTestResult], 
                                  working_results: List[ProxyTestResult]):
        """Save comprehensive results in multiple formats"""
        try:
            # Create output directory
            output_dir = self.config['output_directory']
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save detailed JSON report using checker's method
            self.checker.save_detailed_json_report(checked_results)
            
            # Save comprehensive JSON report
            report = {
                'timestamp': timestamp,
                'summary': {
                    'total_scraped': len(scraped_proxies),
                    'total_checked': len(checked_results),
                    'total_working': len(working_results),
                    'success_rate': len(working_results) / len(checked_results) * 100 if checked_results else 0
                },
                'scraped_proxies': [proxy.to_dict() for proxy in scraped_proxies],
                'checked_results': [result.to_dict() for result in checked_results],
                'working_proxies': [result.to_dict() for result in working_results]
            }
            
            report_file = f'{output_dir}/comprehensive_report_{timestamp}.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f'{Fore.GREEN}[+] Results saved to {output_dir}/ directory{Fore.RESET}')
            print(f'{Fore.GREEN}[+] Files created:{Fore.RESET}')
            print(f'{Fore.WHITE}   - Comprehensive report: {report_file}{Fore.RESET}')
            print(f'{Fore.WHITE}   - Scraped proxies saved during scraping{Fore.RESET}')
            print(f'{Fore.WHITE}   - Working proxies saved immediately during checking{Fore.RESET}')
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            print(f'{Fore.RED}[-] Error saving results: {e}{Fore.RESET}')
    
    def quick_proxy_check(self, proxy_file: str) -> List[ProxyTestResult]:
        """Quick check of existing proxy file"""
        print(f'{Fore.CYAN}[!] Quick proxy check for: {proxy_file}{Fore.RESET}')
        
        # Load proxies from file
        proxies = self.checker.load_proxies_from_file(proxy_file)
        
        if not proxies:
            print(f'{Fore.RED}[-] No proxies found in {proxy_file}{Fore.RESET}')
            return []
        
        print(f'{Fore.GREEN}[+] Loaded {len(proxies)} proxies from {proxy_file}{Fore.RESET}')
        
        try:
            # Check proxies
            results = self.checker.check_proxies_batch(proxies)
            
            # Show statistics
            self.checker.print_statistics(results)
            
            # Save detailed JSON report
            self.checker.save_detailed_json_report(results)
            
            return results
            
        except KeyboardInterrupt:
            print(f'\n{Fore.YELLOW}[!] Quick proxy check was cancelled by user{Fore.RESET}')
            return []
    
    def proxy_health_monitor(self, proxy_file: str, interval_minutes: int = 30):
        """Monitor proxy health over time"""
        print(f'{Fore.CYAN}[!] Starting proxy health monitor{Fore.RESET}')
        print(f'{Fore.CYAN}[!] Monitoring {proxy_file} every {interval_minutes} minutes{Fore.RESET}')
        print(f'{Fore.YELLOW}[!] Press Ctrl+C to stop monitoring{Fore.RESET}\n')
        
        try:
            while True:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'{Fore.CYAN}[{timestamp}] Running health check...{Fore.RESET}')
                
                results = self.quick_proxy_check(proxy_file)
                working_count = len([r for r in results if r.is_working])
                
                print(f'{Fore.GREEN}[+] Health check complete: {working_count} working proxies{Fore.RESET}')
                
                # Wait for next check
                print(f'{Fore.CYAN}[!] Next check in {interval_minutes} minutes...{Fore.RESET}\n')
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f'\n{Fore.YELLOW}[!] Health monitoring stopped{Fore.RESET}')
    
    def proxy_rotation_generator(self, working_proxies: List[ProxyTestResult], 
                               rotation_type: str = 'round_robin') -> List[str]:
        """Generate proxy rotation list based on different strategies"""
        if not working_proxies:
            return []
        
        if rotation_type == 'round_robin':
            # Simple round-robin
            return [r.proxy for r in working_proxies]
        
        elif rotation_type == 'speed_based':
            # Sort by speed (fastest first)
            sorted_proxies = sorted(working_proxies, key=lambda x: x.response_time or float('inf'))
            return [r.proxy for r in sorted_proxies]
        
        elif rotation_type == 'country_based':
            # Group by country, then by speed
            country_groups = {}
            for proxy in working_proxies:
                country = proxy.country or 'Unknown'
                if country not in country_groups:
                    country_groups[country] = []
                country_groups[country].append(proxy)
            
            rotation_list = []
            for country, proxies in country_groups.items():
                # Sort proxies in each country by speed
                sorted_proxies = sorted(proxies, key=lambda x: x.response_time or float('inf'))
                rotation_list.extend([p.proxy for p in sorted_proxies])
            
            return rotation_list
        
        else:
            # Default to round-robin
            return [r.proxy for r in working_proxies]
    
    def export_proxy_config(self, working_proxies: List[ProxyTestResult], 
                          format_type: str = 'python_requests') -> str:
        """Export proxy configuration for different tools"""
        if not working_proxies:
            return ""
        
        if format_type == 'python_requests':
            config = "import requests\n\n"
            config += "# Working proxies for requests\n"
            config += "proxies_list = [\n"
            
            for proxy in working_proxies:
                config += f"    '{proxy.proxy}',  # {proxy.protocol}"
                if proxy.country:
                    config += f" ({proxy.country})"
                if proxy.response_time:
                    config += f" - {proxy.response_time:.2f}s"
                config += "\n"
            
            config += "]\n\n"
            config += "# Example usage:\n"
            config += "for proxy in proxies_list:\n"
            config += "    try:\n"
            config += "        response = requests.get('https://httpbin.org/ip', \n"
            config += "                                proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'}, \n"
            config += "                                timeout=10)\n"
            config += "        print(f'Working: {proxy}')\n"
            config += "    except:\n"
            config += "        print(f'Failed: {proxy}')\n"
            
            return config
        
        elif format_type == 'curl':
            config = "# Proxy list for curl\n"
            for proxy in working_proxies:
                config += f"curl -x {proxy.proxy} https://httpbin.org/ip\n"
            
            return config
        
        else:
            return "\n".join([proxy.proxy for proxy in working_proxies])
    
    def interactive_menu(self):
        """Interactive menu for proxy management"""
        while True:
            print(f'\n{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
            print(f'{Fore.CYAN}[+] PROXY MANAGER MENU{Fore.RESET}')
            print(f'{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
            
            print(f'{Fore.WHITE}[1] Full workflow (Scrape + Check + Save){Fore.RESET}')
            print(f'{Fore.WHITE}[2] Scrape proxies only{Fore.RESET}')
            print(f'{Fore.WHITE}[3] Check existing proxy file{Fore.RESET}')
            print(f'{Fore.WHITE}[4] Health monitoring{Fore.RESET}')
            print(f'{Fore.WHITE}[5] Export proxy configuration{Fore.RESET}')
            print(f'{Fore.WHITE}[6] Settings{Fore.RESET}')
            print(f'{Fore.WHITE}[0] Exit{Fore.RESET}')
            
            choice = input(f'\n{Fore.GREEN}[+] Select option:{Fore.WHITE} ').strip()
            
            if choice == '1':
                self.full_proxy_workflow()
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '2':
                print(f'{Fore.YELLOW}[!] Scraping proxies...{Fore.RESET}')
                proxies = self.scraper.scrape_all_sources()
                self.scraper.print_statistics(proxies)
                
                # Save to the configured output directory
                output_dir = self.config['output_directory']
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                scraped_file = f'{output_dir}/scraped_proxies_{timestamp}.txt'
                self.scraper.save_proxies(proxies, scraped_file)
                
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '3':
                proxy_file = input(f'{Fore.GREEN}[+] Enter proxy file path:{Fore.WHITE} ').strip()
                if os.path.exists(proxy_file):
                    self.quick_proxy_check(proxy_file)
                else:
                    print(f'{Fore.RED}[-] File not found: {proxy_file}{Fore.RESET}')
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '4':
                proxy_file = input(f'{Fore.GREEN}[+] Enter proxy file path:{Fore.WHITE} ').strip()
                if os.path.exists(proxy_file):
                    interval = input(f'{Fore.GREEN}[+] Check interval (minutes, default 30):{Fore.WHITE} ').strip()
                    interval = int(interval) if interval.isdigit() else 30
                    self.proxy_health_monitor(proxy_file, interval)
                else:
                    print(f'{Fore.RED}[-] File not found: {proxy_file}{Fore.RESET}')
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '5':
                proxy_file = input(f'{Fore.GREEN}[+] Enter proxy file path:{Fore.WHITE} ').strip()
                if os.path.exists(proxy_file):
                    proxies = self.checker.load_proxies_from_file(proxy_file)
                    results = self.checker.check_proxies_batch(proxies, show_progress=False)
                    working_results = [r for r in results if r.is_working]
                    
                    if working_results:
                        format_type = input(f'{Fore.GREEN}[+] Export format (python_requests/curl/text):{Fore.WHITE} ').strip()
                        config = self.export_proxy_config(working_results, format_type)
                        
                        output_file = f'proxy_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(config)
                        
                        print(f'{Fore.GREEN}[+] Configuration exported to: {output_file}{Fore.RESET}')
                    else:
                        print(f'{Fore.RED}[-] No working proxies found{Fore.RESET}')
                else:
                    print(f'{Fore.RED}[-] File not found: {proxy_file}{Fore.RESET}')
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '6':
                self.settings_menu()
            
            elif choice == '0':
                print(f'{Fore.CYAN}[!] Exiting...{Fore.RESET}')
                break
            
            else:
                print(f'{Fore.RED}[-] Invalid option{Fore.RESET}')
    
    def settings_menu(self):
        """Settings configuration menu"""
        while True:
            print(f'\n{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
            print(f'{Fore.CYAN}[+] SETTINGS{Fore.RESET}')
            print(f'{Fore.CYAN}══════════════════════════════════════════════════════════════════════════════{Fore.RESET}')
            
            print(f'{Fore.WHITE}[1] View current settings{Fore.RESET}')
            print(f'{Fore.WHITE}[2] Change output directory{Fore.RESET}')
            print(f'{Fore.WHITE}[3] Change max proxies to check{Fore.RESET}')
            print(f'{Fore.WHITE}[4] Change save format{Fore.RESET}')
            print(f'{Fore.WHITE}[0] Back{Fore.RESET}')
            
            choice = input(f'\n{Fore.GREEN}[+] Select option:{Fore.WHITE} ').strip()
            
            if choice == '1':
                print(f'\n{Fore.GREEN}[+] Current Settings:{Fore.RESET}')
                for key, value in self.config.items():
                    print(f'{Fore.WHITE}   {key}: {value}{Fore.RESET}')
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '2':
                new_dir = input(f'{Fore.GREEN}[+] New output directory:{Fore.WHITE} ').strip()
                if new_dir:
                    self.config['output_directory'] = new_dir
                    print(f'{Fore.GREEN}[+] Output directory updated{Fore.RESET}')
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '3':
                new_max = input(f'{Fore.GREEN}[+] New max proxies to check:{Fore.WHITE} ').strip()
                if new_max.isdigit():
                    self.config['max_proxies_to_check'] = int(new_max)
                    print(f'{Fore.GREEN}[+] Max proxies updated{Fore.RESET}')
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '4':
                print(f'{Fore.GREEN}[+] Available formats: txt, json, both{Fore.RESET}')
                new_format = input(f'{Fore.GREEN}[+] New save format:{Fore.WHITE} ').strip()
                if new_format in ['txt', 'json', 'both']:
                    self.config['save_format'] = new_format
                    print(f'{Fore.GREEN}[+] Save format updated{Fore.RESET}')
                input(f'\n{Fore.BLUE}[!] Press Enter to continue...{Fore.RESET}')
            
            elif choice == '0':
                break
            
            else:
                print(f'{Fore.RED}[-] Invalid option{Fore.RESET}')
