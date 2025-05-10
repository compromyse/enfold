from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os
import json

REQUEST_KEY = bytes.fromhex('4D6251655468576D5A7134743677397A')
RESPONSE_KEY = bytes.fromhex('3273357638782F413F4428472B4B6250')
GLOBAL_IV = "556A586E32723575"
IV_INDEX = '0'
RANDOMIV = os.urandom(8).hex()
IV = bytes.fromhex(GLOBAL_IV + RANDOMIV)

class Encryption:
    @staticmethod
    def encrypt(data):
        cipher = AES.new(REQUEST_KEY, AES.MODE_CBC, IV)
        padded_data = pad(json.dumps(data).encode(), 16)
        ct = cipher.encrypt(padded_data)
        ct_b64 = base64.b64encode(ct).decode()
        return RANDOMIV + str(IV_INDEX) + ct_b64

    @staticmethod
    def decrypt(data):
        data = data.strip()
        iv_hex = data[:32]
        ct_b64 = data[32:]

        iv = bytes.fromhex(iv_hex)
        ct = base64.b64decode(ct_b64)
        cipher = AES.new(RESPONSE_KEY, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), 16)
        return json.loads(pt.decode(errors="ignore"))
