from Crypto.Cipher import AES
import base64
import binascii

__all__ = ["encryption"]


class MData:

    def __init__(self, data=b"", character_set='utf-8'):
        self.data = data
        self.character_set = character_set

    def save_data(self, file_name):
        with open(file_name, 'wb') as f:
            f.write(self.data)

    def from_string(self, data):
        self.data = data.encode(self.character_set)
        return self.data

    def from_base64(self, data):
        self.data = base64.b64decode(data.encode(self.character_set))
        return self.data

    def from_hex(self, data):
        self.data = binascii.a2b_hex(data)
        return self.data

    def to_string(self):
        return self.data.decode(self.character_set)

    def to_base64(self):
        return base64.b64encode(self.data).decode()

    def to_hex(self):
        return binascii.b2a_hex(self.data).decode()

    def to_bytes(self):
        return self.data

    def __str__(self):
        try:
            return self.to_string()
        except ValueError:
            return self.to_base64()


class AESCryptor:
    def __init__(self, key, mode, iv, padding_mode="NoPadding", character_set="utf-8"):
        """
        构建一个AES对象
        key: 秘钥，字节型数据
        mode: 使用模式，只提供两种，AES.MODE_CBC, AES.MODE_ECB
        iv： iv偏移量，字节型数据
        paddingMode: 填充模式，默认为NoPadding, 可选NoPadding，ZeroPadding，PKCS5Padding，PKCS7Padding
        characterSet: 字符集编码
        """
        self.key = key
        self.mode = mode
        self.iv = iv
        self.characterSet = character_set
        self.paddingMode = padding_mode
        self.data = b""

    @staticmethod
    def _zero_padding(data):
        data += b'\x00'
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    @staticmethod
    def _strip_zero_padding(data):
        data = data[:-1]
        while len(data) % 16 != 0:
            data = data.rstrip(b'\x00')
            if data[-1] != b"\x00":
                break
        return data

    @staticmethod
    def _pkcs5_7padding(data):
        need_size = 16 - len(data) % 16
        if need_size == 0:
            need_size = 16
        return data + need_size.to_bytes(1, 'little') * need_size

    @staticmethod
    def _strip_pkcs5_7padding(data):
        padding_size = data[-1]
        return data.rstrip(padding_size.to_bytes(1, 'little'))

    def _padding_data(self, data):
        if self.paddingMode == "NoPadding":
            if len(data) % 16 == 0:
                return data
            else:
                return self._zero_padding(data)
        elif self.paddingMode == "ZeroPadding":
            return self._zero_padding(data)
        elif self.paddingMode == "PKCS5Padding" or self.paddingMode == "PKCS7Padding":
            return self._pkcs5_7padding(data)
        else:
            print("不支持Padding")

    def _strip_padding_data(self, data):
        if self.paddingMode == "NoPadding":
            return self._strip_zero_padding(data)
        elif self.paddingMode == "ZeroPadding":
            return self._strip_zero_padding(data)

        elif self.paddingMode == "PKCS5Padding" or self.paddingMode == "PKCS7Padding":
            return self._strip_pkcs5_7padding(data)
        else:
            print("不支持Padding")

    def set_character_set(self, characterSet):
        """
            设置字符集编码
            characterSet: 字符集编码
        """
        self.characterSet = characterSet

    def set_padding_mode(self, mode):
        """
            设置填充模式
            mode: 可选NoPadding，ZeroPadding，PKCS5Padding，PKCS7Padding
        """
        self.paddingMode = mode

    def decrypt_from_base64(self, en_text):
        """
            从base64编码字符串编码进行AES解密
            en_text: 数据类型str
        """
        m_data = MData(character_set=self.characterSet)
        self.data = m_data.from_base64(en_text)
        return self._decrypt()

    def decrypt_from_hex(self, en_text):
        """
            从hex编码字符串编码进行AES解密
            en_text: 数据类型str
        """
        m_data = MData(character_set=self.characterSet)
        self.data = m_data.from_hex(en_text)
        return self._decrypt()

    def decrypt_from_string(self, en_text):
        """
            从字符串进行AES解密
            en_text: 数据类型str
        """
        m_data = MData(character_set=self.characterSet)
        self.data = m_data.from_string(en_text)
        return self._decrypt()

    def decrypt_from_bytes(self, en_text):
        """
            从二进制进行AES解密
            en_text: 数据类型bytes
        """
        self.data = en_text
        return self._decrypt()

    def encrypt_from_string(self, data):
        """
            对字符串进行AES加密
            data: 待加密字符串，数据类型为str
        """
        self.data = data.encode(self.characterSet)
        return self._encrypt()

    def _encrypt(self):
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return

        data = self._padding_data(self.data)
        en_data = aes.encrypt(data)
        return MData(en_data)

    def _decrypt(self):
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return
        data = aes.decrypt(self.data)
        m_data = MData(self._strip_padding_data(data), character_set=self.characterSet)
        return m_data


def encryption(data: str, key: str):
    aes = AESCryptor(key.encode(), AES.MODE_ECB, None, padding_mode="PKCS7Padding", character_set='utf-8')
    m_data = aes.encrypt_from_string(data)
    res = m_data.to_base64()
    return base64.b64encode(res.encode()).decode()
