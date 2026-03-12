/**
 * VoxStory Extension — popup.js
 * Handles the extension popup: open app, configure URL, open alongside platforms.
 */

const DEFAULT_URL = "https://huggingface.co/spaces/shehzadimahumagha/voxstory";

const PLATFORM_URLS = {
  zoom:  "https://app.zoom.us/wc",
  teams: "https://teams.microsoft.com",
  meet:  "https://meet.google.com",
  webex: "https://web.webex.com",
};

/** Load the configured VoxStory URL from storage. */
function getVoxStoryUrl() {
  return new Promise((resolve) => {
    chrome.storage.sync.get({ voxstoryUrl: DEFAULT_URL }, (items) => {
      resolve(items.voxstoryUrl || DEFAULT_URL);
    });
  });
}

/**
 * Open VoxStory in a side panel window.
 * Positions it on the right 40% of the available screen space.
 */
async function openVoxStory(platformUrl) {
  const url = await getVoxStoryUrl();

  const screenW = window.screen.availWidth;
  const screenH = window.screen.availHeight;
  const panelW  = Math.min(900, Math.round(screenW * 0.42));
  const panelLeft = screenW - panelW - 10;

  // If a platform URL is given, open it in the left portion first
  if (platformUrl) {
    const mainW = panelLeft - 10;
    chrome.windows.create({
      url:    platformUrl,
      type:   "normal",
      width:  mainW,
      height: screenH,
      left:   0,
      top:    0,
    });
  }

  // Open VoxStory on the right
  chrome.windows.create({
    url:    url,
    type:   "popup",
    width:  panelW,
    height: screenH,
    left:   panelLeft,
    top:    0,
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const url = await getVoxStoryUrl();

  // Display truncated URL
  const urlDisplay = document.getElementById("currentUrl");
  urlDisplay.textContent = url.replace(/^https?:\/\//, "");

  // Open main button
  document.getElementById("openMain").addEventListener("click", () => {
    openVoxStory(null);
    window.close();
  });

  // Settings link
  document.getElementById("openSettings").addEventListener("click", () => {
    chrome.runtime.openOptionsPage();
    window.close();
  });

  // Platform buttons
  document.querySelectorAll(".btn-platform").forEach((btn) => {
    btn.addEventListener("click", () => {
      const platform = btn.dataset.platform;
      const platformUrl = PLATFORM_URLS[platform];
      openVoxStory(platformUrl);
      window.close();
    });
  });
});
