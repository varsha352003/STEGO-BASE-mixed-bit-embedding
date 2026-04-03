import os
import subprocess
import sys
import shutil

PROJECT_DIR = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"

def clean_folders():
    folders_to_clean = [
        os.path.join(PROJECT_DIR, "output_frames"),
        os.path.join(PROJECT_DIR, "output_frames_with_message"),
        os.path.join(PROJECT_DIR, "uncertainty_debug")
    ]
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned: {folder}")

def run_script(script_name):
    script_path = os.path.join(PROJECT_DIR, script_name)
    if os.path.exists(script_path):
        print(f"\nRunning: {script_name}")
        subprocess.run([sys.executable, script_path], check=True)
    else:
        print(f"Warning: {script_name} not found")

def main():
    os.chdir(PROJECT_DIR)
    
    print("Starting integrated pipeline...")
    
    clean_folders()
    
    print("\nStep 1: Extract frames from video")
    run_script("extract_frames.py")
    
    print("\nStep 2: Generate semantic uncertainty mask")
    run_script("semantic_uncertainty_mask.py")
    
    print("\nStep 3: Embed encrypted message in frames")
    run_script("embed_msg.py")
    
    print("\nStep 4: Extract modified frames")
    run_script("extract_modified_frames.py")
    
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    main()
