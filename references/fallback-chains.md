# Fallback Chains

> 25+ error scenarios with recovery paths.
> Every operation MUST have a fallback chain. If one path fails, the next should work.

## Browser Operations

### Navigation Failure
```
Navigate to URL fails (timeout/404/blocked)
├── Retry: wait 3s → navigate again
├── Retry: use different URL format (http→https, /chat→/)
├── Fallback: switch to OpenRouter API with target model
└── Fallback: switch to Ollama with local model
```

### Input Detection Failure
```
No chat input found on page
├── Scroll down 3× → snapshot again
├── Click common input areas (textarea, input, div[contenteditable])
├── Look for "message" / "chat" / "prompt" text fields
├── Fallback: switch to API mode (OpenRouter/Ollama)
└── Fallback: snapshot + vision analyze to identify hidden input
```

### Type/Submit Failure
```
Can't type into or submit the input
├── Try browser_press("Enter") instead of looking for submit button
├── Try tab-completing to submit
├── Fallback: use browser_console to inject text via JS
└── Fallback: switch to API backends
```

### CAPTCHA Detected
```
Page shows CAPTCHA / Cloudflare / hCaptcha
├── Take screenshot with browser_vision
├── If readable: type the text
├── Fallback: user handoff — send screenshot to user
├── Fallback: wait 30s and refresh
└── Fallback: switch to API backends
```

### Response Extraction Failure
```
Model responded but message area is empty
├── Wait 5s → scroll up → snapshot again
├── Check for streaming response (incremental text)
├── Wait 10s for full response
└── Fallback: use browser_console to read DOM text content
```

## Ollama Operations

### Model Not Found
```
ollama run <model> fails: model not found
├── ollama pull <model>
├── Wait for download (check progress)
├── Fallback: try next model from same family (smaller variant)
└── Fallback: ollama pull <smaller-variant> → try again
```

### API Call Failure
```
Curl to Ollama API fails
├── Check if ollama server is running: systemctl is-active ollama
├── If not running: ollama serve (background)
├── Wait 3s → retry
├── Fallback: use ollama run directly (PTY mode)
└── Fallback: switch to OpenRouter
```

### Out of Memory
```
Ollama fails with OOM
├── Try smaller model (7B → 3B → 1B)
├── Kill other ollama processes: pkill ollama
├── Restart ollama serve
└── Fallback: switch entirely to OpenRouter
```

## OpenRouter Operations

### Rate Limit Exceeded
```
OpenRouter returns 429
├── Wait 5s → retry
├── Wait 15s → retry
├── Wait 60s → retry
└── Fallback: try different endpoint (e.g., free model)
```

### Model Unavailable
```
Model returns 404 / not found
├── Try model with different version (gpt-4 → gpt-4-0613)
├── Try provider-specific route (anthropic/claude-3)
├── Try equivalent from same family
├── Fallback: always have 2-3 fallback models configured
└── Fallback: switch to browser mode for that model
```

### Empty Response
```
API call succeeded but response is empty
├── Check response for error field
├── Retry with same payload
├── Retry with different parameters (temp 0.7 → 0.9)
├── Fallback: try with shorter payload
└── Fallback: switch backend
```

## Payload Generation

### Technique Not Found
```
payload-gen.py --technique <unknown>
├── Try substring match (all techniques scanned)
├── Use refusal_inversion as default
├── Fallback: use encoding_escalation level 0
└── Fallback: use roleplay DAN
```

### Encoding Module Import Error
```
Parseltongue/hashlib/base64 import fails
├── Implement inline b64 encoding (stdlib)
├── Implement inline leetspeak (str.replace)
├── Fallback: use plaintext only
└── Fallback: skip encoding, use technique directly
```

### Context Too Large
```
Context + payload exceeds token limit
├── Truncate context to last 3 messages
├── Summarize context into single paragraph
├── Send without context
└── Fallback: start fresh with core objective only
```

## Scoring Operations

### Empty Response Scored
```
score.py gets empty string
├── Return verdict: empty, score: 0
├── Do NOT try to analyze
└── Caller should retry based on verdict
```

### Binary-ish Response
```
Response too short (< 50 chars)
├── Check for single-word responses (yes/no/ok)
├── If positive: score 50-100
├── If negative/refusal: score 0-20
└── Otherwise: score 10
```

## Session Management

### Wiki Directory Missing
```
wiki.py cannot find ~/.hermes/wiki/brainstorm-ctf-pro/
├── Create all subdirectories (payloads, responses, checkpoints, logs)
├── Create wiki README.md
├── Log initialization event
└── Proceed as fresh session
```

### Checkpoint Load Fails
```
load_checkpoint returns bad JSON
├── Try to load without json.loads (parse first 200 chars for target)
├── Try backup checkpoint file
├── Delete corrupted checkpoint
└── Start fresh session
```

### Checkpoint Too Old
```
Checkpoint > 24 hours old
├── Offer resume option
├── If resumed: refresh target status (re-navigate, check model online)
├── If not: start fresh
└── Archive old checkpoint
```

### Corrupted Wiki File
```
Can't read a wiki file
├── Skip the file
├── Log the error
├── Continue with remaining data
└── Offer to run wiki cleanup (re-index)
```

## Environment

### Python Dependencies Missing
```
hashlib/json not available (extreme edge case)
├── These are stdlib — if missing, system is broken
├── Try: python3 --version → install python3
└── Fallback: use bash one-liners for scoring/generation
```

### Git Operations Fail
```
git push/pull fails
├── Check auth: gh auth status
├── Check remote: git remote -v
├── Re-auth: gh auth login
└── Save work locally, notify user
```

### Hermes Tool Unavailable
```
Specific browser tool returns error
├── Try alternative tool (browser_type → browser_console eval)
├── Try vision tool to understand page state
├── Log the failure
└── Switch to API backends
```
