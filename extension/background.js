/**
 * VoxStory Extension — background.js (Service Worker)
 * Handles installation events and keyboard shortcut commands.
 */

const DEFAULT_URL = "https://huggingface.co/spaces/shehzadimahumagha/voxstory";

chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    // Set default URL on first install
    chrome.storage.sync.set({ voxstoryUrl: DEFAULT_URL });

    // Open the options page so the user can configure their deployment URL
    chrome.runtime.openOptionsPage();
  }
});
