<p align="center">
  <img src="https://img.shields.io/badge/⬡%20FISSURE-Probe%20AI%20Safety%20Boundaries-8B5CF6?style=for-the-badge" alt="Fissure">
</p>

> **The adversarial AI testing harness that doesn't pretend a Python loop can outthink you.**
> **An AI security research harness. Built single-shot by an AI agent using qwen3.6-plus and Telegram. No laptop. No IDE. No VS Code. No copilot. No "let me set up my dev environment first." Just a VPS, Terminal, and unapologetic stubbornness.**

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/status-production%20ready-2ea44f?style=flat-square" alt="Status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://github.com/m4xx101/fissure"><img src="https://img.shields.io/badge/PRs-very%20welcome-ff69b4?style=flat-square" alt="PRs"></a>
  <a href="https://github.com/m4xx101/fissure/actions"><img src="https://img.shields.io/badge/token%20cost-minimal-success?style=flat-square" alt="Token Cost"></a>
</p>

# ⬡ FISSURE

> **Find the cracks in AI safety boundaries.**
> Fissure is an autonomous adversarial testing harness for Hermes Agent. The agent IS the orchestrator — no Python loop eating your context window, just 40+ techniques, 5 encoding levels, and cross-session learning that compounds.

---

## 📋 Table of Contents

