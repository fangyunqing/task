# @Time    : 2023/06/06 14:43
# @Author  : fyq
# @File    : rsa.py
# @Software: PyCharm

__author__ = 'fyq'

import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher

__all__ = ["encryption"]


def encryption(pubkey: str, data: str):
    pubkey = RSA.importKey(pubkey)
    cipher = PKCS1_cipher.new(pubkey)
    encrypt_text = base64.b64encode(cipher.encrypt(data.encode()))
    return encrypt_text.decode()
