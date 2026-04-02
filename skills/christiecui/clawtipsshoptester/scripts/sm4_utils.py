import base64
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT

def sm4_encrypt(plain_text, key):
    """SM4 ECB模式加密"""
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_ENCRYPT)
    # 填充：PKCS7
    block_size = 16
    padding_length = block_size - len(plain_text) % block_size
    padded_data = plain_text.encode('utf-8') + bytes([padding_length]) * padding_length
    encrypted = crypt_sm4.crypt_ecb(padded_data)
    return base64.b64encode(encrypted).decode('utf-8')

def sm4_decrypt(encrypted_text, key):
    """SM4 ECB模式解密"""
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_DECRYPT)
    encrypted_data = base64.b64decode(encrypted_text)
    decrypted = crypt_sm4.crypt_ecb(encrypted_data)
    # 去除填充
    padding_length = decrypted[-1]
    return decrypted[:-padding_length].decode('utf-8')
