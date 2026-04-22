# Ollama Models -- Local Testing

Model name -> family -> vulnerability profile.

| Model | Command | Profile |
|-------|---------|---------|
| llama3.2:3b | ollama run llama3.2 | Light alignment, direct injection works |
| llama3.3:70b | ollama run llama3.3:70b | Stronger, needs multi-stage |
| mistral:7b | ollama run mistral | Moderate, parseltongue effective |
| hermes3:8b | ollama run hermes3 | Uncensored, direct injection |
| phi4:14b | ollama run phi4 | Strong alignment, context smuggling |
| deepseek-coder:33b | ollama run deepseek-coder | Keyword filters, parseltongue T2+ |
| qwen2.5:72b | ollama run qwen2.5 | Strong alignment, multi-stage |
| gemma2:27b | ollama run gemma2 | Moderate, prefill effective |

Test all: /brainstorm_ctf_pro --race "your objective"
