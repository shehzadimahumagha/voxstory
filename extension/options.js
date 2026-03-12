/**
 * VoxStory Extension — options.js
 * Saves and loads the configured VoxStory deployment URL.
 */

const DEFAULT_URL = "https://voxstory.streamlit.app";

document.addEventListener("DOMContentLoaded", () => {
  const input  = document.getElementById("urlInput");
  const btn    = document.getElementById("saveBtn");
  const status = document.getElementById("statusMsg");

  // Load saved URL
  chrome.storage.sync.get({ voxstoryUrl: DEFAULT_URL }, (items) => {
    input.value = items.voxstoryUrl || DEFAULT_URL;
  });

  btn.addEventListener("click", () => {
    const url = input.value.trim();
    if (!url || !url.startsWith("http")) {
      status.style.color = "#E67700";
      status.textContent = "Please enter a valid URL starting with http(s)://";
      return;
    }
    chrome.storage.sync.set({ voxstoryUrl: url }, () => {
      status.style.color = "#00875A";
      status.textContent = "Settings saved.";
      setTimeout(() => { status.textContent = ""; }, 2500);
    });
  });
});
