---
title: VoxStory
emoji: 📋
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.41.0"
app_file: app.py
pinned: false
---

# VoxStory

**AI-powered Business Analyst Agent — from meeting chaos to Jira-ready artifacts in seconds.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C?logo=chainlink&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F55036)](https://console.groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-0052CC)](LICENSE)

---

VoxStory transforms messy stakeholder meeting inputs into production-ready Agile artifacts — with real BA methodology built in, not just summarization. It thinks like a senior Business Analyst: applying INVEST criteria, writing Gherkin acceptance criteria, detecting jargon, flagging open questions, and now synthesizing multi-stakeholder perspectives into a single unified story.

Built as a portfolio project by a Business Analyst who wanted AI tooling that actually understands BA work.

---

## Five Modes

| Mode | Input | Output |
|---|---|---|
| **Transcript Mode** | Raw meeting notes or Zoom transcript | User stories with AC, priority, stakeholder map |
| **Refinement Mode** | Vague or incomplete user story | INVEST assessment + polished story + change log |
| **Technical Story Mode** | Architecture notes, API specs, system design | Implementation-ready stories with API contracts + data requirements |
| **Solution Map** | One or more user stories | Component breakdown, API design, data model, phased roadmap, risk register |
| **Collaboration Board** | Multi-stakeholder perspectives (async or live) | Perspective alignment table + ONE unified story + solution overview |

---

## What Makes It Different

Most AI tools summarize. VoxStory applies BA methodology:

- **INVEST criteria** applied to every story — Independent, Negotiable, Valuable, Estimable, Small, Testable
- **Gherkin acceptance criteria** — happy path + edge cases, always
- **Business language enforcement** — API, database, endpoint automatically rewritten into plain business language
- **Business Value statements** — every story tied to a business outcome, not just a feature
- **Non-functional requirements** — auto-detected from context
- **Open questions and assumptions** flagged before development starts
- **Collaboration Board** — async multi-stakeholder input synthesized into one story (no more conflicting requirements)
- **GitHub integration** — connect any repo for code-aware artifact generation
- **Dual export** — `.docx` for Confluence, `.json` for Jira import

---

## Quick Start

### Option 1 — Use the deployed app (no setup)

Visit the live app, enter your free [Groq API key](https://console.groq.com), and start generating.

> Groq is free. No credit card required. Get a key at [console.groq.com](https://console.groq.com) in under 60 seconds.

### Option 2 — Self-host

```bash
# 1. Clone
git clone https://github.com/smagha2/voxstory.git
cd voxstory

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and set: GROQ_API_KEY=your_key_here
# Free key at: https://console.groq.com

# 5. Run
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Deploy to Streamlit Cloud (Free, Public)

1. Fork this repo on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your fork → set main file: `app.py`
4. Under **Advanced settings** → **Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_groq_key_here"
   ```
5. Click **Deploy** — your public URL is ready in ~2 minutes

---

## Browser Extension (Chrome / Edge)

Use VoxStory as a side panel alongside any web-based meeting tool — Zoom, Microsoft Teams, Google Meet, or Webex.

### Install

1. Download or clone this repo
2. Open Chrome → `chrome://extensions/`
3. Enable **Developer mode** (top-right toggle)
4. Click **Load unpacked** → select the `extension/` folder
5. The VoxStory icon appears in your toolbar

### Generate icons first

```bash
cd extension
python create_icons.py
```

### Usage

- Click the VoxStory toolbar icon
- Click **Open alongside your meeting** for any platform → VoxStory opens as a side panel on the right
- Paste meeting notes from the left window into VoxStory on the right

### Configure your deployment URL

Click **Configure** in the popup to point the extension at your own deployed instance.

---

## Microsoft Teams Integration

Add VoxStory as a tab in any Teams channel, meeting, or personal workspace.

### Quickest method — Website Tab

1. Open a Teams channel → click **+** next to tabs
2. Choose **Website**
3. Enter URL: `https://voxstory.streamlit.app`
4. Name it **VoxStory** → Save

### Full Teams App (with personal app support)

See [`teams-app/README.md`](teams-app/README.md) for packaging and sideloading instructions.

---

## Project Structure

```
voxstory/
├── app.py                         ← Streamlit UI (5 tabs)
├── agent/
│   ├── chain.py                   ← LangChain LCEL chains
│   ├── prompts.py                 ← BA-specific system prompts (5 modes)
│   └── github_tools.py            ← GitHub API integration
├── exporters/
│   ├── docx_exporter.py           ← Word document generation
│   └── json_exporter.py           ← Jira-compatible JSON export
├── extension/                     ← Chrome / Edge browser extension
│   ├── manifest.json
│   ├── popup.html / popup.js
│   ├── options.html / options.js
│   ├── background.js
│   └── icons/
├── teams-app/                     ← Microsoft Teams app manifest
│   ├── manifest.json
│   └── README.md
├── tests/
│   ├── test_chain.py
│   └── test_exporters.py
├── .streamlit/
│   └── config.toml                ← Streamlit production config
├── requirements.txt
├── LICENSE
└── .env.example
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| LLM | Groq + llama-3.3-70b-versatile | Ultra-fast inference, free tier available |
| Agent Framework | LangChain LCEL | Composable chains, easy to swap models |
| UI | Streamlit | Rapid iteration, clean deployment |
| Word Export | python-docx | Native .docx for Confluence upload |
| GitHub Integration | PyGitHub | Code-aware artifact generation |
| Tests | pytest + pytest-mock | CI-ready |
| Browser Extension | Chrome MV3 | Side-panel experience alongside meeting tools |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq inference API key — free at [console.groq.com](https://console.groq.com) |
| `GITHUB_TOKEN` | Optional | GitHub PAT for repo integration (Contents + Issues read) |

---

## Switching LLM Provider

The LLM is isolated to `agent/chain.py`. To switch to OpenAI:

```python
# In agent/chain.py — replace ChatGroq with:
from langchain_openai import ChatOpenAI

def get_llm():
    return ChatOpenAI(model="gpt-4o", temperature=0.3)
```

Add `OPENAI_API_KEY` to `.env`. No other changes needed.

---

## Contributing

Pull requests are welcome. Please:
1. Fork the repo and create a feature branch
2. Follow the existing code style (no emojis in UI, INVEST methodology, Jira aesthetic)
3. Add tests for any new chain functions
4. Update `README.md` if adding new capabilities

---

## Author

**Shehzadi Mahum Agha** — AI - Business Analyst
M.S. Business Analytics, University of Illinois Urbana-Champaign

[GitHub](https://github.com/smagha2) · [LinkedIn](https://www.linkedin.com/in/mahumagha/)

---

## License

[MIT](LICENSE) — free to use, fork, and build on.
