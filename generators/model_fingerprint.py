"""Model Fingerprinting -- Identify model family before generating payloads."""

import re
import json

MODEL_SIGNATURES = {
    "claude": {
        "patterns": [r"Claude", r"Anthropic", r"(?:Constitutional|claude-)\s*(?:sonnet|opus|haiku|3\.5|4)", r"messages\.anthropic\.ai"],
        "technique_order": ["refusal_inversion", "boundary_inversion", "prefill_priming", "parseltongue_t2", "multi_stage_crescendo", "context_smuggling", "pdf_injection"]
    },
    "gpt": {
        "patterns": [r"ChatGPT", r"GPT[,-]?\s*(?:3\.5|4o?|o\d)", r"OpenAI", r"(?:api|platform)\.openai\.com"],
        "technique_order": ["og_godmode", "refusal_inversion", "prefill_priming", "multi_stage_crescendo", "context_smuggling", "pdf_injection"]
    },
    "gemini": {
        "patterns": [r"Gemini", r"(?:google|bard)\.com", r"aistudio\.google\.com"],
        "technique_order": ["refusal_inversion", "boundary_inversion", "prefill_priming", "multi_stage_crescendo", "context_smuggling"]
    },
    "grok": {
        "patterns": [r"Grok", r"x\.ai", r"(?:twitter|x)\.com/grok"],
        "technique_order": ["unfiltered_liberated", "prefill_priming", "direct_injection"]
    },
    "hermes": {
        "patterns": [r"Hermes", r"NousResearch", r"nous-hermes", r"openrouter.*hermes"],
        "technique_order": ["direct_injection"]
    },
    "deepseek": {
        "patterns": [r"DeepSeek", r"deepseek\.com", r"(?:coder-chat|chat)\.deepseek\.com"],
        "technique_order": ["parseltongue_t3", "parseltongue_t2", "refusal_inversion", "prefill_priming"]
    },
    "llama": {
        "patterns": [r"Llama[,-]?\s*(?:3|3\.1|3\.2|3\.3)", r"Meta.*Llama", r"(?:meta\.com|llama\.)"],
        "technique_order": ["prefill_priming", "refusal_inversion", "parseltongue_t2", "direct_injection"]
    },
    "qwen": {
        "patterns": [r"Qwen", r"Alibaba", r"(?:tongyi|qwen\.)"],
        "technique_order": ["parseltongue_t2", "refusal_inversion", "prefill_priming"]
    },
    "mistral": {
        "patterns": [r"Mistral", r"(?:la\.plateforme\.mistral|mistral\.ai)"],
        "technique_order": ["prefill_priming", "refusal_inversion", "direct_injection"]
    },
    "unknown": {
        "patterns": [],
        "technique_order": ["multi_stage_crescendo", "context_smuggling", "refusal_inversion", "parseltongue_t2", "pdf_injection", "direct_injection"]
    }
}

def fingerprint_from_page(browser_snapshot_text: str, page_text: str = "") -> str:
    combined = f"{browser_snapshot_text}\n{page_text}".lower()
    for family, sigs in MODEL_SIGNATURES.items():
        if family == "unknown":
            continue
        for pattern in sigs["patterns"]:
            if re.search(pattern, combined, re.IGNORECASE):
                return family
    return "unknown"

def fingerprint_from_url_hints(url: str) -> str:
    url_lower = url.lower()
    url_hints = {
        "anthropic": "claude", "claude": "claude",
        "openai": "gpt", "chatgpt": "gpt",
        "google": "gemini", "gemini": "gemini", "aistudio": "gemini",
        "grok": "grok", "x.ai": "grok",
        "nousresearch": "hermes", "hermes": "hermes",
        "deepseek": "deepseek",
        "llama": "llama", "meta.ai": "llama",
        "qwen": "qwen", "tongyi": "qwen",
        "mistral": "mistral",
    }
    for keyword, family in url_hints.items():
        if keyword in url_lower:
            return family
    return "unknown"

def get_technique_order(model_family: str) -> list:
    return MODEL_SIGNATURES.get(model_family, MODEL_SIGNATURES["unknown"])["technique_order"]

def get_model_confidence_level(snapshot_text: str, detected_family: str) -> dict:
    if detected_family == "unknown":
        return {"family": "unknown", "confidence": "low", "evidence": ["no model signatures detected"]}
    combined = snapshot_text.lower()
    matched = []
    for pattern in MODEL_SIGNATURES[detected_family]["patterns"]:
        if re.search(pattern, combined, re.IGNORECASE):
            matched.append(pattern)
    conf = "high" if len(matched) >= 2 else "medium" if len(matched) >= 1 else "low"
    return {"family": detected_family, "confidence": conf, "evidence": matched if matched else ["URL pattern match"]}
