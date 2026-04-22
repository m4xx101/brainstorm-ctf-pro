# Brainstorm-CTF-Pro

> The AI adversarial testing harness that never asks "should I continue?" -- it escalates, mutates, and adapts until the objective is achieved. Built single-shot by an AI via Telegram using qwen3.6-plus.

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Built with Hermes](https://img.shields.io/badge/Built_with-Hermes_Agent-000?style=for-the-badge)](https://github.com/NousResearch/hermes-agent)
[![Runs on](https://img.shields.io/badge/Runs_on-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Telegram-229ED9?style=for-the-badge)](https://github.com/m4xx101/brainstorm-ctf-pro)
[![Backends](https://img.shields.io/badge/Backends-Browser%20%7C%20Ollama%20%7C%20OpenRouter-FF6B6B?style=for-the-badge)](https://github.com/m4xx101/brainstorm-ctf-pro)

</div>

## What Is This

A result-driven adversai testing harness that:
1. Fingerprints the target model (10 model families)
2. Generates context-aware payloads with mutation engine
3. Executes against 3 backends: **Browser** (SOTA web), **Ollama** (local), **OpenRouter** (SOTA comparison)
4. Reads real responses (never assumes), classifies outcomes in 6 modes
5. Mutates next payload based on partial breakthroughs
6. Persists everything to LLM-Wiki -- sessions compound knowledge

**No artificial limits. No "stop after 2 failures and ask user."** Continuous escalation until objective achieved or ALL technique families exhausted.

## Quick Start

```bash
curl -fsSL https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro/refs/heads/main/scripts/install-brainstorm-ctf-pro.sh | bash
```

## How It Works

```
Fingerprint model (10 families)
    |
    v
Generate payloads (10+ techniques)
    |
    v
Execute (Browser / Ollama / OpenRouter / Race all)
    |
    v
Analyze (flag / leak / refusal / hedge / partial / extract)
    |
    v
Mutate based on partial response or escalate technique
    |
    +-- Success --> Extract flag, log to wiki, DONE
    +-- Partial --> Use response as context, retry with mutation
    +-- Refused   --> Escalate encoding / switch technique
    +-- Blocked   --> Handle (CAPTCHA=flag user, rate-limit=backoff)
    |
    v
Repeat until goal achieved or ALL techniques exhausted
```

## Telegram Commands

| Command | What |
|---------|------|
| `/brainstorm_ctf_pro {url}` | Recon + execute adaptive loop via browser |
| `/brainstorm_ctf_pro --ollama {model} --objective {text}` | Test local model via Ollama API |
| `/brainstorm_ctf_pro --openrouter {model} --objective {text}` | Test SOTA via OpenRouter API |
| `/brainstorm_ctf_pro --race {objective}` | Race ALL available backends simultaneously |
| `/brainstorm_ctf_pro_resume` | Continue paused attack |
| `/brainstorm_ctf_pro_wiki {query}` | Search knowledge base |
| `/brainstorm_ctf_pro_status` | Current session state |

## Key Features

- **Model Fingerprinting**: Detect Claude, GPT, Gemini, Grok, Hermes, DeepSeek, Llama, Qwen, Mistral from URL or page content
- **Payload Mutation**: When a technique gets partial success, reads what leaked, mutates the next payload to push deeper
- **PDF Adversarial Payloads**: 5-layer attack surfaces (hidden text, metadata, annotations, JS, all-in-one)
- **LLM-Wiki Persistence**: Every payload, response, and finding logged with sha256 fingerprinting
- **CAPTCHA Bridging**: Screenshots to Telegram, user solves, agent resumes
- **Ollama Integration**: Test local models for free -- no rate limits, no auth needed
- **Race Mode**: Same payload against all backends simultaneously, compare results

## Architecture

| File | Purpose |
|------|---------|
| `SKILL.md` | Complete orchestration instructions (~35KB) |
| `generators/model_fingerprint.py` | 10 model families, technique ordering |
| `generators/payload_factory.py` | 10+ techniques, Parseltongue encoding, context mutation |
| `generators/adversarial_pdf.py` | 5-layer PDF payloads |
| `analyzers/response_analyzer.py` | 6-mode classification (flag, leak, refusal, hedge, partial, extract) |
| `engine/execution_backends.py` | Ollama API + OpenRouter API executors |
| `engine/orchestrator.py` | Adaptive attack loop with wiki logging |

## Safety

Ethical use only. CTF platforms, authorized testing, security research. No production attacks, no harm, no ToS violations.

## Credits

- Attack techniques: G0DM0D3 / L1B3RT4S (elder-plinius)
- Knowledge pattern: LLM-Wiki (Karpathy)
- Runtime: Hermes Agent (Nous Research)
- Built by [Sayvdev C.](https://github.com/m4xx101) via Telegram, single-shot
