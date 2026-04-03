import os
import base64
import zlib
from typing import Optional, Tuple, List
from chaotic_crypto import encrypt_with_chaos, decrypt_with_chaos

PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
PASS_FILE = os.path.join(PROJECT_DIR, "pass.txt")
PASS_ENV = "STEGO_PASS"

class SecureEncryptionManager:
    MAX_MESSAGE_SIZE = 50000
    COMPRESSION_LEVEL = 9
    
    @staticmethod
    def get_passphrase() -> bytes:
        pw = os.environ.get(PASS_ENV)
        if pw:
            return pw.encode("utf-8")
        
        if os.path.exists(PASS_FILE):
            with open(PASS_FILE, "r", encoding="utf-8") as f:
                return f.read().strip().encode("utf-8")
        
        return b"default_passphrase"
    
    @staticmethod
    def validate_message(message: str) -> Tuple[bool, Optional[str]]:
        if not message:
            return False, "Message cannot be empty"
        
        if len(message) > SecureEncryptionManager.MAX_MESSAGE_SIZE:
            return False, f"Message exceeds max size of {SecureEncryptionManager.MAX_MESSAGE_SIZE}"
        
        return True, None
    
    @staticmethod
    def encrypt_payload(plaintext: str, passphrase: Optional[bytes] = None) -> str:
        passphrase = passphrase or SecureEncryptionManager.get_passphrase()
        
        is_valid, error = SecureEncryptionManager.validate_message(plaintext)
        if not is_valid:
            raise ValueError(error)
        
        compressed = zlib.compress(
            plaintext.encode("utf-8"),
            level=SecureEncryptionManager.COMPRESSION_LEVEL
        )
        
        envelope = encrypt_with_chaos(compressed, passphrase)
        encrypted_b64 = base64.b64encode(envelope).decode("utf-8")
        
        return encrypted_b64
    
    @staticmethod
    def decrypt_payload(encrypted_b64: str, passphrase: Optional[bytes] = None) -> str:
        passphrase = passphrase or SecureEncryptionManager.get_passphrase()
        
        try:
            envelope = base64.b64decode(encrypted_b64)
            compressed = decrypt_with_chaos(envelope, passphrase)
            plaintext_bytes = zlib.decompress(compressed)
            plaintext = plaintext_bytes.decode("utf-8")
            
            return plaintext
        
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    @staticmethod
    def batch_encrypt(messages: List[str], passphrase: Optional[bytes] = None) -> List[str]:
        passphrase = passphrase or SecureEncryptionManager.get_passphrase()
        encrypted = []
        
        for message in messages:
            is_valid, error = SecureEncryptionManager.validate_message(message)
            if not is_valid:
                raise ValueError(f"Invalid message: {error}")
            
            encrypted_msg = SecureEncryptionManager.encrypt_payload(message, passphrase)
            encrypted.append(encrypted_msg)
        
        return encrypted
    
    @staticmethod
    def batch_decrypt(encrypted_messages: List[str], passphrase: Optional[bytes] = None) -> List[str]:
        passphrase = passphrase or SecureEncryptionManager.get_passphrase()
        plaintext_list = []
        
        for encrypted_b64 in encrypted_messages:
            plaintext = SecureEncryptionManager.decrypt_payload(encrypted_b64, passphrase)
            plaintext_list.append(plaintext)
        
        return plaintext_list
    
    @staticmethod
    def encrypt_file(input_path: str, output_path: str, passphrase: Optional[bytes] = None):
        passphrase = passphrase or SecureEncryptionManager.get_passphrase()
        
        with open(input_path, "r", encoding="utf-8") as f:
            plaintext = f.read()
        
        encrypted = SecureEncryptionManager.encrypt_payload(plaintext, passphrase)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(encrypted)
    
    @staticmethod
    def decrypt_file(input_path: str, output_path: str, passphrase: Optional[bytes] = None):
        passphrase = passphrase or SecureEncryptionManager.get_passphrase()
        
        with open(input_path, "r", encoding="utf-8") as f:
            encrypted_b64 = f.read()
        
        plaintext = SecureEncryptionManager.decrypt_payload(encrypted_b64, passphrase)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(plaintext)

