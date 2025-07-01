# akas_encoder.py
import os, json, struct, io
from PIL import Image, ImageSequence
import cv2

MAGIC = b'AKAS'
VERSION = 3
COMPRESSION_TYPE = 2  # 2 = in-memory WebP

def compress_frame_webp(img):
    buffer = io.BytesIO()
    img = img.convert("RGBA")
    img.save(buffer, format="WEBP", quality=85, lossless=False)
    return buffer.getvalue(), img.width, img.height

def encode_image(image_path, output_path, metadata=None):
    frames = []
    img = Image.open(image_path)
    is_animated = getattr(img, "is_animated", False)

    if is_animated:
        for frame in ImageSequence.Iterator(img):
            data, w, h = compress_frame_webp(frame)
            duration = frame.info.get("duration", 100)
            frames.append((w, h, duration, data))
    else:
        data, w, h = compress_frame_webp(img)
        frames.append((w, h, 0, data))

    _write_akas(output_path, frames, is_animated, metadata)

def encode_video(video_path, output_path, metadata=None):
    cap = cv2.VideoCapture(video_path)
    frames = []
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    duration = int(1000 / fps)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
        data, w, h = compress_frame_webp(img)
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

