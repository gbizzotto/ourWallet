from Crypto.Cipher import AES
import hashlib

iv = b"ourWalletCryptoX"

def encrypt(plain_text, key):
    key = hashlib.sha256(hashlib.sha256(key).digest()).digest()[:16]
    return AES.new(key, AES.MODE_CFB, iv).encrypt(str.encode(plain_text))

def decrypt(enc_text, key):
    key = hashlib.sha256(hashlib.sha256(key).digest()).digest()[:16]
    return AES.new(key, AES.MODE_CFB, iv).decrypt(enc_text).decode()

if __name__ == "__main__":
    plaintext = b"Testing AES encryption/decryption in techieshouts.com"
    key = b"YourSampleEncKey"
    print("Plain text: ",plaintext)
    print("Calling encryption library")
    encryptedtext = encrypt(plaintext,key)
    print("Encrypted text")
    print(encryptedtext.hex())
    decryptedtext = decrypt(encryptedtext,key)
    print("Decrypted text")
    print(decryptedtext)
