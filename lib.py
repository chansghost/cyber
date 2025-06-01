from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from cryptography.hazmat.primitives import padding

# def pad(data, block_size):
#     padding_length = block_size - len(data) % block_size
#     padding = bytes([padding_length] * padding_length)
#     return data + padding

# def unpad(data):
#     padding_length = data[-1]
#     if padding_length == 0 or padding_length > len(data):
#         raise ValueError("Niepoprawne wypełnienie")
#     if any(byte != padding_length for byte in data[-padding_length:]):
#         raise ValueError("Niepoprawne wypełnienie")
#     return data[:-padding_length]


def increment_counter(counter):
    counter_int = int.from_bytes(counter, byteorder='big') + 1
    return counter_int.to_bytes(len(counter), byteorder='big')

def encrypt_block(block, key):
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(block) + encryptor.finalize()

def decrypt_block(block, key):
    if len(block) != len(key):
        raise ValueError("Block and key must be of equal length")
    decrypted_block = bytes([block[i] ^ key[i] for i in range(len(block))])
    return decrypted_block

def encrypt_block_xor(block, key): #do podmiany na cos lepszego
    if len(block) != len(key):
        raise ValueError("Block and key must be of equal length")
    encrypted_block = bytes([block[i] ^ key[i] for i in range(len(block))])
    return encrypted_block

def decrypt_block_xor(block, key): #do podmiany na cos lepszego
    if len(block) != len(key):
        raise ValueError("Block and key must be of equal length")
    decrypted_block = bytes([block[i] ^ key[i] for i in range(len(block))])
    return decrypted_block

def ctr_encrypt(plaintext, key, nonce):
    # Stworzenie obiektu szyfrującego w trybie CTR
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()

def ctr_decrypt(ciphertext, key, nonce):
    # Stworzenie obiektu deszyfrującego w trybie CTR
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


#ECB - to musicie poprawić bo jest źle - encryptowanie i decyptowanie xorem jest do podmianki
def ecb_encrypt(plaintext, key):
    block_size = 16
    key = key.ljust(block_size, b'\0')[:block_size]  # upewnij się, że key ma długość 16 bajtów
    cipher = AES.new(key, AES.MODE_ECB)
    padded_plaintext = pad(plaintext, block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    return ciphertext

def ecb_decrypt(ciphertext, key):
    block_size = 16
    key = key.ljust(block_size, b'\0')[:block_size]
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(ciphertext)
    plaintext = unpad(decrypted, block_size)
    return plaintext


#CBC
def cbc_encrypt(plaintext, key, iv):
    # Add padding to the plaintext to make it a multiple of the block size
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()

    # Create a cipher object using the CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(padded_plaintext) + encryptor.finalize()

def cbc_decrypt(ciphertext, key, iv):
    # Create a cipher object using the CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Remove padding from the plaintext
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext