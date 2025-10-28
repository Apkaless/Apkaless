import random
import os


class APKAC:
    def __init__(self) -> None:
        self.encrypted_data = ''
        self.key = self.key_generator(100)
        

    def load_file(self, file_path: str):
        """Read And Return File Content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
                if not data:
                    print('The File Can\'t Be Empty.')
                    return False
            return data
        except FileNotFoundError:
            print(f'No Such File Found: {file_path}\nPlease Make Sure The File Path is Correct')
            return False

    def key_generator(self, length: int):
        """Generates Random Salt"""
        return "".join(str(random.randint(0,9)) for _ in range(length))
    
    def crypt(self, file_path: str):
        """Crypt And Save The Given File"""
        content = self.load_file(file_path)
        if content:
            for c in range(len(content)):
                current_char = content[c]
                current_num = self.key[c % len(self.key)]
                self.encrypted_data += chr(ord(current_char) ^ ord(current_num))
            raw_encrypted = repr(self.encrypted_data)
            if self.write_encrypted_data(raw_encrypted, self.key):
                return True
            else:
                return False
        print('Error Reading File Content')
        return False

    def write_encrypted_data(self, data, key):
        buff = f"""
wopvEaTEcopFEavc = {data}
iOpvEoeaaeavocp = '{key}'
oIoeaTEAcvpae = ""
for i in range(len(wopvEaTEcopFEavc)):
    nOpcvaEaopcTEapcoTEac = wopvEaTEcopFEavc[i]
    qQoeapvTeaocpOcivNva = iOpvEoeaaeavocp[i % len(iOpvEoeaaeavocp)]
    oIoeaTEAcvpae += chr(ord(nOpcvaEaopcTEapcoTEac) ^ ord(qQoeapvTeaocpOcivNva))
eval(compile(oIoeaTEAcvpae, '<string>', 'exec'))
        """
        try:
            with open('encrypted_code.py', 'w', encoding='utf-8') as f:
                f.write(buff)
                return True
        except Exception as e:
            print(f'Error While Writing Encrypted Data: {str(e)}')
            return False

if __name__ == "__main__":
    crypter = APKAC()
    file = input(f'\n↳ Py File To Encrypt →  ')
    if file: 
        if crypter.crypt(file):
            print(f'\n[+] Encrypted And Saved To → {os.path.abspath('encrypted_code.py')}')
            input('\n')
        else:
            print('ERROR Encrypting The File')