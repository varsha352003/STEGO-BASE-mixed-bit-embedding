import os
import cv2
import numpy as np
import struct
import json

# --------------------------------------------------
BASE = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
FRAMES_DIR = os.path.join(BASE, "output_frames_with_message")
MASK_DIR = os.path.join(BASE, "semantic_mask")
META_PATH = os.path.join(BASE, "embedding_meta.json")
OUT_FILE = os.path.join(BASE, "extracted_encrypted_message.txt")

CHANNEL = 0

# --------------------------------------------------
def bits_to_bytes(bits):
    data = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | b
        data.append(byte)
    return bytes(data)

# --------------------------------------------------
if __name__ == "__main__":
    print("🟢 Phase 3A: Payload Extraction")
    print("=" * 60)

    semantic_mask = np.load(os.path.join(MASK_DIR, "semantic_mask.npy"))

    with open(META_PATH, "r") as f:
        meta = json.load(f)

    bits_per_frame = meta["bits_per_frame"]

    frames = []
    frame_files = sorted(f for f in os.listdir(FRAMES_DIR) if f.endswith(".png"))
    for f in frame_files:
        frames.append(cv2.imread(os.path.join(FRAMES_DIR, f)))

    bits = []

    for idx, frame in enumerate(frames):
        if semantic_mask[idx] == 0:
            continue

        h, w, _ = frame.shape
        read = 0
        for i in range(h):
            for j in range(w):
                if read >= bits_per_frame:
                    break
                bits.append(frame[i, j, CHANNEL] & 1)
                read += 1

    header = bits_to_bytes(bits[:32])
    payload_len = struct.unpack(">I", header)[0]

    total_bits = (payload_len + 4) * 8
    payload_bits = bits[32:total_bits]
    payload_bytes = bits_to_bytes(payload_bits)

    with open(OUT_FILE, "wb") as f:
        f.write(payload_bytes)

    print(f"✅ Extracted payload size: {len(payload_bytes)} bytes")
    print("=" * 60)
