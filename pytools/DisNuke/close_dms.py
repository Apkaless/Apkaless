
import requests
import time
from colorama import Fore, Style

def getheaders(token):
    return {
        'Authorization': token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

def new_title(title):
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.YELLOW}{title.center(50)}")
    print(f"{Fore.CYAN}{'='*50}{Fore.RESET}\n")

def close_all_dms(token):
    """Close all Discord DMs"""
    new_title("DM Closer")
    
    try:
        headers = {"authorization": token, "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        close_dm_request = requests.get("https://discord.com/api/v9/users/@me/channels", headers=getheaders(token)).json()
        
        for channel in close_dm_request:
            try:
                response = requests.delete(
                    f"https://discord.com/api/v9/channels/{channel['id']}",
                    headers=getheaders(token)
                )
                
                if response.status_code == 200:
                    print(f"{Fore.GREEN}[+] {Fore.LIGHTCYAN_EX}Channel ID={Fore.WHITE}{channel['id']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.GREEN}CLOSED{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[-] {Fore.LIGHTCYAN_EX}Channel ID={Fore.WHITE}{channel['id']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.RED}FAILED TO CLOSE{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"{Fore.RED}[-] Error closing channel {channel.get('id', 'unknown')}: {e}{Fore.RESET}")
                
    except Exception as e:
        print(f"{Fore.RED}[-] Close DMs failed: {e}{Fore.RESET}")