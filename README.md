# 📦 `.akas` — Advanced Keyframe Animation Sprite (AKAS) Image Format

The **AKAS** file extension (`.akas`) is a lightweight, Web‑first container for static images **and** short animations.  
It combines the compression power with a simple header that stores metadata and multiple frames, making it perfect for web apps, games, and real‑time previews.

---

## 🌟 Why AKAS?

| Feature | Benefit |
|---------|---------|
| **Single container** | Bundle any number of WebP frames + JSON metadata in one file |
| **Tiny header (14 B + JSON)** | Zero parsing overhead, ideal for streaming |
| **Web‑native payload** | Frames stay as raw WebP → browsers decode them natively |
| **Open spec & MIT code** | Easy to port, fork, and embed in any language |
| **Future‑proof** | Designed to extend with new compression types |

---

## 🔧 File Format Specification

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0      | 4    | `AKAS` | Magic bytes |
| 4      | 1    | Version | Currently `1` |
| 5      | 1    | Compression | `2` = WebP |
| 6      | 1    | `isAnim` | `1` = multi‑frame, `0` = single |
| 7      | 2LE  | Frame count | Up to 65535 |
| 9      | 4LE  | Metadata length | UTF‑8 JSON size |
| 13     | *    | Metadata JSON | e.g. `{ "author":"..." }` |
| …      | *    | Frames | For each frame:<br>`w,h,dur,len,data` |

Frame block layout:

| Field | Type | Notes |
|-------|------|-------|
| `w`   | `uint16` LE | Width  |
| `h`   | `uint16` LE | Height |
| `dur` | `uint16` LE | Duration (ms, `0` = static) |
| `len` | `uint32` LE | Byte length of WebP payload |
| `data`| `[len]`     | Raw WebP bytes |

---

## 👩‍💻 Developer Integration

### ➡️ Python – Web API Example

```python
from flask import Flask, send_file, request
from akas_encoder import encode_akas   # your original Python script
from PIL import Image
import io, json

app = Flask(__name__)

@app.post('/encode')
def encode():
    img = Image.open(request.files['file'])
    meta = json.loads(request.form.get('meta', '{}'))
    akas_bytes = encode_akas([img], metadata=meta)
    return send_file(
        io.BytesIO(akas_bytes),
        mimetype='application/akas',
        download_name='output.akas'
    )

if __name__ == '__main__':
    app.run()
```

### ➡️ JavaScript – Web API Example

```js
import { AkasEncoder, AkasDecoder } from './akasCodec.js';

// Encode <input type="file">
const file = document.querySelector('input').files[0];
const bmp  = await createImageBitmap(file);
const blob = await AkasEncoder.encode([{ bitmap: bmp }], { author: 'You' });

// Decode
const arrayBuf = await blob.arrayBuffer();
const { metadata, frames } = AkasDecoder.decode(arrayBuf);
```

---

## 🌐 Browser Support

| Browser | Version |
|---------|---------|
| Chrome / Edge | 91+ |
| Firefox | 89+ |
| Safari | 14+ |
| Mobile (Chrome, Firefox) | Yes |

*Decoding uses the built‑in WebP codec; animation playback is `<canvas>` re‑draw.*

---

## 🪟 Windows Utilities

| Tool | Status | Description |
|------|--------|-------------|
| **AKAS Viewer** | ✅ Release v1.0 | Double‑click viewer with drag‑n‑drop |
|download link : https://drive.google.com/file/d/1FsRfFogTr_npraXKV7aRqASSOu8f7WPf/view?usp=sharing |
| **AKAS Converter** | ✅ Release v1.0 | Batch convert PNG/JPG ⇢ AKAS |
|download link : https://drive.google.com/file/d/1ZlAgU_SLqCZ78pfHvKT9aAoemTEVdiqG/view?usp=sharing |


---

## 🚧 Roadmap for Future support

- [ ] **Universal editor** (web & desktop) with layers and timeline  
- [ ] Lossless compression mode (AVIF / PNG)  
- [ ] HDR & alpha‑depth extensions  
- [ ] Plug‑in for popular image editors (Photopea, GIMP)

---


Please keep code **ES Module compliant** and write unit tests.

---

## 📄 License Free

Free © 2025 — Built on the original `.akas` format by **[Your Name]**

---

## 📬 Contact

- GitHub Issues: <https://github.com/earthlyakash>  
- Email: `earthlyakash@gmail.com`
