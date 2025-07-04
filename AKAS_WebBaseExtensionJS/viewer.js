/* viewer.js – uses akas_codec.js to preview .akas files */

import { decodeAkas } from './akas_codec.js';

export function previewAkas(blobOrUrl, targetEl) {
  const view = targetEl ?? document.createElement('img');
  const load = async () => {
    const arrayBuf = await (blobOrUrl instanceof Blob
      ? blobOrUrl.arrayBuffer()
      : fetch(blobOrUrl).then(r => r.arrayBuffer()));

    const { frames, isAnim } = decodeAkas(arrayBuf);

    if (!isAnim) {
      view.src = URL.createObjectURL(frames[0].blob);
    } else {
      /* basic canvas animator (loops frames) */
      const canvas = document.createElement('canvas');
      const ctx    = canvas.getContext('2d');
      canvas.width  = frames[0].w;
      canvas.height = frames[0].h;
      view.replaceWith(canvas);

      const imgs = frames.map(f => {
        const img = new Image();
        img.src = URL.createObjectURL(f.blob);
        return { img, dur: f.dur };
      });
      let i = 0, t0 = performance.now();
      const loop = now => {
        if (now - t0 >= imgs[i].dur) { i = (i + 1) % imgs.length; t0 = now; }
        ctx.drawImage(imgs[i].img, 0, 0);
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
      return canvas;
    }
    return view;
  };
  return load();
}
