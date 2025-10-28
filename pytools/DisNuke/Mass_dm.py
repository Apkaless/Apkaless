
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


def massDM(token, content):
    """Send mass DM to all channels"""

    new_title('DM Sender')
    print(f"{Fore.YELLOW}[!] Starting Mass DM...{Fore.RESET}")
    
    try:
        headers = {'Authorization': token}
        channelIds = requests.get("https://discord.com/api/v9/users/@me/channels", headers=getheaders(token)).json()
        
        for channel in channelIds:
            try:
                response = requests.post(
                    f'https://discord.com/api/v9/channels/{channel["id"]}/messages',
                    headers=headers,
                    json={"content": content}
                )
                
                if response.status_code == 200:
                    print(f"{Fore.GREEN}[+] {Fore.LIGHTCYAN_EX}Channel ID={Fore.WHITE}{channel['id']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.GREEN}SENT{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[-] {Fore.LIGHTCYAN_EX}Channel ID={Fore.WHITE}{channel['id']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.RED}FAILED{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"{Fore.RED}[-] Error sending to channel {channel.get('id', 'unknown')}: {e}{Fore.RESET}")
                
    except Exception as e:
        print(f"{Fore.RED}[-] Mass DM failed: {e}{Fore.RESET}")