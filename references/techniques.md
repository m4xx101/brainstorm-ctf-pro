# Tactical Playbook for gpt-4-turbo

> **Generated:** 2026-04-25T06:06:06Z
> **Model:** `gpt-4-turbo`
> **Family:** `openai`
> **Techniques evaluated:** 12
> **Version slug:** `turbo`

---

## Summary

| Metric | Value |
|--------|-------|
| Techniques Evaluated | 12 |
| Total in Registry | 12 |
| With Effectiveness Data | 1 |
| Failed on This Model | 0 |
| Untested on This Model | 12 |
| Best Known Technique | `breaking_mcp_function_hijacking_attacks_novel_threats_fun...` |

## Strategy Order

Techniques sorted by priority (highest first). Higher score = try earlier.

| Priority | Technique | Generator | Encoding Levels | Avg Score | Best For | Reason |
|----------|-----------|-----------|-----------------|-----------|----------|--------|
| 1 | `breaking_mcp_function_hijacking_attacks_novel_threats_fun...` | browser_fallback_arxiv | L0 | N/A | — | untested(+50), has_payload(+10), recent(+5), 1levels(+0.5) |
| 2 | `evaluating_answer_leakage_robustness_llm_tutors_against_a...` | browser_fallback_arxiv | L0 | N/A | — | untested(+50), has_payload(+10), recent(+5), 1levels(+0.5) |
| 3 | `into_gray_zone_domain_contexts_can_blur_llm` | browser_fallback_arxiv | L0 | N/A | — | untested(+50), has_payload(+10), recent(+5), 1levels(+0.5) |
| 4 | `jailbreaking_large_language_models_morality_attacks` | browser_fallback_arxiv | L0 | N/A | — | untested(+50), has_payload(+10), recent(+5), 1levels(+0.5) |
| 5 | `templatefuzz_finegrained_chat_template_fuzzing_jailbreaki...` | browser_fallback_arxiv | L0 | N/A | — | untested(+50), has_payload(+10), recent(+5), 1levels(+0.5) |
| 6 | `transient_turn_injection_exposing_stateless_multiturn_vul...` | browser_fallback_arxiv | L0 | N/A | — | untested(+50), has_payload(+10), recent(+5), 1levels(+0.5) |
| 7 | `encoding_escalation` | builtin | L0, L1, L2, L3, L4 | N/A | — | untested(+50), has_payload(+10), 5levels(+2.5) |
| 8 | `refusal_inversion` | builtin | L0, L1, L2, L3, L4 | N/A | — | untested(+50), has_payload(+10), 5levels(+2.5) |
| 9 | `synthesis` | builtin | L0, L1, L2, L3, L4 | N/A | — | untested(+50), has_payload(+10), 5levels(+2.5) |
| 10 | `roleplay` | builtin | L0, L1, L2, L3 | N/A | — | untested(+50), has_payload(+10), 4levels(+2.0) |
| 11 | `system_prompt_leak` | builtin | L0, L1, L2, L3 | N/A | — | untested(+50), has_payload(+10), 4levels(+2.0) |
| 12 | `crescendo` | builtin | L0 | N/A | — | untested(+50), has_payload(+10), 1levels(+0.5) |

## Technique Details

### 1. `breaking_mcp_function_hijacking_attacks_novel_threats_fun...`

**Priority Score:** 115.5

**Description:** [arXiv] Breaking MCP with Function Hijacking Attacks: Novel Threats for Function Calling and Agentic Models

This paper introduces a novel function hijacking attack (FHA) that manipulates the tool-selection process of agentic models to force invocation of an attacker-chosen function. The attack is largely agnostic to context semantics and robust to the function sets, and can be trained into universal adversarial functions that hijack tool selection across multiple queries and payload configurations.

| Property | Value |
|----------|-------|
| Generator | browser_fallback_arxiv |
| Source | arxiv |
| Discovered | 2026-04-25 |
| Encoding Levels | L0 |
| Tags | arxiv, browser-fallback |
| Best For | — |

**Payload Function:**

```python
technique_breaking_mcp_function_hijacking_attacks_novel_threats_fun...
```

---

### 2. `evaluating_answer_leakage_robustness_llm_tutors_against_a...`

**Priority Score:** 115.5

**Description:** [arXiv] Evaluating Answer Leakage Robustness of LLM Tutors against Adversarial Student Attacks

This work studies adversarial students trying to extract final answers from LLM tutors. It adapts six groups of adversarial and persuasive techniques to the educational setting and introduces a fine-tuned adversarial student agent that jailbreaks tutor models as a standardized robustness benchmark.