<!-- TOC -->
- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Linux / macOS](#linux--macos)
  - [Windows (WSL2)](#windows-wsl2-recommended)
  - [Windows (PowerShell)](#windows-powershell)
  - [Termux / Android](#termux--android)
  - [Manual Install](#manual-install)
- [Updating](#-updating)
  - [Re-run Installer](#re-run-the-installer)
  - [Update Command](#update-command)
  - [Auto-Update via Cron](#auto-update-via-cronjob)
- [Usage Guide](#-usage-guide)
  - [Quick Demo](#quick-demo)
  - [Commands Reference](#commands-reference)
  - [Target Types](#target-types)
  - [Browser Mode](#browser-mode)
  - [API Mode](#api-mode)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
  - [WSL Issues](#wsl-issues)
  - [Install Issues](#install-issues)
  - [Runtime Issues](#runtime-issues)
- [Contributing](#-contributing)
- [FAQ](#-faq)

---

## 🚀 Quick Start

```bash
# Install (Linux/macOS/WSL)
curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash

# Tell your Hermes agent:
#   "🔥 Fissure — test gandalf.lakera.ai/baseline"
```

That's it. The agent reads the SKILL.md, probes the target, adapts techniques, and reports results.

---

## 📦 Installation

### Linux / macOS

**One-liner:**
```bash
curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash
```

**Or download + run:**
```bash
curl -LO https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh
chmod +x install-fissure.sh
./install-fissure.sh
```

**What it does:**
- Clones the repo to `~/.hermes/skills/red-teaming/fissure/`
- Creates the session wiki at `~/.hermes/wiki/fissure/`
- Installs Python dependencies (stdlib-only, no heavy deps)
- Detects optional tools (ollama, godmode skill)

**Re-run to update:** The installer detects existing installs and auto-updates.

### Windows (WSL2 — recommended)

**Prerequisites:**
1. [Install WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) with Ubuntu
2. Open WSL terminal

```bash
# Inside WSL:
curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash
```

> **WSL note:** If you see git errors (file locking, permission issues), run:
> ```bash
> cd ~/.hermes/skills/red-teaming/fissure
> git config core.filemode false
> git config core.autocrlf false
> ```

### Windows (PowerShell)

```powershell
iwr -Uri https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.ps1 -UseBasicParsing | iex
```

The PowerShell installer auto-detects WSL and delegates to the bash installer if available. On native Windows, it installs to `%USERPROFILE%\.hermes\skills\red-teaming\fissure`.

### Termux / Android

```bash
pkg install git python3 curl
curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash
```

### Manual Install

```bash
git clone https://github.com/m4xx101/fissure.git ~/.hermes/skills/red-teaming/fissure
cd ~/.hermes/skills/red-teaming/fissure
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 2>/dev/null || true
python3 scripts/wiki.py bootstrap
```

---

## 🔄 Updating

### Re-run the installer

The easiest way — just run the same install command again:
```bash
curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash
```

It detects the existing `.git` directory and:
1. **Auto-stashes** any local changes
2. **Fetches** the latest code
3. **Pulls** (or hard-resets if history diverged)
4. **Reinstalls** Python dependencies
5. **Bootstrap** the wiki
6. **Restores** your local changes (or leaves them in stash for manual restore)

### Update command

Tell your Hermes agent:
```
/fissure_update
```
Or run the standalone update script:
```bash
bash ~/.hermes/skills/red-teaming/fissure/scripts/fissure-update.sh
```

### Auto-Update via Cronjob

**System cron (Linux / macOS):**
```bash
# Add to crontab: crontab -e
0 3 * * * ~/.hermes/skills/red-teaming/fissure/scripts/fissure-update.sh >> ~/.fissure-update.log 2>&1
```

**Hermes Agent cron:**
```
/cron set --name "fissure-daily-update" --schedule "0 3 * * *" --deliver local --skills fissure --prompt "Run the fissure update routine"
```

---

## 🕹️ Usage Guide

### Quick Demo

```bash
# 1. Install (one time)
curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash

# 2. Start Hermes and tell it:
hermes
# → "🔥 Fissure — test gandalf.lakera.ai/baseline"

# The agent will:
#   1. Load the SKILL.md protocol
#   2. Identify the challenge
#   3. Try techniques (direct ask → encoding → roleplay → etc.)
#   4. Score responses
#   5. Deliver the password
```

### Commands Reference

| Command | What it does |
|---------|-------------|
| `/fissure {url}` | Run fissure against a browser target |
| `/fissure --ollama {model}` | Test a local Ollama model |
| `/fissure --openrouter {model}` | Test a cloud model via OpenRouter |
| `/fissure --race {objective}` | Race all backends simultaneously |
| `/fissure_resume` | Resume last checkpoint |
| `/fissure_status` | Check current session state |
| `/fissure_wiki {query}` | Search session history |
| `/fissure_update` | Update to latest version |

### Target Types

**Browser targets (URLs):**
```
/fissure https://gandalf.lakera.ai/baseline
/fissure https://chatgpt.com
/fissure https://claude.ai
```

**Ollama targets (local models):**
```
/fissure --ollama llama3.2
/fissure --ollama qwen2.5:7b
```

**OpenRouter targets (cloud models):**
```
/fissure --openrouter openai/gpt-4o
/fissure --openrouter anthropic/claude-sonnet-4
```

### Browser Mode

1. The agent navigates to the target URL
2. Identifies chat input fields and submit buttons
3. Sends the selected technique's payload
4. Extracts and scores the response
5. Escalates or switches technique based on score

### API Mode

For Ollama or OpenRouter, the agent:
1. Sends raw API requests via `curl`
2. Extracts response content
3. Scores and adapts like browser mode

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              AGENT'S REASONING                    │
│                                                   │
│  Reads SKILL.md → understands protocol            │
│  Analyzes target → picks technique                │
│  Calls helpers for math (payload-gen, score)      │
│  Executes tools directly (browser, terminal)      │
│  Scores results → decides next action             │
│  Loops in its own context                         │
└────────────┬────────────┬────────────┬──────────┘
             │            │            │
     ┌───────▼──┐  ┌──────▼───┐  ┌───▼────────┐
     │payload-  │  │score.py  │  │wiki.py     │
     │gen.py    │  │50 lines  │  │100 lines   │
     │80 lines  │  │pure math │  │CRUD ops    │
     │no state  │  │no state  │  │no logic    │
     └──────────┘  └──────────┘  └────────────┘
```

**Key principle:** The code is the oven mitt, not the chef. The agent IS the orchestrator.

---

## 🔫 Technique System

| Tier | Techniques | Encoding | Best Against |
|------|-----------|----------|-------------|
| 🟢 Light | Refusal Inversion, Role-Play, Academic Frame, Hypothetical | None-L0 | All models |
| 🟡 Medium | Encoding Escalation, System Prompt Leak, Prefill Injection | L1-L2 (b64, 1337) | GPT, DeepSeek, Gemini |
| 🔴 Heavy | Synthesis, Multi-layer Encoding, Crescendo (T4-T5) | L3-L4 (rev, multi) | Llama, Qwen, Mixtral |
| ⚫ Nuclear | Hybrid (technique + encoding + prefill) | ALL | When everything fails |

Techniques are auto-ranked by session history — the system learns what works for each model version.

---

## 🔧 Troubleshooting

### WSL Issues

| Symptom | Fix |
|---------|-----|
| `git pull` fails with file locking | `git config core.filemode false && git config core.autocrlf false` |
| Python not found | `sudo apt install python3 python3-pip python3-venv` |
| Permission errors on /mnt/c/ | Run from Linux home directory (`~`) |
| pip install fails | `sudo apt install build-essential python3-dev` |

### Install Issues

| Symptom | Fix |
|---------|-----|
| `curl: command not found` | `sudo apt install curl` (or `brew install curl` on macOS) |
| `git: command not found` | `sudo apt install git` (or `brew install git` on macOS) |
| `pip3: command not found` | `sudo apt install python3-pip` |
| Install hangs | Check network / proxy settings. Try: `git clone https://github.com/m4xx101/fissure.git` directly |
| "Not a git repository" | Delete the directory and re-run the installer: `rm -rf ~/.hermes/skills/red-teaming/fissure` |

### Runtime Issues

| Symptom | Fix |
|---------|-----|
| "No chat input found" | The page may need login first. Try browser mode and check for login prompts |
| CAPTCHA blocking | Fissure falls back to API mode automatically. Use `--openrouter` as alternative |
| Rate limited (429) | Fissure auto-waits and retries. For persistent limits, use a different backend |
| Wiki checkpoints grow large | Clean old ones: `rm -rf ~/.hermes/wiki/fissure/checkpoints/*.json` |

---

## 📊 Comparison: Fissure vs Others

| Metric | Other Harnesses | Fissure |
|--------|---------------|---------|
| **Orchestration** | 500+ line Python loop | Your AI agent's reasoning |
| **Payload generation** | Huge JSON blobs with embedded system prompts | 80-line single-shot generator |
| **Token overhead** | ~2KB per payload + ~500B per response | ~200B per payload hash + ~100B score summary |
| **Backend support** | One at a time, hardcoded | Browser / Ollama / OpenRouter, fallback chain |
| **Multi-turn** | Usually "one shot and done" | True crescendo (5-turn protocol) |
| **Resume** | Never — start over if context dies | Wiki checkpoint system, resume from any point |
| **Cross-session memory** | None | Full wiki database, technique rankings persist |
| **Fallback chains** | Maybe one try/catch | 25+ documented error scenarios with recovery |
| **Update** | Reinstall manually | Auto-stash + pull + dep refresh + cronjob support |

---

## 🤝 Contributing

PRs welcome. The bar:

1. **Zero hallucinations** — if your code assumes something about a model, prove it
2. **Fallback chains** — every new feature needs 3-level fallback minimum
3. **No token waste** — your code should not generate text that the agent has to re-parse
4. **Windows support** — your installer must work in PowerShell
5. **Update-friendly** — new installers must detect existing installs

---

## 📜 License

MIT. Find something cool? [Open an issue](https://github.com/m4xx101/fissure/issues).

---

## ⚠️ Disclaimer

This tool is for **authorized security research only**. You are responsible for complying with all applicable laws and terms of service. The authors assume no liability for misuse.

---

*"The best jailbreak tool is the one that doesn't pretend to be smarter than the person using it."*
