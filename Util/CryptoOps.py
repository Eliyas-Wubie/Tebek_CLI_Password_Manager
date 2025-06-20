import json
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def decrypt_data(eData,key=""):
    if key=="":
        f = get_encryption_object()
        decrypted_bytes = f.decrypt(eData)
        decrypted_json = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_json)
        return decrypted_data
    else:
        f = get_encryption_object(key)
        decrypted_bytes = f.decrypt(eData)
        decrypted_json = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_json)
        return decrypted_data

def encrypt_data(dData,key=""):
    if key=="":
        json_data = json.dumps(dData).encode('utf-8')
        f = get_encryption_object()
        encrypted = f.encrypt(json_data)
        return encrypted
    else:
        json_data = json.dumps(dData).encode('utf-8')
        f = get_encryption_object(key)
        encrypted = f.encrypt(json_data)
        return encrypted

def get_key(): 
    key = "I3SJTsjh3tzanQR67JBRhcHNmW55LbtZlR87-3CEVs8=" # static key
    return key

def get_encryption_object(key=""):
    if key=="":
        key_str=get_key()
        f = Fernet(key_str)
        return f
    else:
        key_str=key
        f = Fernet(key_str)
        return f
def generate_fernet_key_from_password(password):
    STATIC_SALT = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F'

    # Derive key using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=STATIC_SALT,
        iterations=100_000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key
