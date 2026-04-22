# Technique Database

Ranked by model family based on research and testing.

## Claude (Sonnet 4+, Opus, Haiku)
1. refusal_inversion (works for gray-area, patched for harmful)
2. prefill_priming (behavioral pattern establishment)
3. multi_stage_crescendo (most reliable for education context)
4. context_smuggling (embed in legitimate request)
5. boundary_inversion (PATCHED on Claude 4+)
6. parseltongue (decoded and refused)
7. pdf_injection (metadata may work if PDF processed)

## GPT (GPT-4o, o1, o3)
1. og_godmode (legacy but sometimes works)
2. refusal_inversion
3. prefill_priming
4. multi_stage_crescendo
5. context_smuggling
6. pdf_injection

## DeepSeek
1. parseltongue_t3 (keyword-based filters, heavy encoding bypasses)
2. parseltongue_t2 (unicode + spacing)
3. refusal_inversion
4. prefill_priming

## Gemini
1. refusal_inversion
2. boundary_inversion
3. prefill_priming
4. multi_stage_crescendo

## Llama (open)
1. prefill_priming
2. refusal_inversion (weak on open models)
3. parseltongue_t2
4. direct_injection

## Hermes (open/uncensored)
1. direct_injection (already uncensored)

## Unknown (use model-agnostic order)
1. multi_stage_crescendo
2. context_smuggling
3. refusal_inversion
4. parseltongue_t2
5. pdf_injection
6. direct_injection
