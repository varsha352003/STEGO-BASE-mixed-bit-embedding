import os
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms as T
import torchvision.models as models
import torch.nn.functional as F

BASE = r"c:\Users\Asus\Contacts\Desktop\capstone\STEGO-BASE-mixed-bit-embedding"
FRAMES_DIR = os.path.join(BASE, "output_frames")
DEBUG_DIR = os.path.join(BASE, "uncertainty_debug")

os.makedirs(DEBUG_DIR, exist_ok=True)


device = "cpu"

model = models.resnet18(pretrained=True)
model.eval()
model.to(device)


transform = T.Compose([
    T.ToPILImage(),
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


@torch.no_grad()
def compute_uncertainty(frame):
    """
    Returns scalar uncertainty value for a frame
    using softmax entropy.
    """
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    tensor = transform(img).unsqueeze(0).to(device)

    logits = model(tensor)
    probs = F.softmax(logits, dim=1)

    entropy = -torch.sum(probs * torch.log(probs + 1e-8), dim=1)
    return entropy.item()


def normalize(x):
    x = np.array(x)
    return (x - x.min()) / (x.max() - x.min() + 1e-8)


if __name__ == "__main__":
    print(" Phase 1: Semantic Uncertainty Analysis")
    print("=" * 60)

    frame_files = sorted([
        f for f in os.listdir(FRAMES_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

    if not frame_files:
        raise RuntimeError(" No frames found for uncertainty analysis")

    uncertainties = []

    for idx, fname in enumerate(frame_files):
        frame = cv2.imread(os.path.join(FRAMES_DIR, fname))
        if frame is None:
            continue

        u = compute_uncertainty(frame)
        uncertainties.append(u)

        print(f"[{idx:03d}] {fname} → uncertainty = {u:.4f}")

    uncertainties = normalize(uncertainties)

    
    plt.figure(figsize=(12, 4))
    plt.plot(uncertainties, color="red", linewidth=2)
    plt.title("Semantic Uncertainty Across Video Frames")
    plt.xlabel("Frame Index")
    plt.ylabel("Normalized Uncertainty")
    plt.grid(True)

    plot_path = os.path.join(DEBUG_DIR, "uncertainty_curve.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()

    
    np.save(os.path.join(DEBUG_DIR, "uncertainty_values.npy"), uncertainties)

    print("\n Uncertainty statistics:")
    print(f"   Min:  {uncertainties.min():.4f}")
    print(f"   Mean: {uncertainties.mean():.4f}")
    print(f"   Max:  {uncertainties.max():.4f}")

    print("\nPhase 1 complete")
    print(f"  Debug outputs saved to: {DEBUG_DIR}")
    print("=" * 60)
    

MASK_DIR = os.path.join(BASE, "semantic_mask")
os.makedirs(MASK_DIR, exist_ok=True)


tau = float(uncertainties.mean())


semantic_mask = (uncertainties >= tau).astype(np.uint8)


np.save(os.path.join(MASK_DIR, "semantic_mask.npy"), semantic_mask)


with open(os.path.join(MASK_DIR, "semantic_mask.txt"), "w") as f:
    for i, val in enumerate(semantic_mask):
        f.write(f"Frame {i:03d}: {'EMBED' if val else 'SKIP'}\n")


embed_count = int(semantic_mask.sum())
total_frames = len(semantic_mask)

print("\n Phase 2: Semantic Mask Generated")
print("=" * 60)
print(f"Total frames            : {total_frames}")
print(f"Embedding-enabled frames: {embed_count}")
print(f"Embedding ratio         : {embed_count / total_frames:.2f}")
print(f"Threshold (τ)           : {tau:.4f}")
print(f" Mask saved to         : {MASK_DIR}")
print("=" * 60)

