import subprocess
import sys
import os
import time
from threading import Thread

PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"

def start_server():
    os.chdir(PROJECT_DIR)
    subprocess.run([sys.executable, "server.py"])

def run_client():
    time.sleep(3)
    os.chdir(PROJECT_DIR)
    subprocess.run([sys.executable, "client.py"])

def main():
    print("Starting Client-Server Pipeline with Video Steganography...\n")
    
    server_process = subprocess.Popen([sys.executable, os.path.join(PROJECT_DIR, "server.py")])
    
    time.sleep(3)
    
    os.chdir(PROJECT_DIR)
    subprocess.run([sys.executable, "client.py"])
    
    print("\nRunning video steganography pipeline...")
    subprocess.run([sys.executable, "pipeline.py"])
    
    time.sleep(1)
    server_process.terminate()
    server_process.wait()
    
    print("\nPipeline completed!")

if __name__ == "__main__":
    main()
