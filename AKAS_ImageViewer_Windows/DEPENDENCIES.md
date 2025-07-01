# 📦 AKAS Viewer Suite – Dependency Guide

Generated: 2025-07-01

| Use‑case | File | Install Command |
|----------|------|-----------------|
| **Desktop Viewer / Converter** | `requirements.desktop.txt` | `pip install -r requirements.desktop.txt` |
| **Browser Polyfill** | `requirements.web.txt` | *(no `npm install` needed)* |

---

## 1️⃣ Desktop (`VraavViewer_2025.py`)

```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.desktop.txt
```

> **System prerequisites**
> * Windows: nothing extra (bundled Tk)
> * macOS: `brew install poppler`
> * Linux: `sudo apt install poppler-utils python3-tk`

---

## 2️⃣ Web (`akas-polyfill/`)

1. Download Pyodide **full web build** v0.25.1  
2. Extract into `akas-polyfill/pyodide/`
3. Add two script tags to your HTML:

```html
<script src="/akas-polyfill/pyodide/pyodide.js"></script>
<script type="module" src="/akas-polyfill/akas-autoload.js"></script>
```

No further build steps—just serve via `http://` and you’re done.

---
