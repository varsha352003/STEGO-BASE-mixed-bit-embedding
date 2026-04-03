
import hashlib
import hmac
import struct
import math
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes


class ChaoticKeyGenerator:
   
    
    def __init__(self, passphrase: bytes, salt: bytes, iterations: int = 1000):
        
        self.iterations = iterations
        self.salt = salt
        
        
        key_material = scrypt(passphrase, salt, key_len=64, N=1<<14, r=8, p=1)
       
        self.x0 = self._bytes_to_float(key_material[0:8], 0.1, 0.9)
        self.r = self._bytes_to_float(key_material[8:16], 3.7, 3.99)
        
        self.hx0 = self._bytes_to_float(key_material[16:24], -0.3, 0.3)
        self.hy0 = self._bytes_to_float(key_material[24:32], -0.3, 0.3)
        self.a = self._bytes_to_float(key_material[32:40], 1.35, 1.45)
        self.b = self._bytes_to_float(key_material[40:48], 0.25, 0.35)
        
        
        self.chaotic_iv = self._generate_iv()
    
    def _bytes_to_float(self, data: bytes, min_val: float, max_val: float) -> float:
        
        int_val = int.from_bytes(data, byteorder='big')
        normalized = int_val / (2**(len(data) * 8) - 1)
        return min_val + normalized * (max_val - min_val)
    
    def _logistic_map(self, x: float) -> float:
        
        if not math.isfinite(x) or abs(x) > 1e10:
            x = 0.5
        result = self.r * x * (1 - x)
        if not math.isfinite(result):
            result = 0.5
        return max(0.0, min(1.0, result))
    
    def _henon_map(self, x: float, y: float) -> tuple:
       
        if not math.isfinite(x) or not math.isfinite(y):
            return 0.1, 0.1
        if abs(x) > 1e10 or abs(y) > 1e10:
            return 0.1, 0.1
        
        x_next = 1 - self.a * x * x + y
        y_next = self.b * x
        
        if not math.isfinite(x_next) or abs(x_next) > 10:
            x_next = 0.1
        if not math.isfinite(y_next) or abs(y_next) > 10:
            y_next = 0.1
        
        x_next = max(-2.0, min(2.0, x_next))
        y_next = max(-2.0, min(2.0, y_next))
        
        return x_next, y_next
    
    def _chaotic_byte(self, x: float, y: float) -> int:
       
        if not math.isfinite(x):
            x = 0.5
        if not math.isfinite(y):
            y = 0.5
        
        x_abs = abs(x) % 10.0
        y_abs = abs(y) % 10.0
        mixed = (x_abs + y_abs) / 2.0
        frac = mixed - int(mixed)
        byte_val = int(abs(frac) * 256) % 256
        return byte_val
    
    def _generate_iv(self) -> bytes:
      
        x, hx, hy = self.x0, self.hx0, self.hy0
        iv_bytes = []
        
        for i in range(16):
            x = self._logistic_map(x)
            hx, hy = self._henon_map(hx, hy)
            
            if i % 4 == 0:
                if not math.isfinite(x):
                    x = 0.5
                if not math.isfinite(hx) or not math.isfinite(hy):
                    hx, hy = 0.1, 0.1
            
            iv_bytes.append(self._chaotic_byte(x, hx))
        
        return bytes(iv_bytes)
    
    def generate_keystream(self, length: int) -> bytes:
        
        keystream = []
        x, hx, hy = self.x0, self.hx0, self.hy0
        
        for _ in range(16):
            x = self._logistic_map(x)
            hx, hy = self._henon_map(hx, hy)
        
        for i in range(length):
            x = self._logistic_map(x)
            hx, hy = self._henon_map(hx, hy)
            
            if (i + 1) % 256 == 0:
                if abs(x) < 0.01 or abs(x - 1.0) < 0.01:
                    x = (x + 0.1) % 1.0
                if abs(hx) < 0.01:
                    hx = (hx + 0.1) % 1.0
                
                if not math.isfinite(x):
                    x = 0.5
                if not math.isfinite(hx) or not math.isfinite(hy):
                    hx, hy = 0.1, 0.1
            
            keystream.append(self._chaotic_byte(x, hx))
        
        return bytes(keystream)


def encrypt_with_chaos(plaintext: bytes, passphrase: bytes) -> bytes:
    
    salt = get_random_bytes(16)
    iterations = 1000
    keygen = ChaoticKeyGenerator(passphrase, salt, iterations)
    keystream = keygen.generate_keystream(len(plaintext))
    ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream))
    hmac_key = scrypt(passphrase, salt, key_len=32, N=1<<14, r=8, p=1)
    mac = hmac.new(hmac_key, ciphertext, hashlib.sha256).digest()
    envelope = b'\x04' + struct.pack('>H', iterations) + salt + keygen.chaotic_iv + mac + ciphertext
    return envelope


def decrypt_with_chaos(envelope: bytes, passphrase: bytes) -> bytes:
    
    if not envelope or envelope[0] != 0x04:
        raise ValueError("Invalid envelope version (expected 0x04 for chaotic)")
    
    iterations = struct.unpack('>H', envelope[1:3])[0]
    salt = envelope[3:19]
    chaotic_iv = envelope[19:35]
    mac = envelope[35:67]
    ciphertext = envelope[67:]
    
    keygen = ChaoticKeyGenerator(passphrase, salt, iterations)
    
    if keygen.chaotic_iv != chaotic_iv:
        raise ValueError("Passphrase verification failed (IV mismatch)")
    
    hmac_key = scrypt(passphrase, salt, key_len=32, N=1<<14, r=8, p=1)
    expected_mac = hmac.new(hmac_key, ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac):
        raise ValueError("HMAC verification failed - data may be corrupted")
    
    keystream = keygen.generate_keystream(len(ciphertext))
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, keystream))
    return plaintext


def get_envelope_info(envelope: bytes) -> dict:
    
    if not envelope or envelope[0] != 0x04:
        return {"error": "Invalid or unsupported envelope"}
    
    iterations = struct.unpack('>H', envelope[1:3])[0]
    salt = envelope[3:19]
    iv = envelope[19:35]
    
    return {
        "version": 4,
        "algorithm": "Chaotic (Logistic + Henon)",
        "iterations": iterations,
        "salt_hex": salt.hex(),
        "iv_hex": iv.hex(),
        "total_size": len(envelope)
    }