/*  akas_codec.js  –  100 % vanilla JS, ES module
    Mirrors your Python files: WebP compression type = 2
*/

export function encodeAkas(frames, metadata = {}, isAnim = false, version = 1) {
  /* frames = [{w,h,dur,data:Uint8Array}]    data = raw WebP bytes */
  const metaBytes = new TextEncoder().encode(JSON.stringify(metadata));
  let size = 4 + 1 + 1 + 1 + 2 + 4 + metaBytes.length;           // header
  for (const f of frames) size += 2 + 2 + 2 + 4 + f.data.length; // per‑frame

  const buf = new ArrayBuffer(size);
  const dv  = new DataView(buf);
  let p = 0;

  // --- file header ----------------------------------------------------
  ['A', 'K', 'A', 'S'].forEach(c => dv.setUint8(p++, c.charCodeAt(0)));
  dv.setUint8(p++, version);
  dv.setUint8(p++, 2);                       // compression = 2 (WebP)
  dv.setUint8(p++, isAnim ? 1 : 0);
  dv.setUint16(p, frames.length, true); p += 2;
  dv.setUint32(p, metaBytes.length, true);  p += 4;
  new Uint8Array(buf, p, metaBytes.length).set(metaBytes); p += metaBytes.length;

  // --- frames ---------------------------------------------------------
  for (const f of frames) {
    dv.setUint16(p, f.w, true); p += 2;
    dv.setUint16(p, f.h, true); p += 2;
    dv.setUint16(p, f.dur ?? 1000, true); p += 2;
    dv.setUint32(p, f.data.length, true);   p += 4;
    new Uint8Array(buf, p, f.data.length).set(f.data); p += f.data.length;
  }
  return new Uint8Array(buf);
}

export function decodeAkas(arrayBuf) {
  const buf = arrayBuf instanceof Uint8Array ? arrayBuf : new Uint8Array(arrayBuf);
  const dv  = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  let p = 0;

  const magic = String.fromCharCode(...buf.slice(0, 4));
  if (magic !== 'AKAS') throw new Error('Not an AKAS file');
  p += 4;

  const version = dv.getUint8(p++);
  const comp    = dv.getUint8(p++);              // 2 = WebP
  const isAnim  = dv.getUint8(p++);
  const count   = dv.getUint16(p, true); p += 2;
  const metaLen = dv.getUint32(p, true); p += 4;
  const metaStr = new TextDecoder().decode(buf.slice(p, p + metaLen)); p += metaLen;
  const metadata = metaStr ? JSON.parse(metaStr) : {};

  const frames = [];
  for (let i = 0; i < count; i++) {
    const w   = dv.getUint16(p, true); p += 2;
    const h   = dv.getUint16(p, true); p += 2;
    const dur = dv.getUint16(p, true); p += 2;
    const len = dv.getUint32(p, true); p += 4;
    const data = buf.slice(p, p + len); p += len;
    frames.push({ w, h, dur, data, blob: new Blob([data], { type: 'image/webp' }) });
  }
  return { version, comp, isAnim: !!isAnim, metadata, frames };
}
