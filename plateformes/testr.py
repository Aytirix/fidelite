from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import json
import random

class AESHelper:
    def __init__(self):
        self.key = self.random_key(16)
        self.iv = "@qwertyuiop12344".encode('utf-8')

    def random_key(self, length):
            characters = "@abcdefghijklmnopqrstuvwxyz123456789"
            return ''.join(random.choice(characters) for _ in range(length)).encode('utf-8')

    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv, padding='PKCS7')
        padded_data = self.pad(data)
        return base64.b64encode(cipher.encrypt(padded_data)).decode('utf-8')

    def pad(self, data):
        padding_len = 16 - len(data) % 16
        padding = chr(padding_len) * padding_len
        return data.encode('utf-8') + padding.encode('utf-8')

class RSAHelper:
    def __init__(self, public_key_pem):
        self.public_key = RSA.import_key(public_key_pem)

    def encrypt_with_public_key(self, data):
        cipher = PKCS1_OAEP.new(self.public_key)
        encrypted_data = cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted_data).decode('utf-8')

def login(email, password, rsa_helper, aes_helper):
    encrypted_key = rsa_helper.encrypt_with_public_key(aes_helper.key)
    encrypted_data = {
        'email': aes_helper.encrypt(email),
        'password': aes_helper.encrypt(password)
    }
    encrypted_data_json = aes_helper.encrypt(json.dumps(encrypted_data))
    # Vous devez envoyer encrypted_key et encrypted_data_json à votre serveur ici
    # Par exemple : return http.post(api_url, {'data': encrypted_data_json, 'key': encrypted_key})
    return encrypted_key, encrypted_data_json

# Exemple d'utilisation
public_key = '''-----BEGIN PUBLIC KEY-----\n  MIGeMA0GCSqGSIb3DQEBAQUAA4GMADCBiAKBgHO4AqKut5xbco9jgfz+bqkx9v0M\nO9t5DGzZEltqqZE5tNzHbve2D+KPWTeD+G9q2PilkPPHRz2+r5MgwlD4dGP6zum3\nhNj27CCIgUeaIJGhX/JlmBO3bgFGCcuemuKc+ygFJYvf0RzCo5svfn/6cKSHeovl\norMqQbQU3GrHLVA9AgMBAAE=\n  -----END PUBLIC KEY-----'''

aes_helper = AESHelper()
rsa_helper = RSAHelper(public_key)

# Remplacer par vos vraies données de connexion
email = "huklhuk@regre.gt"
password = "huklhuk@regre.gt"

encrypted_key, encrypted_data_json = login(email, password, rsa_helper, aes_helper)

print(f'encrypted_key: {encrypted_key}')
print(f'encrypted_data_json: {encrypted_data_json}')
