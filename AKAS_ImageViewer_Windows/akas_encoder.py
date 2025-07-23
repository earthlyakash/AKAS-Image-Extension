### --- akas_encoder.py (updated) ---
import os, json, struct, io
from PIL import Image, ImageSequence
import cv2

MAGIC = b'AKAS'
VERSION = 3
COMPRESSION_TYPE = 2  # 2 = in-memory WebP

def compress_frame_webp(img, quality):
    buffer = io.BytesIO()
    img = img.convert("RGBA")
    img.save(buffer, format="WEBP", quality=quality, lossless=False)
    return buffer.getvalue(), img.width, img.height

def encode_image(image_path, output_path, metadata=None, quality=85):
    frames = []
    img = Image.open(image_path)
    is_animated = getattr(img, "is_animated", False)

    if is_animated:
        for frame in ImageSequence.Iterator(img):
            data, w, h = compress_frame_webp(frame, quality)
            duration = frame.info.get("duration", 100)
            frames.append((w, h, duration, data))
    else:
        data, w, h = compress_frame_webp(img, quality)
        frames.append((w, h, 0, data))

    _write_akas(output_path, frames, is_animated, metadata)

def encode_video(video_path, output_path, metadata=None, quality=85):
    cap = cv2.VideoCapture(video_path)
    frames = []
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    duration = int(1000 / fps)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
        data, w, h = compress_frame_webp(img, quality)
        frames.append((w, h, duration, data))

    cap.release()
    _write_akas(output_path, frames, is_animated=True, metadata=metadata)

def _write_akas(path, frames, is_animated, metadata):
    meta_bytes = json.dumps(metadata or {}).encode('utf-8')

    with open(path, 'wb') as f:
        f.write(MAGIC)                                   # 4 bytes
        f.write(struct.pack('B', VERSION))               # 1 byte
        f.write(struct.pack('B', COMPRESSION_TYPE))      # 1 byte (2 for WebP)
        f.write(struct.pack('B', 1 if is_animated else 0))# 1 byte
        f.write(struct.pack('H', len(frames)))           # 2 bytes

        f.write(struct.pack('I', len(meta_bytes)))       # 4 bytes
        f.write(meta_bytes)                              # N bytes

        for w, h, dur, data in frames:
            f.write(struct.pack('H', w))                 # 2 bytes
            f.write(struct.pack('H', h))                 # 2 bytes
            f.write(struct.pack('H', dur))               # 2 bytes
            f.write(struct.pack('I', len(data)))         # 4 bytes
            f.write(data)                                # N bytes


### --- akas_converter.py (updated) ---
import os
import mimetypes
import tkinter as tk
from tkinter import filedialog, messagebox
from akas_encoder import encode_image, encode_video
from PIL import Image

def is_video_file(file_path):
    mime = mimetypes.guess_type(file_path)[0]
    return mime and mime.startswith("video")

def is_animated_gif(file_path):
    try:
        img = Image.open(file_path)
        return getattr(img, "is_animated", False)
    except:
        return False

def convert_file(file_path, output_dir, log_area, quality=8):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1].lower()

    metadata = {
        "creator": "Akash Kumar",
        "source_file": file_path
    }

    quality_mapped = int(quality * 10)

    try:
        if ext == ".gif" and is_animated_gif(file_path):
            output_file = os.path.join(output_dir, f"{file_name}_ani.akas")
            encode_image(file_path, output_file, metadata, quality=quality_mapped)
        elif is_video_file(file_path):
            output_file = os.path.join(output_dir, f"{file_name}_ani.akas")
            encode_video(file_path, output_file, metadata, quality=quality_mapped)
        else:
            output_file = os.path.join(output_dir, f"{file_name}.akas")
            encode_image(file_path, output_file, metadata, quality=quality_mapped)

        log_area.insert(tk.END, f"\u2705 Converted: {file_name}\n")
    except Exception as e:
        log_area.insert(tk.END, f"\u274C Failed: {file_name} — {e}\n")

def launch_gui():
    root = tk.Tk()
    root.title("\U0001F5BC\uFE0F AKAS Converter")

    tk.Label(root, text="AKAS Converter", font=("Arial", 16, "bold")).pack(pady=10)

    log_area = tk.Text(root, height=15, width=60, bg="#f9f9f9")
    log_area.pack(padx=10, pady=10)

    quality_var = tk.IntVar(value=8)
    tk.Label(root, text="Compression Quality (1–10):").pack()
    tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, variable=quality_var).pack()

    def handle_single():
        file_path = filedialog.askopenfilename(title="Select Image or Video")
        if not file_path:
            return
        output_dir = os.path.dirname(file_path)
        convert_file(file_path, output_dir, log_area, quality=quality_var.get())

    def handle_bulk():
        dir_path = filedialog.askdirectory(title="Select Folder")
        if not dir_path:
            return

        output_dir = dir_path.rstrip("/\\") + "_output"
        os.makedirs(output_dir, exist_ok=True)

        valid_exts = [
            ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".avif", ".gif",
            ".mp4", ".mov", ".avi", ".mkv"
        ]

        for file in os.listdir(dir_path):
            full_path = os.path.join(dir_path, file)
            if os.path.isfile(full_path) and os.path.splitext(file)[1].lower() in valid_exts:
                convert_file(full_path, output_dir, log_area, quality=quality_var.get())

        log_area.insert(tk.END, f"\n\u2705 All converted files saved to: {output_dir}\n")

    tk.Button(root, text="\U0001F4C4 Convert Single File", command=handle_single, width=30).pack(pady=5)
    tk.Button(root, text="\U0001F4C1 Convert Folder (Bulk)", command=handle_bulk, width=30).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
