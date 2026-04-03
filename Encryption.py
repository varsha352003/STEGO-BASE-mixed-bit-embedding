
import os, base64, zlib
from chaotic_crypto import encrypt_with_chaos


PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
ENCRYPTED_MESSAGE_TXT = os.path.join(PROJECT_DIR, "encrypted_message.txt")
PLAINTEXT_FILE = os.path.join(PROJECT_DIR, "message.txt")  
PASS_FILE = os.path.join(PROJECT_DIR, "pass.txt")          
PASS_ENV = "STEGO_PASS"
MAX_MESSAGE_SIZE = 50000  # Limit message to 50,000 characters                                     

def get_passphrase() -> bytes:
    """Get passphrase from env var, file, or prompt"""

    pw = os.environ.get(PASS_ENV)
    if pw:
        return pw.encode("utf-8")

    if os.path.exists(PASS_FILE):
        with open(PASS_FILE, "r", encoding="utf-8") as f:
            return f.read().strip().encode("utf-8")

    return input("Enter passphrase (visible): ").encode("utf-8")

def load_plaintext() -> str:
    """Load plaintext message from file or use default"""
    if os.path.exists(PLAINTEXT_FILE):
        with open(PLAINTEXT_FILE, "r", encoding="utf-8") as f:
            plaintext = f.read()
    else:
        plaintext = "This is a test message hidden in the video." * 100000
    
    # Limit to MAX_MESSAGE_SIZE
    if len(plaintext) > MAX_MESSAGE_SIZE:
        plaintext = plaintext[:MAX_MESSAGE_SIZE]
        print(f" ⚠️  Message truncated to {MAX_MESSAGE_SIZE} characters")
    
    return plaintext

def encrypt_message(plaintext: str, passphrase: bytes) -> str:
    
    compressed = zlib.compress(plaintext.encode("utf-8"))
    
   
    envelope = encrypt_with_chaos(compressed, passphrase)
    
  
    return base64.b64encode(envelope).decode("utf-8")

def save_text(s: str, path: str):
    """Save text to file"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)

if __name__ == "__main__":
    print(" Chaotic Encryption Module")
    print("=" * 50)
    
    plaintext = load_plaintext()
    print(f" Plaintext loaded: {len(plaintext)} characters")
    
    pw = get_passphrase()
    print(f" Passphrase obtained: {len(pw)} bytes")
    
    print(" Encrypting with chaotic keystream...")
    token = encrypt_message(plaintext, pw)
    
    save_text(token, ENCRYPTED_MESSAGE_TXT)
    
    print(f"Encrypted message saved to: {ENCRYPTED_MESSAGE_TXT}")
    print(f"Encrypted size: {len(token)} base64 characters")
    print(f"Compression ratio: {len(plaintext) / len(token):.2f}x")
    print("=" * 50)