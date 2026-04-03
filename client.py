import os
import base64
import zlib
import json
import requests
import sys
from chaotic_crypto import decrypt_with_chaos

PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
PASS_FILE = os.path.join(PROJECT_DIR, "pass.txt")
PASS_ENV = "STEGO_PASS"
DECRYPTED_MESSAGE_TXT = os.path.join(PROJECT_DIR, "decrypted_message.txt")

DEFAULT_SERVER_URL = "http://127.0.0.1:5000"

class StegoClient:
    def __init__(self, server_url=DEFAULT_SERVER_URL):
        self.server_url = server_url
        self.session = requests.Session()
    
    def get_passphrase(self) -> bytes:
        pw = os.environ.get(PASS_ENV)
        if pw:
            return pw.encode("utf-8")
        
        if os.path.exists(PASS_FILE):
            with open(PASS_FILE, "r", encoding="utf-8") as f:
                return f.read().strip().encode("utf-8")
        
        return b"default_passphrase"
    
    def check_server_health(self) -> bool:
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Server health check failed: {e}")
            return False
    
    def get_server_info(self) -> dict:
        try:
            response = self.session.get(f"{self.server_url}/server-info", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Failed to get server info: {e}")
            return {}
    
    def request_encryption(self, plaintext: str) -> str:
        try:
            payload = {"message": plaintext}
            response = self.session.post(
                f"{self.server_url}/encrypt",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("encrypted_message", "")
            else:
                print(f"Server error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Encryption request failed: {e}")
            return None
    
    def request_batch_encryption(self, messages: list) -> list:
        try:
            payload = {"messages": messages}
            response = self.session.post(
                f"{self.server_url}/encrypt-batch",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("encrypted_messages", [])
            else:
                print(f"Server error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"Batch encryption request failed: {e}")
            return []
    
    def decrypt_message(self, encrypted_b64: str) -> str:
        try:
            passphrase = self.get_passphrase()
            
            envelope = base64.b64decode(encrypted_b64)
            compressed = decrypt_with_chaos(envelope, passphrase)
            plaintext_bytes = zlib.decompress(compressed)
            plaintext = plaintext_bytes.decode("utf-8")
            
            return plaintext
        
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None
    
    def decrypt_batch(self, encrypted_messages: list) -> list:
        decrypted = []
        for encrypted_b64 in encrypted_messages:
            plaintext = self.decrypt_message(encrypted_b64)
            if plaintext:
                decrypted.append(plaintext)
        return decrypted
    
    def save_plaintext(self, plaintext: str, path: str = DECRYPTED_MESSAGE_TXT):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(plaintext)
            print(f"Plaintext saved to: {path}")
            return True
        except Exception as e:
            print(f"Failed to save plaintext: {e}")
            return False

def encrypt_and_retrieve(client: StegoClient, plaintext: str) -> str:
    print("Requesting encryption from server...")
    encrypted = client.request_encryption(plaintext)
    
    if encrypted:
        print(f"Received encrypted message ({len(encrypted)} chars)")
        return encrypted
    
    return None

def retrieve_and_decrypt(client: StegoClient, encrypted_b64: str) -> str:
    print("Decrypting message on client side...")
    plaintext = client.decrypt_message(encrypted_b64)
    
    if plaintext:
        print(f"Decryption successful ({len(plaintext)} chars)")
        return plaintext
    
    return None

def main():
    client = StegoClient()
    
    if not client.check_server_health():
        print("Cannot connect to server")
        return
    
    print("Connected to server")
    info = client.get_server_info()
    print(f"Server info: {json.dumps(info, indent=2)}")
    
    test_message = "I am working on video stegnography project."
    
    encrypted = encrypt_and_retrieve(client, test_message)
    
    if encrypted:
        decrypted = retrieve_and_decrypt(client, encrypted)
        
        if decrypted:
            print(f"Original: {test_message}")
            print(f"Decrypted: {decrypted}")
            
            if test_message == decrypted:
                print("Encryption-Decryption pipeline successful!")
                client.save_plaintext(decrypted)
            else:
                print("Mismatch in encryption-decryption!")
        else:
            print("Decryption failed")
    else:
        print("Encryption request failed")

if __name__ == "__main__":
    main()
