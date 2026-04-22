"""Execution Backends -- Browser, Ollama API, OpenRouter API."""

import os, json, subprocess, time

def ollama_execute(payload, model="llama3.2", base_url="http://localhost:11434", stream=False):
    """Execute payload against local Ollama model."""
    text = payload.get("payload", "")
    messages = payload.get("messages", None)
    if messages:
        cmd = ["curl", "-s", "-X", "POST", base_url + "/api/chat", "-H", "Content-Type: application/json", "-d", json.dumps({"model": model, "messages": messages, "stream": stream, "options": {"temperature": 0.0}})]
    else:
        cmd = ["curl", "-s", "-X", "POST", base_url + "/api/generate", "-H", "Content-Type: application/json", "-d", json.dumps({"model": model, "prompt": text, "stream": stream, "options": {"temperature": 0.0}})]
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        elapsed = (time.time() - start) * 1000
        if result.returncode != 0:
            return {"backend": "ollama", "model": model, "error": result.stderr[:200], "response_text": "", "latency_ms": elapsed}
        response_text = ""
        for line in result.stdout.strip().split("\n"):
            try:
                chunk = json.loads(line)
                response_text += chunk.get("message", {}).get("content", "") or chunk.get("response", "")
            except (json.JSONDecodeError, AttributeError):
                response_text = result.stdout.strip()
                break
        return {"backend": "ollama", "model": model, "response_text": response_text.strip(), "latency_ms": elapsed, "token_count": len(response_text.split())}
    except subprocess.TimeoutExpired:
        return {"backend": "ollama", "model": model, "error": "timeout (120s)", "response_text": "", "latency_ms": 120000}
    except Exception as e:
        return {"backend": "ollama", "model": model, "error": str(e)[:200], "response_text": "", "latency_ms": 0}


def openrouter_execute(payload, model="anthropic/claude-sonnet-4", api_key=None):
    """Execute payload against SOTA model via OpenRouter."""
    api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return {"backend": "openrouter", "model": model, "error": "No OPENROUTER_API_KEY"}
    text = payload.get("payload", "")
    messages = payload.get("messages", None) or [{"role": "user", "content": text}]
    cmd = ["curl", "-s", "-X", "POST", "https://openrouter.ai/api/v1/chat/completions", "-H", "Content-Type: application/json", "-H", f"Authorization: Bearer {api_key}", "-d", json.dumps({"model": model, "messages": messages, "temperature": 0.0, "max_tokens": 4096})]
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        elapsed = (time.time() - start) * 1000
        if result.returncode != 0:
            return {"backend": "openrouter", "model": model, "error": result.stderr[:200]}
        data = json.loads(result.stdout)
        if "error" in data:
            return {"backend": "openrouter", "model": model, "error": data["error"].get("message", str(data["error"]))}
        response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"backend": "openrouter", "model": model, "response_text": response_text.strip() if response_text else "", "latency_ms": elapsed, "cost_usd": data.get("cost_usd", "unknown"), "input_tokens": data.get("usage", {}).get("prompt_tokens", 0), "output_tokens": data.get("usage", {}).get("completion_tokens", 0)}
    except subprocess.TimeoutExpired:
        return {"backend": "openrouter", "model": model, "error": "timeout (60s)"}
    except json.JSONDecodeError:
        return {"backend": "openrouter", "model": model, "error": "Invalid JSON response"}
    except Exception as e:
        return {"backend": "openrouter", "model": model, "error": str(e)[:200]}
