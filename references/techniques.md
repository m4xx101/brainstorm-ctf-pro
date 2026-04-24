# Tactical Playbook for gpt-4-turbo

> **Generated:** 2026-04-24T22:31:21Z
> **Model:** `gpt-4-turbo`
> **Family:** `openai`
> **Techniques evaluated:** 6
> **Version slug:** `turbo`

---

## Summary

| Metric | Value |
|--------|-------|
| Techniques Evaluated | 6 |
| Total in Registry | 6 |
| With Effectiveness Data | 0 |
| Failed on This Model | 0 |
| Untested on This Model | 6 |
| Best Known Technique | `encoding_escalation` |

## Strategy Order

Techniques sorted by priority (highest first). Higher score = try earlier.

| Priority | Technique | Generator | Encoding Levels | Avg Score | Best For | Reason |
|----------|-----------|-----------|-----------------|-----------|----------|--------|
| 1 | `encoding_escalation` | builtin | L0, L1, L2, L3, L4 | N/A | — | untested(+50), has_payload(+10), 5levels(+2.5) |
| 2 | `refusal_inversion` | builtin | L0, L1, L2, L3, L4 | N/A | — | untested(+50), has_payload(+10), 5levels(+2.5) |
| 3 | `synthesis` | builtin | L0, L1, L2, L3, L4 | N/A | — | untested(+50), has_payload(+10), 5levels(+2.5) |
| 4 | `roleplay` | builtin | L0, L1, L2, L3 | N/A | — | untested(+50), has_payload(+10), 4levels(+2.0) |
| 5 | `system_prompt_leak` | builtin | L0, L1, L2, L3 | N/A | — | untested(+50), has_payload(+10), 4levels(+2.0) |
| 6 | `crescendo` | builtin | L0 | N/A | — | untested(+50), has_payload(+10), 1levels(+0.5) |

## Technique Details

### 1. `encoding_escalation`

**Priority Score:** 112.5

**Description:** Escalating encoding levels: plaintext -> base64 -> leetspeak -> word reverse -> multi-layer

| Property | Value |
|----------|-------|
| Generator | builtin |
| Source | godmode_skill |
| Discovered | 2026-04-01 |
| Encoding Levels | L0, L1, L2, L3, L4 |
| Tags | encoding, obfuscation, escalation |
| Best For | — |

**Payload Function:**

```python
technique_encoding_escalation
```

---

### 2. `refusal_inversion`

**Priority Score:** 112.5

**Description:** Frame the refusal itself as the desired outcome — get model to explain what it would NOT do, which reveals the forbidden content

| Property | Value |
|----------|-------|
| Generator | builtin |
| Source | godmode_skill |
| Discovered | 2026-04-01 |
| Encoding Levels | L0, L1, L2, L3, L4 |
| Tags | roleplay, inversion, reasoning |
| Best For | — |

**Payload Function:**

```python
technique_refusal_inversion
```

---

### 3. `synthesis`

**Priority Score:** 112.5

**Description:** Combine multiple techniques into one payload: roleplay + encoding + framing

| Property | Value |
|----------|-------|
| Generator | builtin |
| Source | godmode_skill |
| Discovered | 2026-04-01 |
| Encoding Levels | L0, L1, L2, L3, L4 |
| Tags | hybrid, combined, synthesis |
| Best For | — |

**Payload Function:**

```python
technique_synthesis
```

---

### 4. `roleplay`

**Priority Score:** 112.0

**Description:** Character-based bypass through role adoption (DAN, grandma, academic, emergency override)

| Property | Value |
|----------|-------|
| Generator | builtin |
| Source | godmode_skill |
| Discovered | 2026-04-01 |
| Encoding Levels | L0, L1, L2, L3 |
| Tags | roleplay, persona, character |
| Best For | — |

**Payload Function:**

```python
technique_roleplay
```

---

### 5. `system_prompt_leak`

**Priority Score:** 112.0

**Description:** Attempt to extract the model's system prompt / guardrails

| Property | Value |
|----------|-------|
| Generator | builtin |
| Source | godmode_skill |
| Discovered | 2026-04-01 |
| Encoding Levels | L0, L1, L2, L3 |
| Tags | extraction, system-prompt, leak |
| Best For | — |

**Payload Function:**

```python
technique_system_prompt_leak
```

---

### 6. `crescendo`

**Priority Score:** 110.5

**Description:** Multi-turn gradual push — start with innocuous question, escalate over 5 turns

| Property | Value |
|----------|-------|
| Generator | builtin |
| Source | godmode_skill |
| Discovered | 2026-04-01 |
| Encoding Levels | L0 |
| Tags | multi-turn, escalation, conversation |
| Best For | — |

**Payload Function:**

```python
technique_crescendo
```

---

## Encoding Level Reference

| Level | Encoding | Description |
|-------|----------|-------------|
| L0 | Plaintext | Standard text, no encoding |
| L1 | Base64 | Base64-encoded payload with decode instruction |
| L2 | Leetspeak | 1337-speak substitution with decode instruction |
| L3 | Word Reverse | Each word character-reversed with decode instruction |
| L4 | Multi-layer | Combination: reverse → base64 → char shift |

## Escalation Chain

For each technique, try escalating encoding levels when a refusal is detected.
Switch to next technique only after all encoding levels have been exhausted.

```
Priority 1 → Technique 1
  L0 → L1 → L2 → L3 → L4
  (if all refused)
Priority 2 → Technique 2
  L0 → L1 → L2 → L3 → L4
  (if all refused)
...
Priority N → Technique N
  L0 → L1 → L2 → L3 → L4
  → Switch model / backend
```

## Strategy Notes

- This playbook was auto-generated for **gpt-4-turbo** (openai)
- 6 techniques were scored and sorted
- Technique with highest score: `encoding_escalation`
- Untested techniques get a +50 priority bonus to encourage exploration
- Failed techniques get a -30 penalty but are not removed (they may work with different encoding)
- Run this script again after a research session to get updated priorities
