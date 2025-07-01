
# 🌟 AKAS Viewer Suite

**Author:** **Akash Kumar**  
**Last update:** 2025-07-01

A two‑part toolkit that lets anyone **view, edit, convert, and embed `.akas` images** — online and offline.

| Component | What it is | Platforms |
|-----------|------------|-----------|
| **AKAS Image Viewer** (`VraavViewer_2025.py`) | Full‑featured desktop viewer & editor | Windows / macOS / Linux (Python 3.9+) |
| **AKAS Web Polyfill** (`akas‑polyfill/`) | JavaScript + Pyodide auto‑loader so `<img src="*.akas">` works in any browser | Chrome, Edge, Firefox, Safari, Brave |

---

## 🚀 Quick Start

### Desktop

```bash
git clone https://github.com/your-handle/akas-viewer-suite.git
cd akas-viewer-suite
python -m venv venv && source venv/bin/activate  # optional
pip install -r requirements.txt
python VraavViewer_2025.py [optional_image.akas]
```

*Double‑click the window, drag folders, or use **File ▸ Open**.*

### Web

```html
<!-- 1. Copy akas-polyfill/ folder to your site -->
<script src="/akas-polyfill/pyodide/pyodide.js"></script>
<script type="module" src="/akas-polyfill/akas-autoload.js"></script>

<!-- 2. Use .akas like PNG -->
<img src="/images/photo.akas" alt="Custom Image">
```

Serve via `http://` / `https://` or tiny dev server:

```bash
python -m http.server 8000
```

---

## ✨ AKAS Viewer Highlights

* **30+ formats**: PNG, JPG, WebP, PSD, PDF pages, and **.akas**
* **Animated .akas** playback with frame timing
* **Real‑time tools**: crop, rotate, flip, resize, draw, text, filters
* **Dark / Light / Fullscreen** toggle
* **AKAS Converter** built‑in (single & bulk)
* **Metadata‑aware** — displays size, frame count, file size
* **Recycle‑Bin delete** (safe) + Windows property dialog
* **Keyboard** shortcuts: ← → ↑ ↓ Delete, etc.
* **PDF navigation** (page‑by‑page)

---

## 🌐 Web Polyfill Highlights

* Auto‑detects `<img>` & CSS `url("*.akas")`
* Runs **your Python decoder** in WebAssembly via Pyodide
* Plays multi‑frame .akas on `<canvas>` with per‑frame durations
* Zero dependencies beyond the **Pyodide web build**
* Works offline once files are served (no CDN required)

---

## 🛠️ Developer API

### Python encode

```python
from akas_encoder import encode_image
encode_image("logo.png", "logo.akas", {"creator":"Akash"})
```

### C++ decode

```cpp
#include "akas_codec.h"
std::vector<AKASFrame> frames;
DecodeAKAS("demo.akas", frames);
```

### JavaScript (browser)

```js
import { decodeAkas } from '/akas-polyfill/akas_decoder.js';
const arrayBuf = await fetch('photo.akas').then(r=>r.arrayBuffer());
const { frames } = decodeAkas(new Uint8Array(arrayBuf));
```

---

## 📂 Repo Contents

```
VraavViewer_2025.py      # Desktop GUI viewer/editor
akas_encoder.py          # Reference encoder
akas_decoder.py          # Reference decoder
akas_converter.py        # CLI + GUI converter
akas-polyfill/
   ├─ akas-autoload.js   # Browser auto-loader
   ├─ akas_decoder.py    # Decoder for Pyodide
   └─ pyodide/           # WebAssembly runtime
demo.akas                # Sample animated file
test.html                # One‑page web demo
README.md                # (this file)
```

---

## 💼 Real‑World Use Examples

| Project        | Why AKAS?                              | Example |
|----------------|----------------------------------------|---------|
| 🖥️ Portfolio   | Lightweight animated artwork           | `<img src="cover.akas">` |
| 🛍️ E‑commerce  | 360° product spins with alpha          | `.hero { background:url('shoe.akas') }` |
| 📰 News Site   | Inline motion graphics without video   | `<img src="chart.akas">` |
| 📸 Photo Hub   | Hybrid still+motion galleries          | Grid of .akas thumbnails |

---

## 🗺️ Roadmap

- [ ] AVIF compression option  
- [ ] Photoshop **Save as AKAS** plug‑in  
- [ ] Electron one‑click desktop installer  
- [ ] Publish `akas-polyfill` on NPM  

---

## 📝 License

MIT License © 2025 **Akash Kumar**

> Use it, fork it, embed it — just keep the credits.

Built with ❤️ and WebAssembly.
