from Crypto.Cipher import AES
from Crypto import Random
import base64
import msvcrt,sys 


class AESEncrypter(object):
    key = None
    def __init__(self, key):
        AESEncrypter.key = self.format_key(key)

    @classmethod
    def format_key(cls, key):
        sub_key = '*' * (16 - len(key))
        key += sub_key
        return key

    @classmethod
    def padding(cls, s):
        pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(0) #chr(AES.block_size - len(s) % AES.block_size)
        return pad(s)

    @classmethod
    def unpadding(cls, s):
        # unpad = lambda s : s[:-ord(s[len(s)-1:])]
        unpad = lambda s: s.rstrip(chr(0))
        return unpad(s)

    @classmethod
    def encrypt(cls, text, key=None):
        key = cls.key if not key else cls.format_key(key)
        text = AESEncrypter.padding(text)
        iv = Random.new().read(AES.block_size)
        cryptor = AES.new(key, AES.MODE_CBC, iv)
        result = base64.b64encode(iv + cryptor.encrypt(text))
        return result.decode()

    @classmethod
    def decrypt(cls, text, key=None):
        key = cls.key if not key else cls.format_key(key)
        text = base64.b64decode(text)
        print(text, len(text[:AES.block_size]))
        cryptor = AES.new(key, AES.MODE_CBC, text[:AES.block_size])
        result = cryptor.decrypt(text[AES.block_size:])
        return AESEncrypter.unpadding(result.decode())



def key_input():    
    sys.stdout.write('key: ')
    sys.stdout.flush()
    chars = []
    while True:        
        newChar = msvcrt.getch().decode()
        if newChar == '\x00':
            continue
        # print('newchar is ', repr(newChar))
        if newChar in ['\r', '\n']:           
            break        
        elif newChar == '\b': # 如果是退格，则删除末尾一位            
            if chars:                
                del chars[-1]                
                msvcrt.putch('\b'.encode()) # 控制台回退一格                
                msvcrt.putch(' '.encode()) # 打印空格替换掉*                
                msvcrt.putch('\b'.encode())        
        else:            
            chars.append(newChar)            
            sys.stdout.write('*')
            sys.stdout.flush()
    print()
    return ''.join(chars)




if __name__ == '__main__':
    # key = '1314' * 4 
    # res = Encrypter.encrypt("wa.520", key)
    # print(Encrypter.decrypt(text=res, key=key))
    pwd = key_input()
    print(pwd)