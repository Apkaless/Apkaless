import subprocess
import time
import os
import re
from colorama import Fore, init
from datetime import datetime




def intro():
    red = Fore.RED
    green = Fore.GREEN
    white = Fore.WHITE
    lblue = Fore.LIGHTBLUE_EX

    print(f'''{red}

 ▄▄▄       ██▓███   ██ ▄█▀▄▄▄       ██▓    ▓█████   ██████   ██████ 
▒████▄    ▓██░  ██▒ ██▄█▒▒████▄    ▓██▒    ▓█   ▀ ▒██    ▒ ▒██    ▒ 
▒██  ▀█▄  ▓██░ ██▓▒▓███▄░▒██  ▀█▄  ▒██░    ▒███   ░ ▓██▄   ░ ▓██▄   
░██▄▄▄▄██ ▒██▄█▓▒ ▒▓██ █▄░██▄▄▄▄██ ▒██░    ▒▓█  ▄   ▒   ██▒  ▒   ██▒
 ▓█   ▓██▒▒██▒ ░  ░▒██▒ █▄▓█   ▓██▒░██████▒░▒████▒▒██████▒▒▒██████▒▒
 ▒▒   ▓▒█░▒▓▒░ ░  ░▒ ▒▒ ▓▒▒▒   ▓▒█░░ ▒░▓  ░░░ ▒░ ░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░
  ▒   ▒▒ ░░▒ ░     ░ ░▒ ▒░ ▒   ▒▒ ░░ ░ ▒  ░ ░ ░  ░░ ░▒  ░ ░░ ░▒  ░ ░
  ░   ▒   ░░       ░ ░░ ░  ░   ▒     ░ ░      ░   ░  ░  ░  ░  ░  ░  
      ░  ░         ░  ░        ░  ░    ░  ░   ░  ░      ░        ░  
                                                                    
                            
                    ===================================
                    | {red}[Instagram]: {white}Apkalees           {red}|
                    {red}===================================
          
          
          
 {lblue}[Will Change The Following Values]:
           
          [{white}*{lblue}] Full Speed & Duplex ==> {white}True{lblue}

          [{white}*{lblue}] Disable Power Saving Mode ==> {white}True{lblue}

          [{white}*{lblue}] TCP & UDP Checksum (Ipv4 & Ipv6) Rx & Tx ==> {white}True{lblue}
          
          [{white}*{lblue}] Disable WolShutdownLinkSpeed ==> {white}True{lblue}
      
''')
def cls():

    os.system('cls')

    return True


def find_adapter_registry_key(tr_name):

    res = subprocess.check_output('reg query HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}', shell=True)


    devices = re.findall(r'HKEY_LOCAL_MACHINE\\.+',res.decode().strip())

    for device in devices[1:]:

        res = subprocess.check_output(f'reg query {device}', shell=True).decode().strip()

        if tr_name in res:

            return device




def get_transport_name():
    cls()
    res = subprocess.check_output('getmac', shell=True).decode().strip()
    return re.search(r'{[(\d|\s)].+}', res).group()



def find_high_value(device):

    res = subprocess.check_output(f'reg query {device}\\Ndi\params\*SpeedDuplex\enum', shell=True)

    decoded_res = res.decode().strip()

    key = re.search(r'HKEY_LOCAL_MACHINE\\.+', decoded_res).group()

    clean_res = decoded_res.strip(key)

    final_res = clean_res.strip()

    return re.findall(r'\d+', final_res)


def change_device_properties(device: str, spd: str):

    print(f'{yellow}[!] {white}Type {red}(Y) {white}For Yes And {red}(N) {white}For No\n')
    subprocess.check_call(f'reg add {device} /v *SpeedDuplex /t REG_SZ /d {spd} && reg add {device} /v *TCPChecksumOffloadIPv4 /t REG_SZ /d 3 && reg add {device} /v *TCPChecksumOffloadIPv6 /t REG_SZ /d 3 && reg add {device} /v *UDPChecksumOffloadIPv4 /t REG_SZ /d 3 && reg add {device} /v *UDPChecksumOffloadIPv6 /t REG_SZ /d 3 && reg add {device} /v WolShutdownLinkSpeed /t REG_SZ /d 2', shell=True)
    cls()
    time.sleep(1.5) 
    print(f'\n{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}The {gr}Progress {white}Has Been Done !\n')
    time.sleep(2)


if __name__ == '__main__':

    init(convert=True)

    red = Fore.RED
    yellow = Fore.YELLOW
    white = Fore.WHITE
    mg = Fore.MAGENTA
    gr = Fore.GREEN

    intro()
    input(f'{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}To Proceed Hit {mg}[ENTER] {white}Key ! ')

    device = find_adapter_registry_key(get_transport_name())

    values = find_high_value(device)

    values = list(dict.fromkeys(values))

    new_list = [int(i) for i in values]

    new_list.sort()

    highest_value = new_list[-1]

    change_device_properties(device, highest_value)

    input(f'{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}Hit {red}[Enter] {white}To Exit ')

    time.sleep(1)

    exit(0)

