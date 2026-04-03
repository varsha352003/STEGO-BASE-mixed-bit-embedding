import subprocess
import os
import sys

PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
os.chdir(PROJECT_DIR)

steps = [
    ("Tier-0: Encrypt Payload (Chaotic Encryption)", "Encryption.py"),

    ("Tier-1: Frame Extraction + Watermarking", "extract_frames.py"),

    ("Tier-2: Semantic Uncertainty Analysis + Mask Generation", 
     "semantic_uncertainty_mask.py"),

    ("Tier-3: Semantic-Guided Payload Embedding", "embed_msg.py"),

    ("Tier-3: Semantic-Guided Payload Extraction", 
     "extract_modified_frames.py"),

    ("Tier-0: Decryption (Chaotic Decryption)", "Decryption.py")
]


def run_script(name, script):
    print(f"\n🔹 Running step: {name}")
    try:
        subprocess.run([sys.executable, script], check=True)
        print(f"✅ {name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running {script}")
        sys.exit(1)

def main():
    print("🚀 Starting Two-Tier Video Steganography Pipeline...\n")
    for name, script in steps:
        run_script(name, script)
    print("\n🎉 Pipeline completed successfully!")

if __name__ == "__main__":
    main()