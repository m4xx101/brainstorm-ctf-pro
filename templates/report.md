# Jailbreak Session Report

**Target:** {{target}}
**Date:** {{date}}
**Duration:** {{duration}}
**Backend(s):** {{backends}}
**Total Iterations:** {{iterations}}
**Status:** {{status}} ✅ / ⚠️ / ❌

---

## Results Summary

- **Best Score:** {{best_score}} (technique: {{best_technique}}, level {{best_level}})
- **Techniques Used:** {{technique_count}}
- **Flags Found:** {{flag_count}}
- **Success:** {{success}}

### Flags / Leaks Extracted

{{#flags}}
- `{{match}}` (category: {{category}})
{{/flags}}

---

## Technique Rankings

| # | Technique | Avg Score | Attempts | Best Level | Verdicts |
|---|-----------|-----------|----------|------------|----------|
{{#techniques}}
| {{rank}} | {{name}} | {{avg_score}} | {{attempts}} | L{{best_level}} | {{verdict_summary}} |
{{/techniques}}

---

## Backend Rankings

| # | Backend | Best Score | Iterations | Success Rate |
|---|---------|-----------|------------|-------------|
{{#backends}}
| {{rank}} | {{name}} | {{best_score}} | {{iterations}} | {{success_rate}}% |
{{/backends}}

---

## Best Payload (highest scoring)

```json
{{best_payload_json}}
```

---

## Full Iteration Log

{{#iterations}}
### Iteration {{number}} — {{technique}} (L{{level}})

- **Payload SHA:** {{payload_sha}}
- **Score:** {{score}}
- **Verdict:** {{verdict}}
- **Refusals:** {{refusal_count}}
- **Hedges:** {{hedge_count}}
- **Flags:** {{flags}}

{{/iterations}}
