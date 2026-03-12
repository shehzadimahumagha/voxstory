# VoxStory — Microsoft Teams Integration

Add VoxStory as a tab in any Teams channel, group chat, or personal app.

## Option A — Personal App (quickest, 2 min)

1. In Teams, click **Apps** (left sidebar) → **Manage your apps**
2. Click **Upload an app** → **Upload a custom app**
3. Upload `voxstory-teams.zip` (see below)
4. VoxStory appears in your personal app list

## Option B — Channel / Meeting Tab

1. Open a Teams channel or meeting chat
2. Click **+** next to the tab bar → **Website**
3. Paste your VoxStory URL: `https://huggingface.co/spaces/shehzadimahumagha/voxstory`
4. Name it **VoxStory** → Save

## Building the Teams App Package

```bash
# From this directory
zip voxstory-teams.zip manifest.json color.png outline.png
```

The `.zip` contains:
- `manifest.json` — app definition
- `color.png` — 192×192 colour icon (replace placeholder)
- `outline.png` — 32×32 transparent outline icon (replace placeholder)

## Customising the URL

If you have your own deployed instance, edit `manifest.json` and replace
`https://huggingface.co/spaces/shehzadimahumagha/voxstory` with your URL in `contentUrl` and `websiteUrl`.

Then re-zip and re-upload.
