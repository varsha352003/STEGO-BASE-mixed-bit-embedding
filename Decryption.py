# Decryption.py — Chaotic decryption with passphrase (BINARY-SAFE)
import os
import base64
import zlib
from chaotic_crypto import decrypt_with_chaos

# --------------------------------------------------
PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
EXTRACTED_ENCRYPTED_TXT = os.path.join(PROJECT_DIR, "extracted_encrypted_message.txt")
DECRYPTED_MESSAGE_TXT = os.path.join(PROJECT_DIR, "decrypted_message.txt")
PASS_FILE = os.path.join(PROJECT_DIR, "pass.txt")
PASS_ENV = "STEGO_PASS"


def get_passphrase() -> bytes:
    pw = os.environ.get(PASS_ENV)
    if pw:
        return pw.encode("utf-8")

    if os.path.exists(PASS_FILE):
        with open(PASS_FILE, "rb") as f:
            return f.read().strip()

    return input("Enter passphrase (visible): ").encode("utf-8")


def load_encrypted_bytes(path: str) -> bytes:

    with open(path, "rb") as f:
        return f.read()


def save_plaintext(data: bytes, path: str):

    try:
        text = data.decode("utf-8")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except UnicodeDecodeError:
        with open(path, "wb") as f:
            f.write(data)


def decrypt_message(encrypted_bytes: bytes, passphrase: bytes) -> bytes:
    
    token_b64 = encrypted_bytes.decode("ascii")

    envelope = base64.b64decode(token_b64)

    compressed = decrypt_with_chaos(envelope, passphrase)

    return zlib.decompress(compressed)


if __name__ == "__main__":
    print(" Chaotic Decryption Module")
    print("=" * 50)

    encrypted_bytes = load_encrypted_bytes(EXTRACTED_ENCRYPTED_TXT)
    print(f" Extracted payload size: {len(encrypted_bytes)} bytes")

    pw = get_passphrase()
    print(f" Passphrase obtained: {len(pw)} bytes")

    try:
        plaintext_bytes = decrypt_message(encrypted_bytes, pw)
        save_plaintext(plaintext_bytes, DECRYPTED_MESSAGE_TXT)

        print(f" Decryption successful")
        print(f" Output saved to: {DECRYPTED_MESSAGE_TXT}")
        print("=" * 50)

    except Exception as e:
        print(f" Decryption failed: {e}")
        print(" Check payload integrity or passphrase")
        print("=" * 50)
