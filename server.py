import os
import base64
import zlib
import json
import socket
import threading
import struct
from flask import Flask, request, jsonify
from chaotic_crypto import encrypt_with_chaos

app = Flask(__name__)

PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
PASS_FILE = os.path.join(PROJECT_DIR, "pass.txt")
PASS_ENV = "STEGO_PASS"
MAX_MESSAGE_SIZE = 50000
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

def get_passphrase() -> bytes:
    pw = os.environ.get(PASS_ENV)
    if pw:
        return pw.encode("utf-8")
    
    if os.path.exists(PASS_FILE):
        with open(PASS_FILE, "r", encoding="utf-8") as f:
            return f.read().strip().encode("utf-8")
    
    return b"default_passphrase"

def encrypt_message(plaintext: str, passphrase: bytes) -> str:
    if len(plaintext) > MAX_MESSAGE_SIZE:
        plaintext = plaintext[:MAX_MESSAGE_SIZE]
    
    compressed = zlib.compress(plaintext.encode("utf-8"))
    envelope = encrypt_with_chaos(compressed, passphrase)
    return base64.b64encode(envelope).decode("utf-8")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "Server is running"}), 200

@app.route('/encrypt', methods=['POST'])
def encrypt_endpoint():
    try:
        data = request.get_json()
        plaintext = data.get('message', '')
        
        if not plaintext:
            return jsonify({"error": "No message provided"}), 400
        
        passphrase = get_passphrase()
        encrypted = encrypt_message(plaintext, passphrase)
        
        return jsonify({
            "status": "success",
            "encrypted_message": encrypted,
            "size": len(encrypted)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/encrypt-batch', methods=['POST'])
def encrypt_batch():
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        passphrase = get_passphrase()
        encrypted_messages = []
        
        for msg in messages:
            encrypted = encrypt_message(msg, passphrase)
            encrypted_messages.append(encrypted)
        
        return jsonify({
            "status": "success",
            "encrypted_messages": encrypted_messages,
            "count": len(encrypted_messages)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/server-info', methods=['GET'])
def server_info():
    return jsonify({
        "server": "Steganography Server",
        "version": "1.0",
        "max_message_size": MAX_MESSAGE_SIZE,
        "endpoints": [
            "/health",
            "/encrypt",
            "/encrypt-batch",
            "/server-info"
        ]
    }), 200

def run_server(host=SERVER_HOST, port=SERVER_PORT, debug=False):
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    print(f"Starting Steganography Server on {SERVER_HOST}:{SERVER_PORT}")
    run_server()
