from Crypto.Cipher import AES
import hashlib

iv = b"ourWalletCryptoX"

def encrypt(plain_text, key):
    key = hashlib.sha256(hashlib.sha256(key).digest()).digest()[:16]
    return AES.new(key, AES.MODE_CFB, iv).encrypt(str.encode(plain_text))

def decrypt(enc_text, key):
    key = hashlib.sha256(hashlib.sha256(key).digest()).digest()[:16]
    return AES.new(key, AES.MODE_CFB, iv).decrypt(enc_text).decode()

def normalize(der_signature_bytes):
    size_r = der_signature_bytes[3]
    size_s = der_signature_bytes[4+size_r+2]
    pos_s = 7+size_r
    r = der_signature_bytes[4:4+size_r]
    s = der_signature_bytes[pos_s:pos_s+size_s]
    r_dec = int.from_bytes(r, "big")
    s_dec = int.from_bytes(s, "big")
    if s > r:
        N = 115792089237316195423570985008687907852837564279074904382605163141518161494337
        s_dec = N - s_dec
        new_s = str(s_dec).encode()
        size_difference = len(s) - len(new_s)
        der_signature_bytes[pos_s:pos_s+size_s] = new_s
        der_signature_bytes[4+size_r+2] -= size_difference
        der_signature_bytes[         1] -= size_difference
    return der_signature_bytes

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
