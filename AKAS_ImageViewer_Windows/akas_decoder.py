# akas_decoder.py (fixed)
import struct, json, io
from PIL import Image

MAGIC = b'AKAS'

def decode_akas(file_path, save=True):
    with open(file_path, 'rb') as f:
        if f.read(4) != MAGIC:
            print("❌ Not a valid .akas file.")
            return None

        version = struct.unpack('B', f.read(1))[0]
        compression_type = struct.unpack('B', f.read(1))[0]
        is_anim = struct.unpack('B', f.read(1))[0]
        frame_count = struct.unpack('H', f.read(2))[0]

        meta_len = struct.unpack('I', f.read(4))[0]
        meta_bytes = f.read(meta_len)

        try:
            metadata = json.loads(meta_bytes.decode('utf-8'))
        except Exception as e:
            print("❌ Metadata decode error:", e)
            return None


        print("Metadata:", metadata)
        print("Animated:", bool(is_anim))
        print("Frames:", frame_count)

        frames = []

        for i in range(frame_count):
            w = struct.unpack('H', f.read(2))[0]
            h = struct.unpack('H', f.read(2))[0]
            dur = struct.unpack('H', f.read(2))[0]
            data_len = struct.unpack('I', f.read(4))[0]
            data = f.read(data_len)

            if compression_type == 2:  # WebP
                try:
                    img = Image.open(io.BytesIO(data)).convert("RGBA")
                except Exception as e:
                    print(f"❌ Failed to decode frame {i+1}: {e}")
                    continue
            else:
                print("❌ Unsupported compression type.")
                return None

            if save:
                img.save(f"akas_frame_{i+1}.png")
            frames.append((img, dur))

        return metadata, frames
