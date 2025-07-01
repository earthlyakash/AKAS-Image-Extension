
# 🖼️ AKAS Image Polyfill

This project enables browser support for the custom `.akas` image format — including animated `.akas` files — using your original Python decoder running inside WebAssembly (via Pyodide).

---

## 🔧 What This Does

✅ View `.akas` files in `<img>` tags and CSS `background-image`  
✅ Supports **animated .akas** (multi-frame playback with durations)  
✅ 100% offline-compatible — no server needed after setup  
✅ Based on your **original `akas_decoder.py`** (pure Python)  
✅ Works on all modern browsers: Chrome, Edge, Firefox, Safari, Brave

---

## 📦 Folder Structure

```
project/
├─ test.html                    # Your test HTML file
├─ demo.akas                    # Sample AKAS image or animation
└─ akas-polyfill/
   ├─ akas-autoload.js          # This polyfill (JS)
   ├─ akas_decoder.py           # Your AKAS decoder in Python
   └─ pyodide/                  # Pyodide full web build (from pyodide.org)
       ├─ pyodide.js
       ├─ pyodide.asm.js
       ├─ pyodide.asm.wasm
       ├─ python_stdlib.zip
       └─ ...
```

---

## 🚀 Developer Use Case

### 🧩 "I want to show `.akas` images or banners on my website"

> ✅ You can simply use AKAS files like this:

```html
<script src="/akas-polyfill/pyodide/pyodide.js"></script>
<script type="module" src="/akas-polyfill/akas-autoload.js"></script>

<img src="/images/photo.akas" alt="Custom Image">
```

---

### 🖼 "I have a dynamic site or portfolio"

```html
<div class="hero"></div>

<style>
  .hero {
    width: 100%;
    height: 300px;
    background-image: url('/media/animated_banner.akas');
    background-size: cover;
    background-position: center;
  }
</style>
```

The polyfill will detect `.akas`, convert it to WebP, and play animated frames using `<canvas>`.

---

### ⚙️ How it works (under the hood)

1. JavaScript scans for `.akas` usage in `<img>` and CSS.
2. Loads `pyodide.js` and your `akas_decoder.py` into the browser.
3. Parses `.akas` format using **your own logic**.
4. Converts WebP frames and renders them — either replacing `<img>` with a Blob URL or `<canvas>` if animated.
5. Frame `duration` is respected for playback.

---

## 🌐 Hosting

Must be served via **http://** or **https://**

```bash
# Local dev test:
python -m http.server 8000
```

Then open:
[http://localhost:8000/test.html](http://localhost:8000/test.html)

---

## 💼 Real‑World Use Examples

| Project        | Use AKAS for                     |
|----------------|----------------------------------|
| 🖥️ Personal Portfolio | Animated banners in CSS background |
| 🛍️ E-Commerce Site    | Product previews with .akas animation |
| 📰 News Site          | Interactive headlines using `.akas` |
| 📸 Image Gallery      | Web-native display of `.akas` format |

---

## 📄 License

MIT License © 2025 Akash Kumar  
You may reuse, integrate, modify freely.

---

## 🤝 Contribute

Pull requests welcome — especially for:

- React/Vue/Angular wrappers
- Drag-and-drop AKAS preview component
- Optional fallback support for older browsers

Built with ❤️ using [Pyodide](https://pyodide.org) and your original AKAS logic.
