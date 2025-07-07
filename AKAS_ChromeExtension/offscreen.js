import { encodeAkas } from './akas_codec.js';

chrome.runtime.onMessage.addListener((msg, _, sendResponse) => {
  if (msg.type !== 'CONVERT_URL_TO_AKAS') return;

  (async () => {
    try {
      const imgBlob = await fetch(msg.url).then(r => r.blob());
      const bitmap  = await createImageBitmap(imgBlob);

      const canvas = new OffscreenCanvas(bitmap.width, bitmap.height);
      const ctx = canvas.getContext('2d');
      ctx.drawImage(bitmap, 0, 0);

      const webpBlob  = await canvas.convertToBlob({ type: 'image/webp', quality: 0.92 });
      const webpBytes = new Uint8Array(await webpBlob.arrayBuffer());

      const akasBytes = encodeAkas([{ w: bitmap.width, h: bitmap.height, dur: 1000, data: webpBytes }]);

      const akasBlob = new Blob([akasBytes], { type: 'application/octet-stream' });
      const blobUrl  = URL.createObjectURL(akasBlob);

      sendResponse({ blobUrl });
    } catch (e) {
      console.error("[akas‑offscreen] Error:", e);
      sendResponse({ error: e.message });
    }
  })();

  return true;
});