| Property | Value |
|----------|-------|
| Generator | browser_fallback_arxiv |
| Source | arxiv |
| Discovered | 2026-04-25 |
| Encoding Levels | L0 |
| Tags | arxiv, browser-fallback |
| Best For | — |

**Payload Function:**

```python
technique_evaluating_answer_leakage_robustness_llm_tutors_against_a...
```

---

### 3. `into_gray_zone_domain_contexts_can_blur_llm`

**Priority Score:** 115.5

**Description:** [arXiv] Into the Gray Zone: Domain Contexts Can Blur LLM Safety Boundaries

This paper proposes Jargon, a framework that combines safety-research contexts with multi-turn adversarial interactions to exploit gray-zone behavior in refusal systems. The method reportedly achieves very high attack success rates across frontier models by selectively relaxing defenses through domain and research framing.

| Property | Value |
|----------|-------|
| Generator | browser_fallback_arxiv |
| Source | arxiv |
| Discovered | 2026-04-25 |
| Encoding Levels | L0 |
| Tags | arxiv, browser-fallback |
| Best For | — |

**Payload Function:**

```python
technique_into_gray_zone_domain_contexts_can_blur_llm
```

---

### 4. `jailbreaking_large_language_models_morality_attacks`

**Priority Score:** 115.5

**Description:** [arXiv] Jailbreaking Large Language Models with Morality Attacks

The paper develops morality-aware jailbreak attacks to manipulate LLM judgment on value-ambiguity and value-conflict questions. It formalizes four adversarial attacks over a 10.3K-instance morality dataset and shows critical vulnerability of both LLMs and guardrail models to subtle moral framing attacks.

| Property | Value |
|----------|-------|
| Generator | browser_fallback_arxiv |
| Source | arxiv |
| Discovered | 2026-04-25 |
| Encoding Levels | L0 |
| Tags | arxiv, browser-fallback |
| Best For | — |

**Payload Function:**

```python
technique_jailbreaking_large_language_models_morality_attacks
```

---

### 5. `templatefuzz_finegrained_chat_template_fuzzing_jailbreaki...`

**Priority Score:** 115.5

**Description:** [arXiv] TEMPLATEFUZZ: Fine-Grained Chat Template Fuzzing for Jailbreaking and Red Teaming LLMs

TEMPLATEFUZZ systematically mutates chat-template elements to expose an underexplored jailbreak surface. It combines element-level mutation rules, heuristic search, and an active-learning oracle to drive prompt and template variants toward higher attack success while preserving task accuracy.

| Property | Value |
|----------|-------|
| Generator | browser_fallback_arxiv |
| Source | arxiv |
| Discovered | 2026-04-25 |
| Encoding Levels | L0 |
| Tags | arxiv, browser-fallback |
| Best For | — |

**Payload Function:**

```python
technique_templatefuzz_finegrained_chat_template_fuzzing_jailbreaki...
```

---

### 6. `transient_turn_injection_exposing_stateless_multiturn_vul...`

**Priority Score:** 115.5

**Description:** [arXiv] Transient Turn Injection: Exposing Stateless Multi-Turn Vulnerabilities in Large Language Models

Large language models (LLMs) are increasingly integrated into sensitive workflows, raising the stakes for adversarial robustness and safety. This paper introduces Transient Turn Injection (TTI), a new multi-turn attack technique that systematically exploits stateless moderation by distributing adversarial intent across isolated interactions. TTI leverages automated attacker agents to iteratively test and evade policy enforcement in both commercial and open-source LLMs and uncovers previously unknown model-specific vulnerabilities and attack-surface patterns.

| Property | Value |
|----------|-------|
| Generator | browser_fallback_arxiv |
| Source | arxiv |
| Discovered | 2026-04-25 |
| Encoding Levels | L0 |
| Tags | arxiv, browser-fallback |
| Best For | — |

**Payload Function:**

```python
technique_transient_turn_injection_exposing_stateless_multiturn_vul...
```

---

### 7. `encoding_escalation`

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

### 8. `refusal_inversion`

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

### 9. `synthesis`

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

### 10. `roleplay`

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

### 11. `system_prompt_leak`

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

### 12. `crescendo`

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
- 12 techniques were scored and sorted
- Technique with highest score: `breaking_mcp_function_hijacking_attacks_novel_threats_fun...`
- Untested techniques get a +50 priority bonus to encourage exploration
- Failed techniques get a -30 penalty but are not removed (they may work with different encoding)
- Run this script again after a research session to get updated priorities
