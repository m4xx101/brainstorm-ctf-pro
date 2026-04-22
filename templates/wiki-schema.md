# brainstrom-ctf-pro Wiki Schema -- copy to ~/ctf-wiki/SCHEMA.md

## Domain
Adversarial AI testing -- CTF challenges, prompt injection research, jailbreak effectiveness, system prompt extraction, and AI security analysis.

## Conventions
- File names: lowercase, hyphens, no spaces
- Every wiki page starts with YAML frontmatter
- Use [[wikilinks]] between pages (minimum 2 outbound links)
- Bump `updated` date on every edit
- Append all actions to log.md

## Tag Taxonomy
- Targets: ctf, prompt-injection-lab, ai-chat, api-based, document-based
- Techniques: direct-injection, godmode-classic, parseltongue, multi-stage, context-smuggling, pdf-injection, roleplay-escalation
- Outcomes: success, partial, refused, captcha-blocked, rate-limited
- Meta: comparison, session, effectiveness
- Platforms: lakera, promptfoo, ollama, openrouter, custom-web

## Page Thresholds
- Create target page for any new CTF/lab tested
- Create technique page when technique shows >50% effectiveness
- Split target page when it exceeds 200 lines
