/* akas-autoload.js  v2.0  – renders *static and animated* .akas files
   Works fully offline using Pyodide + your original akas_decoder.py    */

//////////////////////////////////////////////////////////////////
// 1.  Load Pyodide once and register akas_decoder.py as a module
//////////////////////////////////////////////////////////////////
let pyReady = null;
async function getPy() {
  if (pyReady) return pyReady;
  pyReady = (async () => {
    const pyodide = await window.loadPyodide({
      indexURL: "./akas-polyfill/pyodide/",
    });

    /* write akas_decoder.py into Pyodide FS and import it */
    const pyCode = await (await fetch("./akas-polyfill/akas_decoder.py")).text();
    pyodide.FS.writeFile("akas_decoder.py", pyCode);
    await pyodide.runPython("import akas_decoder");

    return pyodide;
  })();
  return pyReady;
}

//////////////////////////////////////////////////////////////////
// 2.  Fetch, decode, and swap an element (IMG or CSS background)
//////////////////////////////////////////////////////////////////
async function decodeAndSwap(el, url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch: " + url);
    const bytes = new Uint8Array(await res.arrayBuffer());

    /* ---- run Python decoder ---- */
    const py = await getPy();
    py.globals.set("file_bytes", bytes);

    /* Python -> JSON list of frames [{data,b64},duration] */
    const framesJSON = py.runPython(`
import akas_decoder, json, base64
_, frames = akas_decoder.decode_akas(bytes(file_bytes), save=False)
json.dumps([
    {"data": base64.b64encode(fr[0]).decode("ascii"),
     "duration": int(fr[1]) or 100} for fr in frames])
`);
    const frames = JSON.parse(framesJSON);

    /* ---- decode every WebP frame to ImageBitmap ---- */
    const bitmaps = await Promise.all(
      frames.map((fr) => {
        const blob = new Blob(
          [Uint8Array.from(atob(fr.data), (c) => c.charCodeAt(0))],
          { type: "image/webp" }
        );
        return createImageBitmap(blob);
      })
    );

    ////////////////////////////////////////////////////////
    // 3.  Static image  → keep <img> / background
    ////////////////////////////////////////////////////////
    if (bitmaps.length === 1) {
      const blob = new Blob(
        [Uint8Array.from(atob(frames[0].data), (c) => c.charCodeAt(0))],
        { type: "image/webp" }
      );
      const objURL = URL.createObjectURL(blob);
      if (el.tagName === "IMG") el.src = objURL;
      else el.style.backgroundImage = `url("${objURL}")`;
      return;
    }

    ////////////////////////////////////////////////////////
    // 4.  Animated image → replace with <canvas> + loop
    ////////////////////////////////////////////////////////
    let canvas;
    if (el.tagName === "IMG") {
      canvas = document.createElement("canvas");
      canvas.width = bitmaps[0].width;
      canvas.height = bitmaps[0].height;
      el.replaceWith(canvas);
    } else {
      canvas = document.createElement("canvas");
      canvas.style.position = "absolute";
      canvas.style.top = canvas.style.left = "0";
      canvas.style.width = "100%";
      canvas.style.height = "100%";
      el.style.position = "relative";
      el.appendChild(canvas);
      canvas.width = bitmaps[0].width;
      canvas.height = bitmaps[0].height;
    }
    const ctx = canvas.getContext("2d");

    let idx = 0;
    (function draw() {
      ctx.drawImage(bitmaps[idx], 0, 0, canvas.width, canvas.height);
      const dur = frames[idx].duration || 100;
      idx = (idx + 1) % bitmaps.length;
      setTimeout(draw, dur);
    })();
  } catch (err) {
    console.error("AKAS polyfill failed", err);
  }
}

//////////////////////////////////////////////////////////////////
// 5.  Scan DOM & observe mutations
//////////////////////////////////////////////////////////////////
function scan() {
  /* <img src="*.akas"> */
  document.querySelectorAll("img[src$='.akas' i]").forEach((img) => {
    if (!img.dataset.akasDone) {
      img.dataset.akasDone = 1;
      decodeAndSwap(img, img.currentSrc || img.src);
    }
  });

  /* CSS background-image: url("*.akas") */
  document.querySelectorAll("[style*='.akas']").forEach((el) => {
    if (el.dataset.akasDone) return;
    const m = /url\\(["']?([^"')]+\\.akas)["']?\\)/i.exec(el.style.backgroundImage);
    if (m) {
      el.dataset.akasDone = 1;
      decodeAndSwap(el, m[1]);
    }
  });
}

new MutationObserver(scan).observe(document.documentElement, {
  childList: true,
  subtree: true,
});
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", scan);
} else {
  scan();
}
