import os
import cv2
import numpy as np
import math
import struct
import json
import shutil


BASE = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
FRAMES_DIR = os.path.join(BASE, "output_frames")
OUT_DIR = os.path.join(BASE, "output_frames_with_message")
MASK_DIR = os.path.join(BASE, "semantic_mask")
UNCERTAINTY_PATH = os.path.join(BASE, "uncertainty_debug", "uncertainty_values.npy")
MSG_PATH = os.path.join(BASE, "encrypted_message.txt")
VIDEO_OUT = os.path.join(BASE, "output_video_with_message.mp4")
META_PATH = os.path.join(BASE, "embedding_meta.json")

if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(MASK_DIR, exist_ok=True)

CHANNEL = 0  

def bytes_to_bits(data: bytes):
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits


def rebuild_video(frames_dir, out_path, fps=30):
    files = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
    first = cv2.imread(os.path.join(frames_dir, files[0]))
    h, w, _ = first.shape

    out = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    for f in files:
        out.write(cv2.imread(os.path.join(frames_dir, f)))

    out.release()
    print(f"🎥 Video rebuilt → {out_path}")


if __name__ == "__main__":
    print("Phase 3A: Global Bitstream Video Embedding")
    print("=" * 60)

    with open(MSG_PATH, "rb") as f:
        payload = f.read()

    payload_len = len(payload)
    header = struct.pack(">I", payload_len)
    full_payload = header + payload

    bits = bytes_to_bits(full_payload)
    total_bits = len(bits)

    uncertainty = np.load(UNCERTAINTY_PATH)
    semantic_mask = uncertainty >= uncertainty.mean()
    eligible_frames = np.where(semantic_mask)[0]

    frame_files = sorted(f for f in os.listdir(FRAMES_DIR) if f.endswith(".png"))

    bits_per_frame = math.ceil(total_bits / len(eligible_frames))

    
    meta = {
        "payload_bits": total_bits,
        "bits_per_frame": bits_per_frame
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    bit_idx = 0
    frames_used = 0

    for idx, fname in enumerate(frame_files):
        frame = cv2.imread(os.path.join(FRAMES_DIR, fname))

        if semantic_mask[idx] and bit_idx < total_bits:
            written = 0
            h, w, _ = frame.shape
            for i in range(h):
                for j in range(w):
                    if bit_idx >= total_bits or written >= bits_per_frame:
                        break
                    frame[i, j, CHANNEL] = (frame[i, j, CHANNEL] & 0xFE) | bits[bit_idx]
                    bit_idx += 1
                    written += 1
            frames_used += 1
            print(f" Frame {idx:03d} → {written} bits")

        cv2.imwrite(os.path.join(OUT_DIR, f"frame_{idx:04d}.png"), frame)

    print(f"\n Bits embedded: {bit_idx}/{total_bits}")
    print(f" Frames used : {frames_used}")

    rebuild_video(OUT_DIR, VIDEO_OUT)

    print("=" * 60)
    print(" Phase 3A embedding COMPLETE")
