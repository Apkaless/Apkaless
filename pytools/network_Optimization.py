import subprocess
import time
import os
import re
from colorama import Fore, init
from datetime import datetime
import psutil



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
                    | {red}[Instagram]: {white}Apkaless           {red}|
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


def network_optimization():
    mac_addresses = []
    ips = []

    def cls():

        os.system('cls')

        return True

    def find_mac_address_of_current_adapter():

        for iface, address in psutil.net_if_addrs().items():
            for addr in address:
                if addr.family.AF_LINK == psutil.AF_LINK:
                    mac_address = addr.address
                    mac_addresses.append(mac_address)
                elif addr.family == 2:
                    ips.append(addr.address)

        return mac_addresses[0], ips[0]

    def find_adapter_registry_key(tr_name):

        res = subprocess.check_output(
            r'reg query HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}',
            shell=True)

        devices = re.findall(r'HKEY_LOCAL_MACHINE\\.+', res.decode().strip())

        for device in devices[1:]:

            res = subprocess.check_output(f'reg query {device}', shell=True).decode().strip()

            if tr_name in res:
                return device

    def get_transport_name(mac_address):
        cls()
        res = subprocess.check_output('getmac', shell=True).decode().strip()
        res = res.strip().split('\n')
        for i in res:
            if mac_address in i:
                return i

    def find_high_value(device):

        res = subprocess.check_output(fr'reg query {device}\Ndi\params\*SpeedDuplex\enum', shell=True)

        decoded_res = res.decode().strip()

        key = re.search(r'HKEY_LOCAL_MACHINE\\.+', decoded_res).group()

        clean_res = decoded_res.strip(key)

        final_res = clean_res.strip()

        return re.findall(r'\d+', final_res)

    def change_device_properties(device: str, spd: str):

        res = subprocess.check_output(
            fr'reg add {device} /v *SpeedDuplex /t REG_SZ /d {spd} /f && reg add {device} /v *TCPChecksumOffloadIPv4 /t REG_SZ /d 3 /f && reg add {device} /v *TCPChecksumOffloadIPv6 /t REG_SZ /d 3 /f && reg add {device} /v *UDPChecksumOffloadIPv4 /t REG_SZ /d 3 /f && reg add {device} /v *UDPChecksumOffloadIPv6 /t REG_SZ /d 3 /f && reg add {device} /v WolShutdownLinkSpeed /t REG_SZ /d 2 /f',
            shell=True).decode()
        cls()
        if 'The operation completed successfully.' in res:
            print(f'''\n{lmagenta}[!] The Following Properties Has Been Changed:

        {green}Maximum  Speed  Set To ==> {white}True
        {green}Shutdown Speed  Set To ==> {white}False
        {green}TCP Offload     Set To ==> {white}Rx & Tx Enabled
        {green}UDP Pffload     Set To ==> {white}Rx & Tx Enabled''')

            return True

    def disable_nagle_alg():
        res = subprocess.check_output(
            r'reg query HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces', text=True,
            stderr=subprocess.PIPE)
        interfaces = res.strip().split('\n')
        for iface in interfaces:
            res = subprocess.check_output(f'reg query {iface}', text=True, stderr=subprocess.PIPE)
            if ips[0] in res:
                res = subprocess.check_output(
                    f'reg add {iface} /v TcpAckFrequency /t REG_DWORD /d 1 /f && reg add {iface} /v TCPNoDelay /t REG_DWORD /d 1 /f',
                    shell=True, text=True, stderr=subprocess.PIPE)
                if 'The operation completed successfully.' in res:
                    print(f'''{green}        Nagle's Algorithm Set To ==> {white}False''')
                    return True
        print(
            f'\n{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}The {green}Progress {white}Has Been Done !\n')

    transport_name = re.search('{.+}', get_transport_name(find_mac_address_of_current_adapter()[0])).group()

    try:
        device = find_adapter_registry_key(transport_name)

        values = find_high_value(device)

        values = list(dict.fromkeys(values))

        new_list = [int(i) for i in values]

        new_list.sort()

        highest_value = new_list[-1]

        if change_device_properties(device, str(highest_value)):

            if disable_nagle_alg():
                pass
            else:
                print(f'{red}[-] Error: {white}Unable To Disable Nagle\'s Algorithm !')
        else:
            print(f'\n{red}[-] Error: {white}There Was An Error While Changing The Device Properties')

    except Exception as e:
        print(e)
        time.sleep(3)

    input(
        f'{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}Hit {red}[Enter] {white}To Exit ')

if __name__ == '__main__':

    init(convert=True)

    red = Fore.RED
    yellow = Fore.YELLOW
    white = Fore.WHITE
    mg = Fore.MAGENTA
    green = Fore.GREEN
    lmagenta = Fore.LIGHTMAGENTA_EX

    intro()
    input(f'{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}Hit {red}[Enter] {white}To Start The Magic ')
    network_optimization()

    time.sleep(1)

    exit(0)

