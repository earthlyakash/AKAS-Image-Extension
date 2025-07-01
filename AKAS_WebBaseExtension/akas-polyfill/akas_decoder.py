# Minimal version of your decode_akas without Pillow (for browser use)
import struct, json, io, base64

MAGIC = b'AKAS'
def decode_akas(data: bytes, save=False):
    f = memoryview(data)
    off=0
    if f[:4].tobytes()!=MAGIC: raise ValueError("Bad magic")
    off=4
    version = f[off]; off+=1
    comp    = f[off]; off+=1
    is_anim = f[off]; off+=1
    frame_cnt = struct.unpack_from('<H', f, off)[0]; off+=2
    meta_len  = struct.unpack_from('<I', f, off)[0]; off+=4
    meta_bytes= f[off:off+meta_len].tobytes(); off+=meta_len
    try:
        meta = json.loads(meta_bytes.decode()) if meta_len else {}
    except: meta={}
    frames=[]
    for _ in range(frame_cnt):
        w,h,dur = struct.unpack_from('<HHH', f, off); off+=6
        dlen = struct.unpack_from('<I', f, off)[0]; off+=4
        data = f[off:off+dlen].tobytes(); off+=dlen
        frames.append((data, dur))
    return meta, frames
