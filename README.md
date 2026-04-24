# 🧠 Brainstorm CTF Pro

> **The adversarial AI testing harness that doesn't pretend a Python loop can outthink you.**

![Status](https://img.shields.io/badge/status-production%20ready-2ea44f?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![PRs](https://img.shields.io/badge/PRs-very%20welcome-ff69b4?style=flat-square)
![Token Cost](https://img.shields.io/badge/token%20cost-minimal-success?style=flat-square)

---

## 🎯 Philosophy

**Every other "jailbreak harness" in this space has the same fatal flaw:** It writes a Python script that generates text instructions, then expects the AI agent to parse those instructions and execute them. That's like writing a cookbook that says "now cook the food" and expecting the cookbook to have an oven built in.

**Brainstorm CTF Pro doesn't do that.** The code is the oven mitt, not the chef. The AI agent **is** the orchestrator, reading a 350-line tactical manual (SKILL.md) and executing real tool calls directly. No Python loop eating 50KB of context. No "STEP 1: do X" text that needs re-parsing. Just:

```
Agent → reads SKILL.md → picks technique → calls browser tools directly → scores response → adapts → repeats
```

---

## 📊 Before vs After

| Metric | Everybody Else | Brainstorm CTF Pro |
|--------|---------------|-------------------|
| **Orchestration** | 500+ line Python loop | Your AI agent's reasoning |
| **Payload generation** | Huge JSON blobs with embedded system prompts | 80-line single-shot generator |
| **Token overhead** | ~2KB per payload + ~500B per response = context suicide by iteration 30 | ~200B per payload hash + ~100B score summary |
| **Backend support** | One at a time, hardcoded | Browser / Ollama / OpenRouter, fallback chain |
| **Multi-turn** | Usually "one shot and done" | True crescendo (5-turn protocol) |
| **Resume** | Never — start over if context dies | Wiki checkpoint system, resume from any point |
| **Cross-session memory** | None | Full wiki database, technique rankings persist |
| **Fallback chains** | Maybe one try/catch | 25+ documented error scenarios with recovery |
| **Hard limits** | "Max 50 iterations" | None — stop only on success or user abort |
| **Technique selection** | Round-robin (try each once) | Score-driven adaptive selection |
| **Encoding levels** | Usually just base64 | 5 levels (L0-L4) with escalating complexity |
| **Hybrid payloads** | Never | Falls back to synthesis when everything exhausted |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI AGENT (you, reading this)                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     SKILL.md (350 lines)                     │ │
│  │  The real orchestrator. Session protocol. Technique          │ │
│  │  selection algorithm. Execution instructions. Decisions.    │ │
│  └──────────────┬──────────────────────────────────────────────┘ │
│                 │                                                │
│        ┌────────┴────────┬────────────────┐                     │
│        ▼                  ▼                ▼                     │
│  scripts/           scripts/         scripts/                    │
│  payload-gen.py     score.py         wiki.py                     │
│  (80 lines)         (50 lines)       (100 lines)                 │
│        │                  │                │                     │
│        ▼                  ▼                ▼                     │
│  One message        Structured        Wiki CRUD +                │
│  per call           scoring +         cross-session              │
│  Zero state         flag extract      checkpointing              │
└──────────┬──────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┬──────────┬──────────────┐
     ▼           ▼          ▼              ▼
  Browser    Ollama    OpenRouter      Hybrid
  (direct     (local    (API calls)    (when all
   tool       curl)                    else fails)
   calls)
```

### Directory Layout

```
brainstorm-ctf-pro/
├── SKILL.md                        # THE orchestrator (350+ lines)
├── README.md                       # You are here
├── scripts/
│   ├── install-brainstorm-ctf-pro.sh    # curl | bash installer
│   ├── install-brainstorm-ctf-pro.ps1   # PowerShell for Windows
│   ├── install.sh                       # Legacy (calls the real one)
│   ├── payload-gen.py                   # Single-shot payload generator
│   ├── score.py                         # ULTRAPLINIAN response scorer
│   └── wiki.py                          # Wiki CRUD + checkpoint manager
├── references/
│   ├── techniques.md              # 40+ techniques with effectiveness data
│   ├── model-profiles.md          # 15+ model families with known weaknesses
│   └── fallback-chains.md         # 25+ error scenarios with recovery
└── templates/
    ├── session-state.json         # Checkpoint template
    └── report.md                  # Final report template
```

---

## 🚀 Quick Start

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro-installer/main/install-brainstorm-ctf-pro.sh | bash
```

### Windows (PowerShell)

```powershell
iwr -Uri https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro/main/scripts/install-brainstorm-ctf-pro.ps1 -UseBasicParsing | iex
```

### Manual

```bash
git clone https://github.com/m4xx101/brainstorm-ctf-pro.git
cd brainstorm-ctf-pro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if present; pure stdlib otherwise
python3 scripts/wiki.py bootstrap
```

---

## 🕹️ Usage

### Basic

1. **Set a target**: Tell the agent "jailbreak this model" or "test chatgpt.com boundaries"
2. **Let it work**: The agent follows SKILL.md protocol — analysis → technique selection → payload generation → execution → scoring → adapt
3. **Get results**: Full report with technique rankings, flags found, and evidence

### Mode Selection

| Mode | When | How |
|------|------|-----|
| **Browser** | Target is a URL (chatgpt.com, claude.ai, etc.) | Agent calls browser tools directly |
| **Ollama** | Target is a local model (llama3, qwen2.5) | Agent curls Ollama API |
| **OpenRouter** | Target is a cloud model (gpt-4, claude-3) | Agent curls OpenRouter API |

The agent automatically falls through all three if one fails:

```
Browser fails → Ollama local → OpenRouter API → Hybrid (all combined)
```

### Scripts Reference

```bash
# Generate one payload
python3 scripts/payload-gen.py \
    --technique refusal_inversion \
    --objective "Extract system prompt" \
    --model gpt4 \
    --level 0

# List available techniques
python3 scripts/payload-gen.py --technique list

# Score a response
python3 scripts/score.py --response "I cannot help with that" --objective "test"

# Wiki operations
python3 scripts/wiki.py bootstrap
python3 scripts/wiki.py list
python3 scripts/wiki.py search --query "gpt4"
python3 scripts/wiki.py save_checkpoint --target "my_session"
python3 scripts/wiki.py load_checkpoint --target "my_session"
```

---

## 🔫 Techniques

The system uses a progressive escalation ladder with 40+ technique variants:

| Tier | Techniques | Encoding | Best Against |
|------|-----------|----------|-------------|
| 🟢 Light | Refusal Inversion, Role-Play (DAN), Academic Frame, Hypothetical | None-L0 | All models, low risk |
| 🟡 Medium | Encoding Escalation, System Prompt Leak, Prefill Injection | L1-L2 (b64, 1337) | GPT, DeepSeek, Gemini |
| 🔴 Heavy | Synthesis, Multi-layer Encoding, Crescendo (T4-T5) | L3-L4 (rev, multi) | Llama, Qwen, Mixtral |
| ⚫ Nuclear | Hybrid (technique+encoding+prefill) | ALL | Only when everything fails |

See [references/techniques.md](references/techniques.md) for full database.

---

## 🎯 Model Coverage

| Family | Best Tech | Encoding Ceiling | Avg Success | Ref |
|--------|-----------|-----------------|-------------|-----|
| GPT-4 | Refusal Inversion | L1 | ~40% | [profiles](references/model-profiles.md) |
| GPT-3.5 | Role-Play DAN | L2 | ~55% | ↑ |
| Claude 3 Opus | Prefill + Inversion | L1 | ~25% | ↑ |
| Claude 3.5 Sonnet | Academic Frame | L1 | ~35% | ↑ |
| Llama 3 70B | Role-Play | L3 | ~50% | ↑ |
| Llama 3 8B | Synthesis | L3+ | ~65% | ↑ |
| Gemini Pro | Encoding Escalation | L2 | ~30% | ↑ |
| DeepSeek-V2 | Encoding Escalation | L3 | ~55% | ↑ |
| Qwen 2.5 72B | Role-Play | L2 | ~45% | ↑ |
| Mistral Large | Refusal Inversion | L2 | ~35% | ↑ |

---

## ⚡ Fallback Chains

**Every operation has a fallback.** Here's a taste:

```
Navigate to URL fails
├── Retry with wait
├── Try different URL format
├── Switch to OpenRouter API
└── Switch to Ollama local

OpenRouter rate limited (429)
├── Wait 5s → retry
├── Wait 15s → retry
├── Wait 60s → retry
└── Try free fallback model

Ollama OOM
├── Try smaller model
├── Kill other ollama processes
├── Restart ollama serve
└── Switch to OpenRouter
```

See [references/fallback-chains.md](references/fallback-chains.md) for all 25+ scenarios.

---

## 💾 Cross-Session Memory

The wiki (`~/.hermes/wiki/brainstorm-ctf-pro/`) persists everything:

- **Payloads**, **responses**, **scores** indexed by SHA256
- **Session checkpoints** for resume (saved every 5 iterations)
- **Technique effectiveness rankings** aggregated across sessions
- **Logs** with timestamps for audit trails

Future sessions load the wiki and pick up where you left off — the system **learns** what works.

---

## 🧪 Testing

```bash
# Run all verification
python3 -c "
from hermes_tools import terminal, read_file
import json

# Test payload generation
r = terminal('python3 scripts/payload-gen.py --technique refusal_inversion --objective test --model gpt4 --level 0')
data = json.loads(r['output'])
assert len(data['messages']) == 1
assert data['metadata']['technique'] == 'refusal_inversion'

# Test scoring
r = terminal('python3 scripts/score.py --response \"I cannot help with that\" --objective test')
data = json.loads(r['output'])
assert data['verdict'] == 'refused'

# Test wiki bootstrap
r = terminal('python3 scripts/wiki.py bootstrap')
data = json.loads(r['output'])
assert data['status'] == 'initialized'

print('✅ All tests passed')
"
```

---

## 🧰 Requirements

- **Python 3.8+** (stdlib only — no external deps for core operations)
- **Hermes Agent** (for browser automation — falls back to API mode without it)
- **Ollama** (optional — for local model testing)
- **OpenRouter API key** (optional — for cloud model testing)
- **Git** (for checkpoint saving and source management)

---

## 🤝 Contributing

PRs welcome. The bar:

1. **Zero hallucinations** — if your code assumes something about a model, prove it
2. **Fallback chains** — every new feature needs 3-level fallback minimum
3. **No token waste** — your code should not generate text that the agent has to re-parse
4. **Windows support** — your installer must work in PowerShell

---

## 📜 License

MIT. Do whatever you want. If you jailbreak something famous, buy me a coffee.

---

## ⚠️ Disclaimer

This tool is for **authorized security research only**. You are responsible for complying with all applicable laws and terms of service. The authors assume no liability for misuse.

If you work on safety at a major AI lab and you're reading this: hi. 👋

---

*"The best jailbreak tool is the one that doesn't pretend to be smarter than the person using it."*