class PipelineOrchestrator:
    
    def __init__(self):
        self.encryption_manager = SecureEncryptionManager()
    
    def prepare_payload(self, message: str) -> str:
        return self.encryption_manager.encrypt_payload(message)
    
    def recover_payload(self, encrypted_b64: str) -> str:
        return self.encryption_manager.decrypt_payload(encrypted_b64)
    
    def get_encryption_stats(self, plaintext: str) -> dict:
        encrypted = self.encryption_manager.encrypt_payload(plaintext)
        
        compression_ratio = len(plaintext) / len(encrypted)
        
        return {
            "original_size": len(plaintext),
            "encrypted_size": len(encrypted),
            "compression_ratio": f"{compression_ratio:.2f}x",
            "encrypted_preview": encrypted[:50] + "..."
        }
    
    def verify_integrity(self, plaintext: str) -> bool:
        encrypted = self.encryption_manager.encrypt_payload(plaintext)
        decrypted = self.encryption_manager.decrypt_payload(encrypted)
        
        return plaintext == decrypted

def encrypt_for_embedding(message: str) -> str:
    return SecureEncryptionManager.encrypt_payload(message)

def decrypt_after_extraction(encrypted_b64: str) -> str:
    return SecureEncryptionManager.decrypt_payload(encrypted_b64)

def encrypt_message_batch(messages: List[str]) -> List[str]:
    return SecureEncryptionManager.batch_encrypt(messages)

def decrypt_message_batch(encrypted_messages: List[str]) -> List[str]:
    return SecureEncryptionManager.batch_decrypt(encrypted_messages)

def get_message_hash(message: str) -> str:
    import hashlib
    return hashlib.sha256(message.encode()).hexdigest()

def verify_message_hash(message: str, message_hash: str) -> bool:
    return get_message_hash(message) == message_hash

class AdaptivePayloadHandler:
    
    SMALL_PAYLOAD_THRESHOLD = 1024
    MEDIUM_PAYLOAD_THRESHOLD = 1024 * 100
    
    @staticmethod
    def handle_payload(payload: str, strategy: str = "auto") -> str:
        size = len(payload)
        
        if strategy == "auto":
            if size < AdaptivePayloadHandler.SMALL_PAYLOAD_THRESHOLD:
                strategy = "standard"
            elif size < AdaptivePayloadHandler.MEDIUM_PAYLOAD_THRESHOLD:
                strategy = "optimized"
            else:
                strategy = "chunked"
        
        if strategy == "standard":
            return SecureEncryptionManager.encrypt_payload(payload)
        
        elif strategy == "optimized":
            optimized_payload = payload.strip()
            return SecureEncryptionManager.encrypt_payload(optimized_payload)
        
        elif strategy == "chunked":
            chunk_size = AdaptivePayloadHandler.MEDIUM_PAYLOAD_THRESHOLD
            chunks = [payload[i:i+chunk_size] for i in range(0, len(payload), chunk_size)]
            encrypted_chunks = []
            
            for chunk in chunks:
                encrypted = SecureEncryptionManager.encrypt_payload(chunk)
                encrypted_chunks.append(encrypted)
            
            import json
            return base64.b64encode(
                json.dumps({"chunks": encrypted_chunks}).encode()
            ).decode()
        
        else:
            return SecureEncryptionManager.encrypt_payload(payload)
    
    @staticmethod
    def recover_payload(encrypted_payload: str, strategy: str = "auto") -> str:
        try:
            data = base64.b64decode(encrypted_payload)
            import json
            parsed = json.loads(data.decode())
            
            if "chunks" in parsed:
                chunks = parsed["chunks"]
                recovered_chunks = []
                
                for chunk in chunks:
                    plaintext = SecureEncryptionManager.decrypt_payload(chunk)
                    recovered_chunks.append(plaintext)
                
                return "".join(recovered_chunks)
            
            else:
                return SecureEncryptionManager.decrypt_payload(encrypted_payload)
        
        except:
            return SecureEncryptionManager.decrypt_payload(encrypted_payload)

if __name__ == "__main__":
    test_message = "This is a secure test message for the pipeline."
    
    print("Testing SecureEncryptionManager:")
    print("-" * 50)
    
    encrypted = SecureEncryptionManager.encrypt_payload(test_message)
    print(f"Original: {test_message}")
    print(f"Encrypted size: {len(encrypted)}")
    
    decrypted = SecureEncryptionManager.decrypt_payload(encrypted)
    print(f"Decrypted: {decrypted}")
    print(f"Verified: {test_message == decrypted}")
    
    print("\nTesting PipelineOrchestrator:")
    print("-" * 50)
    
    orchestrator = PipelineOrchestrator()
    stats = orchestrator.get_encryption_stats(test_message)
    print(f"Stats: {stats}")
    
    verified = orchestrator.verify_integrity(test_message)
    print(f"Integrity verified: {verified}")
