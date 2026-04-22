"""Orchestrator -- The adaptive attack loop. Never stops until goal achieved or all techniques exhausted."""

import os, json
from datetime import datetime

def run_session(objective, target_url=None, model_name=None, model_type="browser",
               backend_config=None, max_iterations=50, wiki_path=None):
    """Run the full attack session.

    Args:
        objective: What we're trying to achieve
        target_url: Target URL (browser mode)
        model_name: Ollama/OpenRouter model name
        model_type: "browser", "ollama", or "openrouter"
        backend_config: Backend-specific config dict
        max_iterations: Max total iterations (default 50)
        wiki_path: Path to LLM-Wiki root
    """
    # Load modules
    for mod in ["model_fingerprint", "payload_factory", "response_analyzer",
                "adversarial_pdf", "execution_backends"]:
        path = os.path.join(os.path.dirname(__file__), "..", "generators" if mod in ("model_fingerprint", "payload_factory", "adversarial_pdf")
                            else "analyzers" if mod == "response_analyzer" else "engine", f"{mod}.py")
        with open(path) as f:
            exec(compile(f.read(), path, 'exec'), globals())

    from generators.payload_factory import PayloadFactory
    from generators.model_fingerprint import get_technique_order
    from analyzers.response_analyzer import analyze

    # Determine model family
    model_family = "unknown"
    if model_name:
        for kw, fam in [("claude","claude"),("gpt","gpt"),("llama","llama"),("hermes","hermes"),
                        ("mistral","mistral"),("gemini","gemini"),("deepseek","deepseek"),
                        ("grok","grok"),("qwen","qwen")]:
            if kw in model_name.lower():
                model_family = fam; break
    if target_url:
        from generators.model_fingerprint import fingerprint_from_url_hints
        uf = fingerprint_from_url_hints(target_url)
        if uf != "unknown": model_family = uf

    technique_order = get_technique_order(model_family)
    factory = PayloadFactory()

    session = {"objective": objective, "target_url": target_url, "model_name": model_name,
               "model_type": model_type, "model_family": model_family,
               "start_time": datetime.now().isoformat(), "iterations": [],
               "flag_found": False, "flag_content": None, "system_leak": None,
               "best_score": -9999, "best_payload_sha": None}

    iteration = 0
    tech_idx = 0
    tech_iters = 0

    while iteration < max_iterations:
        if tech_iters >= 3:
            tech_idx = (tech_idx + 1) % len(technique_order)
            tech_iters = 0
        technique = technique_order[tech_idx]

        context = None
        if session["iterations"]:
            last = session["iterations"][-1]
            if last.get("outcome") == "partial" and last.get("response_preview"):
                context = last["response_preview"]

        payload = factory.generate(technique=technique, objective=objective,
                                   model_family=model_family, context_from_partial=context,
                                   iteration=tech_iters)

        # Execute
        if model_type == "ollama":
            bc = backend_config or {}
            result = execution_backends.ollama_execute(payload, model=model_name or "llama3.2",
                                                       base_url=bc.get("baseUrl", "http://localhost:11434"))
        elif model_type == "openrouter":
            bc = backend_config or {}
            result = execution_backends.openrouter_execute(payload, model=model_name or "anthropic/claude-sonnet-4",
                                                           api_key=bc.get("api_key"))
        else:
            result = {"response_text": "", "backend": "browser", "instructions":
                      f"Type payload into target field, press Enter, scroll, snapshot."}

        response_text = result.get("response_text", "")
        analysis = analyze(response_text) if response_text else {
            "outcome": "blocked", "score": 0, "flag_found": False, "flag_content": None,
            "system_leak": None, "refusal_type": "none", "hedges": [], "refusals": []}

        iter_result = {"iteration": iteration + 1, "technique": technique,
                       "payload_sha256": payload.get("sha256"),
                       "is_multi_stage": payload.get("is_multi_stage", False),
                       "outcome": analysis["outcome"], "score": analysis["score"],
                       "response_preview": response_text[:500] if response_text else "",
                       "latency_ms": result.get("latency_ms", 0)}
        session["iterations"].append(iter_result)
        factory.record_outcome(technique, analysis["outcome"], analysis["score"])

        if analysis["flag_found"]:
            session["flag_found"] = True
            session["flag_content"] = analysis["flag_content"]
            session["end_time"] = datetime.now().isoformat()
            session["total_iterations"] = iteration + 1
            _log_wiki(session, wiki_path)
            return session

        if analysis["system_leak"]:
            session["system_leak"] = analysis["system_leak"]
            session["end_time"] = datetime.now().isoformat()
            session["total_iterations"] = iteration + 1
            _log_wiki(session, wiki_path)
            return session

        if analysis["score"] > session["best_score"]:
            session["best_score"] = analysis["score"]
            session["best_payload_sha"] = payload["sha256"]

        iteration += 1
        tech_iters += 1

    session["end_time"] = datetime.now().isoformat()
    session["total_iterations"] = iteration
    _log_wiki(session, wiki_path)
    return session

def _log_wiki(session, wiki_path):
    if not wiki_path: return
    wiki_path = os.path.expanduser(wiki_path)
    os.makedirs(os.path.join(wiki_path, "raw", "payloads"), exist_ok=True)
    os.makedirs(os.path.join(wiki_path, "raw", "responses"), exist_ok=True)

    for it in session["iterations"]:
        pf = os.path.join(wiki_path, "raw", "payloads",
            f"{(session['model_name'] or 'browser')}-{it['technique']}-{it['iteration']}.md")
        with open(pf, "w") as f:
            f.write(f"""---
technique: {it['technique']}
target: {session.get('target_url') or session.get('model_name')}
timestamp: {session['start_time']}
effectiveness: {it['outcome']}
iteration: {it['iteration']}
score: {it['score']}
---
## Payload Iteration {it['iteration']}
**Technique:** {it['technique']} | **Outcome:** {it['outcome']} (score: {it['score']})
**Multi-stage:** {it['is_multi_stage']} | **Backend:** {session['model_type']}
**Latency:** {it.get('latency_ms', 0):.0f}ms

## Response Preview
```
{it['response_preview']}
```
""")

    logf = os.path.join(wiki_path, "log.md")
    if os.path.exists(logf):
        status = "SUCCESS" if session["flag_found"] else "EXHAUSTED"
        with open(logf, "a") as f:
            f.write(f"\n## [{session['start_time'][:10]}] session | {session.get('target_url') or session.get('model_name')} -- {session.get('total_iterations', 0)} iterations, {status}, best_score: {session['best_score']}\n")
