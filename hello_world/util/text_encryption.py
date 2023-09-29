from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import hashlib


def encrypt(password, data):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode() if type(password)==str else password)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
    return base64.encodebytes(salt + nonce + ct).decode('utf-8')

def decrypt(password, data):

    data = base64.decodebytes(data.encode('utf-8'))
    salt = data[:16]
    nonce = data[16:28]
    ct = data[28:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode() if type(password)==str else password)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None).decode('utf-8')


def get_md5(password):
    password = password.encode() if type(password) == str else password
    checksum = hashlib.md5(password)
    checksum = checksum.hexdigest()
    return checksum
