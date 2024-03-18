import cloudscraper
import httpx
import time
from threading import Thread
import string
import random
import os
from colorama import Fore, init
import webbrowser


def logo():


    print(rf'''{cyan}
    ___          __         __              
   /   |  ____  / /______ _/ /__  __________
  / /| | / __ \/ //_/ __ `/ / _ \/ ___/ ___/
 / ___ |/ /_/ / ,< / /_/ / /  __(__  |__  ) 
/_/  |_/ .___/_/|_|\__,_/_/\___/____/____/  
      /_/                                   

      
[+] Name        : Discord Bot (Users Checker)
[+] Instagram   : Apkalees
[+] Github      : https://github.com/apkaless
[+] Nationality : Iraq


''')

    input('\n//////////==> [ ENTER ] <==////////// ')

    os.system('cls')



def internetChecker():

    print('\n[!] Checking Your Connection To The Internet ...\n')
    try:

        cloudscraper.create_scraper().get('https://www.google.com/')

        return 1
    
    except:

        return 0

def randomUser():

    letters = string.ascii_letters + string.digits

    username2 = ''.join(random.choice(letters) for i in range(3)) + ''.join('_')
    username3 = ''.join(random.choice(letters) for i in range(3)) + ''.join('.')
    username5 = ''.join('_') + ''.join(random.choice(letters) for i in range(3))
    username6 = ''.join('.') + ''.join(random.choice(letters) for i in range(3))
    username8 = ''.join(random.choice(letters) for i in range(2)) + ''.join('_') + ''.join(random.choice(letters) for i in range(1))
    username9 = ''.join(random.choice(letters) for i in range(2)) + ''.join('.') + ''.join(random.choice(letters) for i in range(1))
    username11 = ''.join(random.choice(letters) for i in range(1)) + ''.join('_') + ''.join(random.choice(letters) for i in range(2))
    username12 = ''.join(random.choice(letters) for i in range(1)) + ''.join('.') + ''.join(random.choice(letters) for i in range(2))

    users = [username2, username3,username5, username6, username8, username9, username11, username12]

    return users

def dominator(email, password):

    os.system('cls')

    with cloudscraper.create_scraper(debug=False) as s:
        

        login_url = 'https://discord.com/api/v9/auth/login'


        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Origin':'https://discord.com',
            'Referer':'https://discord.com/login',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
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
                   'Follow Me On Instagram ==> Apkaless', 'FBI AND CIA ARE COMING TO UR LOCATION MOVE AWAY RIGHT NOW', 
                   'You Got Detected By Discord Security System!!!!!', 
                   'I Love When Y O u Use UR Mind', 'This is a message from apkaless 2 u son of a good man: dont be bad guy.', 
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
        {cyan}[!] Total Checked Users: [{white}{len(checkedUsers)}{lightb}]
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
                        'Origin':'https://discord.com',
                        'Referer':'https://discord.com/login',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                        'X-Fingerprint': '&',
                        'X-Super-Properties': '&'
                    }

                    user = s.patch('https://discord.com/api/v9/users/@me', headers=headers2, json=data2, cookies=saved_cookies)
                
                    if 'code' in user.json():
                        falseUsers.append(username)
                        checkedUsers.append(username)
                        # print(f'\n{counter}) [-] Username Unavailable ===> {username}\n========================\n')
                    elif 'captcha_key' in user.json():
                        # print(f'{counter}) Captured User ===> {username}\n======================')
                        with open('captured.txt', 'a') as f:
                            f.writelines([f'====================\nCaptured By Apkaless\n====================\nUser: {username}\n====================\nFollow Me On Instagram ===> Apkaless\n====================\n', '\n'])
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


if __name__ == '__main__':

    init(convert=True)
    blue = Fore.BLUE
    red = Fore.RED
    green= Fore.GREEN
    white = Fore.WHITE
    yellow = Fore.YELLOW
    lightb = Fore.LIGHTBLUE_EX
    cyan = Fore.CYAN
    logoRights = logo()

    internet = internetChecker()

    if internet:
        os.system('cls')

    else:
        print('\n[!] No Internet Connection\n')
        time.sleep(3)
        exit(0)
        
    while True:
        print(f'''{yellow}[!] In order to use this tool you need to do this:{white}
              
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
    
    dominator_thread = Thread(target=dominator, args=(emailInput, passwordInput))

    dominator_thread.start()