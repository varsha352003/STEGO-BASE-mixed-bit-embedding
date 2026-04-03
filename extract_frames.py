import cv2
import os
import numpy as np

def apply_dct_watermark(frame, alpha=0.02):
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = np.float32(y)
    h, w = y.shape

    for i in range(0, h - 8, 8):
        for j in range(0, w - 8, 8):
            block = y[i:i+8, j:j+8]
            dct = cv2.dct(block)
            dct[3, 4] *= (1 + alpha)
            dct[4, 3] *= (1 + alpha)
            y[i:i+8, j:j+8] = cv2.idct(dct)

    y = np.clip(y, 0, 255).astype(np.uint8)
    watermarked = cv2.merge([y, cr, cb])
    return cv2.cvtColor(watermarked, cv2.COLOR_YCrCb2BGR)

def extract_frames_from_video(video_path, output_folder, frame_interval=1):
    import shutil
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Error: Could not open video file.")
        return

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame = apply_dct_watermark(frame)
            frame_path = os.path.join(output_folder, f"frame_{saved_count:04d}.png")
            cv2.imwrite(frame_path, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"✅ {saved_count} watermarked frames extracted")

if __name__ == "__main__":
    video_path = r"C:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding\18127221-hd_1080_1920_30fps.mp4"
    output_folder = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding\output_frames"
    extract_frames_from_video(video_path, output_folder)