
import requests
import time
from colorama import Fore, Style

def getheaders(token):
    return {
        'Authorization': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

def new_title(title):
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.YELLOW}{title.center(50)}")
    print(f"{Fore.CYAN}{'='*50}{Fore.RESET}\n")

def blockAllFriends(token):
    """Block all Discord friends"""
    new_title('Friend Blocker')
    print(f"{Fore.YELLOW}[!] Blocking all friends...{Fore.RESET}")
    
    try:
        headers = {"Authorization": token, "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        json_data = {"type": 2}  # Type 2 = Block
        block_friends_request = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=getheaders(token)).json()
        for friend in block_friends_request:
            try:
                response = requests.put(
                    f"https://discord.com/api/v9/users/@me/relationships/{friend['id']}",
                    headers=headers,
                    json=json_data,
                )
                
                if response.status_code in (200,204):
                    username = friend.get('user', {}).get('username', 'Unknown')
                    print(f"{Fore.GREEN}[+] {Fore.LIGHTCYAN_EX}Friend={Fore.WHITE}{username}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.GREEN}BLOCKED{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[-] Failed to block friend: {response.status_code}{Fore.RESET}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"{Fore.RED}[-] Error blocking friend: {e}{Fore.RESET}")
                
    except Exception as e:
        print(f"{Fore.RED}[-] Block friends failed: {e}{Fore.RESET}")