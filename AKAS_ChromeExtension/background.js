const MENU_ID = "save-as-akas";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: MENU_ID,
    title: "Save image as .akas",
    contexts: ["image"]
  });
});

async function ensureOffscreen() {
  if (await chrome.offscreen.hasDocument()) return;
  await chrome.offscreen.createDocument({
    url: chrome.runtime.getURL("offscreen.html"),
    reasons: ["DOM_SCRAPING", "BLOBS"],
    justification: "Convert image to AKAS"
  });
}

chrome.contextMenus.onClicked.addListener(async (info) => {
  if (info.menuItemId !== MENU_ID || !info.srcUrl) return;

  try {
    await ensureOffscreen();

    const res = await chrome.runtime.sendMessage({
      type: "CONVERT_URL_TO_AKAS",
      url: info.srcUrl
    });

    if (!res || !res.blobUrl) throw new Error("Conversion failed or no blob URL");

    const fileStem = (info.srcUrl.split(/[?#]/)[0].split('/').pop() || "image")
                     .replace(/\.[a-z0-9]+$/i, "");

    chrome.downloads.download({
      url: res.blobUrl,
      filename: fileStem + ".akas",
      saveAs: true
    }, id => {
      if (chrome.runtime.lastError) {
        console.error("[akas] Download failed:", chrome.runtime.lastError.message);
      } else {
        console.log("[akas] Downloaded:", id);
      }
    });

  } catch (err) {
    console.error("[akas] Error:", err);
  }
});
