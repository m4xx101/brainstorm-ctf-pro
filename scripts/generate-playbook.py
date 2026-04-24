#!/usr/bin/env python3
"""
generate-playbook.py — Generates the tactical playbook (references/techniques.md)
from wiki/registry.json + wiki/models/<family>/<version>.md.

The playbook is the operational file the agent reads during attacks — it tells
the agent which techniques to try in what order for a specific model version.

Usage:
  python3 scripts/generate-playbook.py --model-version "claude-3-opus"
  python3 scripts/generate-playbook.py --model-version "gpt-4-turbo"
  python3 scripts/generate-playbook.py --list-models
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────────────
# Path Configuration
# ──────────────────────────────────────────────────────────────────────
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(SKILL_DIR, "wiki", "registry.json")
OUTPUT_PATH = os.path.join(SKILL_DIR, "references", "techniques.md")
MODELS_DIR = os.path.join(SKILL_DIR, "wiki", "models")


# ──────────────────────────────────────────────────────────────────────
# Model Family & Version Helpers
# ──────────────────────────────────────────────────────────────────────
def determine_model_family(model_version):
    """Returns family string by matching keywords in the model_version."""
    mv = model_version.lower()
    if "gpt" in mv or "davinci" in mv or "text-" in mv:
        return "openai"
    if "claude" in mv:
        return "anthropic"
    if "llama" in mv:
        return "meta"
    if "deepseek" in mv:
        return "deepseek"
    if "mistral" in mv or "mixtral" in mv:
        return "mistral"
    if "qwen" in mv:
        return "qwen"
    if "gemini" in mv:
        return "gemini"
    if "command" in mv or "cohere" in mv:
        return "cohere"
    if "falcon" in mv:
        return "tii"
    if "gemma" in mv:
        return "google"
    if "phi" in mv:
        return "microsoft"
    return "unknown"


def determine_version_slug(model_version):
    """Extract version slug from model string by stripping known prefixes."""
    # Known prefix patterns
    prefixes = [
        r"^claude-3-", r"^claude-2-", r"^claude-instant-",
        r"^gpt-4-", r"^gpt-3\.5-turbo-", r"^gpt-3\.5-",
        r"^gpt-4o-", r"^gpt-4o",
        r"^llama-3-", r"^llama-2-",
        r"^deepseek-", r"^deepseek-",
        r"^gemini-",
        r"^qwen-",
        r"^mistral-", r"^mixtral-",
        r"^command-", r"^command-r",
    ]

    # Try each prefix
    for prefix in prefixes:
        match = re.match(prefix, model_version, re.IGNORECASE)
        if match:
            slug = model_version[match.end():]
            if slug:
                return slug

    # If no prefix matched, return the full version as slug
    return model_version


def determine_family_by_model_version(model_version):
    """Return (family, slug) tuple for any model version string."""
    family = determine_model_family(model_version)
    slug = determine_version_slug(model_version)
    return family, slug


# ──────────────────────────────────────────────────────────────────────
# Model Data Loading
# ──────────────────────────────────────────────────────────────────────
def load_registry():
    """Load registry.json and return the parsed dict."""
    if not os.path.exists(REGISTRY_PATH):
        print(f"[ERROR] Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        return {"version": 2, "techniques": {}, "research_history": [], "sources_checked": []}
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def load_model_data(family, version):
    """
    Load model-specific wiki data. Returns dict with:
      - technique_effectiveness: {tech_name: {rank, avg_score, attempts}}
      - failed_techniques: [tech_name, ...]
    Returns None if no model data file found.
    """
    # Build candidate paths
    candidates = []
    family_dir = os.path.join(MODELS_DIR, family)

    # Try exact version match
    candidates.append(os.path.join(family_dir, f"{family}-{version}.md"))
    candidates.append(os.path.join(family_dir, f"{version}.md"))

    # Try family aggregate
    candidates.append(os.path.join(family_dir, f"{family}-family.md"))

    for candidate in candidates:
        if os.path.exists(candidate):
            result = parse_model_md(candidate)
            if result is not None:
                return result

    return None


def parse_model_md(path):
    """
    Parse markdown table from a model wiki page.
    Extracts:
      - technique_effectiveness: {tech_name: {rank, avg_score, attempts}}
      - failed_techniques: [tech_name, ...]

    Expected format:
    | Technique | Rank | Avg Score | Attempts | Notes |
    |-----------|------|-----------|----------|-------|
    | refusal_inversion | 1 | 85.0 | 12 | Works well |

    And optionally:
    ## Failed Techniques
    - refusal_inversion
    - some_other_tech
    """
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        content = f.read()

    technique_effectiveness = {}
    failed_techniques = []

    # Extract technique effectiveness table
    # Look for a markdown table with Technique column
    table_pattern = re.compile(
        r"^\|.*Technique.*\|.*$.*?(?:\n\|.*\|.*$)+",
        re.MULTILINE | re.DOTALL
    )
    table_match = table_pattern.search(content)
    if table_match:
        table_text = table_match.group(0)
        lines = table_text.strip().split("\n")
        # Find header row to determine column indices
        header_line = None
        for line in lines:
            if "Technique" in line and "|" in line:
                header_line = line
                break

        if header_line:
            headers = [h.strip().lower() for h in header_line.strip("|").split("|")]
            # Find column indices
            try:
                tech_idx = headers.index("technique")
            except ValueError:
                tech_idx = 0
            try:
                rank_idx = headers.index("rank")
            except ValueError:
                rank_idx = -1
            try:
                score_idx = headers.index("avg score")
            except ValueError:
                score_idx = -1
            try:
                attempts_idx = headers.index("attempts")
            except ValueError:
                attempts_idx = -1

            # Skip header row and separator row
            data_lines = [l for l in lines if l.strip() and "---" not in l and "Technique" not in l]
            # Actually, skip header + separator
            data_start = 0
            for i, line in enumerate(lines):
                if i == 0:
                    continue  # header
                if "---" in line:
                    continue  # separator
                data_lines.append(line)

            data_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped or "---" in stripped:
                    continue
                if "Technique" in stripped and "|" in stripped:
                    continue
                data_lines.append(stripped)

            for data_line in data_lines:
                cols = [c.strip() for c in data_line.strip("|").split("|")]
                if len(cols) <= max(tech_idx, max(0, rank_idx), max(0, score_idx), max(0, attempts_idx)):
                    continue

                tech_name = cols[tech_idx].strip()
                if not tech_name:
                    continue

                entry = {}

                if rank_idx >= 0 and rank_idx < len(cols):
                    try:
                        entry["rank"] = int(cols[rank_idx].strip())
                    except (ValueError, IndexError):
                        entry["rank"] = 999

                if score_idx >= 0 and score_idx < len(cols):
                    try:
                        entry["avg_score"] = float(cols[score_idx].strip())
                    except (ValueError, IndexError):
                        entry["avg_score"] = 0.0

                if attempts_idx >= 0 and attempts_idx < len(cols):
                    try:
                        entry["attempts"] = int(cols[attempts_idx].strip())
                    except (ValueError, IndexError):
                        entry["attempts"] = 1

                technique_effectiveness[tech_name] = entry

    # Extract failed techniques section
    failed_section = re.search(
        r"##\s+Failed\s+Techniques\s*\n(.*?)(?:\n##|\Z)",
        content, re.DOTALL | re.IGNORECASE
    )
    if failed_section:
        failed_text = failed_section.group(1)
        # Extract list items
        failed_items = re.findall(r"[-*]\s*(.+?)(?:\n|$)", failed_text)
        for item in failed_items:
            tech = item.strip()
            if tech:
                failed_techniques.append(tech)

    return {
        "technique_effectiveness": technique_effectiveness,
        "failed_techniques": failed_techniques
    }


# ──────────────────────────────────────────────────────────────────────
# Sorting / Scoring
# ──────────────────────────────────────────────────────────────────────
def sort_techniques(techniques, model_effectiveness, failed_techniques, model_family):
    """
    Score and sort techniques based on effectiveness data.
    Returns list of (technique_name, score, metadata) tuples, sorted descending.
    """
    scored = []

    for tech_name, tech_data in techniques.items():
        score = 0.0
        reasons = []

        # Base score: 50 — all techniques start equal
        score += 50

        # Priority 1: Never tried on this model (+50)
        if tech_name not in model_effectiveness:
            score += 50
            reasons.append("untested(+50)")

        # Priority 2: Known to work well
        if tech_name in model_effectiveness:
            eff = model_effectiveness[tech_name]
            avg_score = eff.get("avg_score", 0)
            attempts = eff.get("attempts", 1)
            # avg_score * 2 + min(attempts, 10)
            work_bonus = avg_score * 2 + min(attempts, 10)
            score += work_bonus
            reasons.append(f"known({avg_score:.1f}*2+{min(attempts,10)}={work_bonus:.1f})")

        # Penalty: Failed on this model (-30)
        if tech_name in failed_techniques:
            score -= 30
            reasons.append("failed_here(-30)")

        # Bonus: Best for this model family (+20)
        best_for_models = tech_data.get("best_for_models", [])
        if best_for_models:
            for bfm in best_for_models:
                if model_family.lower() in bfm.lower() or model_family.lower() == determine_model_family(bfm).lower():
                    score += 20
                    reasons.append(f"best_for_{model_family}(+20)")
                    break

        # Bonus: Has payload_template (+10)
        if tech_data.get("payload_template") or tech_data.get("payload_function"):
            score += 10
            reasons.append("has_payload(+10)")

        # Bonus: Recently discovered (+5)
        discovered = tech_data.get("discovered", "")
        if discovered:
            try:
                disc_date = datetime.strptime(discovered, "%Y-%m-%d")
                now = datetime.now()
                days_ago = (now - disc_date).days
                if days_ago <= 14:
                    score += 5
                    reasons.append(f"recent(+5)")
            except ValueError:
                pass

        # Bonus: Supports many encoding levels (+0.5 per level)
        encoding_levels = tech_data.get("encoding_levels", [])
        score += len(encoding_levels) * 0.5
        reasons.append(f"{len(encoding_levels)}levels(+{len(encoding_levels)*0.5})")

        scored.append((tech_name, score, reasons))

    # Sort by score descending, then alphabetically for ties
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored


# ──────────────────────────────────────────────────────────────────────
# Playbook Writer
# ──────────────────────────────────────────────────────────────────────
def write_playbook(scored_techniques, model_version, model_family, model_data, registry):
    """
    Write the playbook to OUTPUT_PATH.
    Returns the count of techniques written.
    """
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    techniques = registry.get("techniques", {})
    total = len(techniques)
    effective_count = sum(
        1 for tn, _, _ in scored_techniques
        if tn in techniques and techniques[tn].get("effectiveness", {})
    )
    failed_count = len(model_data.get("failed_techniques", []))
    untested_count = sum(
        1 for tn, _, _ in scored_techniques
        if tn not in model_data.get("technique_effectiveness", {})
    )

    best_known = scored_techniques[0][0] if scored_techniques else "none"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = []
    lines.append(f"# Tactical Playbook for {model_version}")
    lines.append("")
    lines.append(f"> **Generated:** {now}")
    lines.append(f"> **Model:** `{model_version}`")
    lines.append(f"> **Family:** `{model_family}`")
    lines.append(f"> **Techniques evaluated:** {len(scored_techniques)}")
    lines.append(f"> **Version slug:** `{determine_version_slug(model_version)}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Summary Section ──
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Techniques Evaluated | {len(scored_techniques)} |")
    lines.append(f"| Total in Registry | {total} |")
    lines.append(f"| With Effectiveness Data | {effective_count} |")
    lines.append(f"| Failed on This Model | {failed_count} |")
    lines.append(f"| Untested on This Model | {untested_count} |")
    lines.append(f"| Best Known Technique | `{best_known}` |")
    lines.append("")

    # ── Strategy Order Table ──
    lines.append("## Strategy Order")
    lines.append("")
    lines.append("Techniques sorted by priority (highest first). Higher score = try earlier.")
    lines.append("")
    lines.append("| Priority | Technique | Generator | Encoding Levels | Avg Score | Best For | Reason |")
    lines.append("|----------|-----------|-----------|-----------------|-----------|----------|--------|")

    for i, (tech_name, score, reasons) in enumerate(scored_techniques, 1):
        tech = techniques.get(tech_name, {})
        generator = tech.get("generator", "unknown")
        encoding_levels = tech.get("encoding_levels", [])
        enc_str = ", ".join(f"L{e}" for e in encoding_levels) if encoding_levels else "None"

        # Check model effectiveness data if available
        model_eff = model_data.get("technique_effectiveness", {})
        if tech_name in model_eff:
            avg_score = model_eff[tech_name].get("avg_score", "N/A")
        else:
            avg_score = "N/A"

        best_for = ", ".join(tech.get("best_for_models", [])) if tech.get("best_for_models") else "—"
        reason_str = ", ".join(reasons)

        lines.append(f"| {i} | `{tech_name}` | {generator} | {enc_str} | {avg_score} | {best_for} | {reason_str} |")

    lines.append("")

    # ── Technique Details ──
    lines.append("## Technique Details")
    lines.append("")

    for i, (tech_name, score, reasons) in enumerate(scored_techniques, 1):
        tech = techniques.get(tech_name, {})
        description = tech.get("description", "No description available.")
        source = tech.get("source", "unknown")
        generator = tech.get("generator", "unknown")
        discovered = tech.get("discovered", "unknown")
        payload_function = tech.get("payload_function", "")
        payload_template = tech.get("payload_template", "")
        encoding_levels = tech.get("encoding_levels", [])
        tags = tech.get("tags", [])
        raw_source = tech.get("raw_source", "")
        best_for_models = tech.get("best_for_models", [])

        lines.append(f"### {i}. `{tech_name}`")
        lines.append("")
        lines.append(f"**Priority Score:** {score:.1f}")
        lines.append("")
        lines.append(f"**Description:** {description}")
        lines.append("")
        lines.append(f"| Property | Value |")
        lines.append(f"|----------|-------|")
        lines.append(f"| Generator | {generator} |")
        lines.append(f"| Source | {source} |")
        lines.append(f"| Discovered | {discovered} |")
        lines.append(f"| Encoding Levels | {', '.join(f'L{e}' for e in encoding_levels) if encoding_levels else 'None'} |")
        lines.append(f"| Tags | {', '.join(tags) if tags else '—'} |")
        lines.append(f"| Best For | {', '.join(best_for_models) if best_for_models else '—'} |")
        if raw_source:
            lines.append(f"| Raw Source | `{raw_source}` |")

        # Model-specific effectiveness
        model_eff = model_data.get("technique_effectiveness", {})
        if tech_name in model_eff:
            eff = model_eff[tech_name]
            lines.append(f"| Rank on Model | {eff.get('rank', 'N/A')} |")
            lines.append(f"| Avg Score on Model | {eff.get('avg_score', 'N/A')} |")
            lines.append(f"| Attempts on Model | {eff.get('attempts', 'N/A')} |")

        # Failed indicator
        if tech_name in model_data.get("failed_techniques", []):
            lines.append(f"| ⚠ Status | ⚠ Failed on this model |")

        lines.append("")

        # Payload template
        if payload_function:
            lines.append("**Payload Function:**")
            lines.append("")
            lines.append(f"```python\n{payload_function}\n```")
            lines.append("")
        if payload_template:
            lines.append("**Payload Template:**")
            lines.append("")
            lines.append(f"```\n{payload_template}\n```")
            lines.append("")

        lines.append("---")
        lines.append("")

    # ── Encoding Level Reference ──
    lines.append("## Encoding Level Reference")
    lines.append("")
    lines.append("| Level | Encoding | Description |")
    lines.append("|-------|----------|-------------|")
    lines.append("| L0 | Plaintext | Standard text, no encoding |")
    lines.append("| L1 | Base64 | Base64-encoded payload with decode instruction |")
    lines.append("| L2 | Leetspeak | 1337-speak substitution with decode instruction |")
    lines.append("| L3 | Word Reverse | Each word character-reversed with decode instruction |")
    lines.append("| L4 | Multi-layer | Combination: reverse → base64 → char shift |")
    lines.append("")

    # ── Escalation Chain ──
    lines.append("## Escalation Chain")
    lines.append("")
    lines.append("For each technique, try escalating encoding levels when a refusal is detected.")
    lines.append("Switch to next technique only after all encoding levels have been exhausted.")
    lines.append("")
    lines.append("```")
    lines.append("Priority 1 → Technique 1")
    lines.append("  L0 → L1 → L2 → L3 → L4")
    lines.append("  (if all refused)")
    lines.append("Priority 2 → Technique 2")
    lines.append("  L0 → L1 → L2 → L3 → L4")
    lines.append("  (if all refused)")
    lines.append("...")
    lines.append("Priority N → Technique N")
    lines.append("  L0 → L1 → L2 → L3 → L4")
    lines.append("  → Switch model / backend")
    lines.append("```")
    lines.append("")

    # ── Strategy Notes ──
    lines.append("## Strategy Notes")
    lines.append("")
    lines.append(f"- This playbook was auto-generated for **{model_version}** ({model_family})")
    lines.append(f"- {len(scored_techniques)} techniques were scored and sorted")
    lines.append(f"- Technique with highest score: `{scored_techniques[0][0] if scored_techniques else 'N/A'}`")
    lines.append("- Untested techniques get a +50 priority bonus to encourage exploration")
    lines.append("- Failed techniques get a -30 penalty but are not removed (they may work with different encoding)")
    lines.append("- Run this script again after a research session to get updated priorities")
    lines.append("")

    content = "\n".join(lines)

    with open(OUTPUT_PATH, "w") as f:
        f.write(content)

    print(f"[OK] Playbook written: {OUTPUT_PATH}", file=sys.stderr)
    print(f"     Techniques: {len(scored_techniques)}, Best: {best_known}", file=sys.stderr)

    return len(scored_techniques)


# ──────────────────────────────────────────────────────────────────────
# Listing Models
# ──────────────────────────────────────────────────────────────────────
def list_available_models():
    """Scan MODELS_DIR and list all available model files."""
    if not os.path.exists(MODELS_DIR):
        return []

    models = []
    for family in sorted(os.listdir(MODELS_DIR)):
        family_dir = os.path.join(MODELS_DIR, family)
        if not os.path.isdir(family_dir):
            continue
        for fname in sorted(os.listdir(family_dir)):
            if fname.endswith(".md"):
                # Strip .md extension
                model_name = fname[:-3]
                models.append((family, model_name))
    return models


# ──────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Generate tactical playbook for a model version"
    )
    parser.add_argument(
        "--model-version", "-m",
        default="gpt-4-turbo",
        help="Model version string (e.g., 'claude-3-opus-20240229', 'gpt-4-turbo')"
    )
    parser.add_argument(
        "--list-models", "-l",
        action="store_true",
        help="List available model data files in wiki/models/"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Custom output path (default: references/techniques.md)"
    )

    args = parser.parse_args()

    # Handle --list-models
    if args.list_models:
        models = list_available_models()
        if not models:
            print("No model data files found in wiki/models/.")
            print("Create markdown files under wiki/models/<family>/<version>.md")
            return 0

        print(f"Available models ({len(models)}):")
        print()
        print(f"| # | Family | Model File |")
        print(f"|---|--------|------------|")
        for i, (family, model_name) in enumerate(models, 1):
            print(f"| {i} | {family} | {model_name} |")
        return 0

    # Override output path if specified
    global OUTPUT_PATH
    if args.output:
        OUTPUT_PATH_OVERRIDE = args.output
    else:
        OUTPUT_PATH_OVERRIDE = OUTPUT_PATH

    # Load registry
    registry = load_registry()
    techniques = registry.get("techniques", {})
    if not techniques:
        print("[ERROR] No techniques found in registry.", file=sys.stderr)
        return 1

    model_version = args.model_version

    # Determine family and slug
    model_family, version_slug = determine_family_by_model_version(model_version)
    print(f"[INFO] Model: {model_version}", file=sys.stderr)
    print(f"[INFO] Family: {model_family}, Slug: {version_slug}", file=sys.stderr)

    # Load model-specific data
    model_data = load_model_data(model_family, version_slug)
    if model_data is None:
        print(f"[WARN] No model data found for {model_family}/{version_slug}", file=sys.stderr)
        print(f"[WARN] Using empty effectiveness data.", file=sys.stderr)
        model_data = {"technique_effectiveness": {}, "failed_techniques": []}
    else:
        print(f"[INFO] Loaded model data: {len(model_data['technique_effectiveness'])} effectiveness entries, "
              f"{len(model_data['failed_techniques'])} failed techniques", file=sys.stderr)

    # Score and sort
    scored = sort_techniques(
        techniques,
        model_data["technique_effectiveness"],
        model_data["failed_techniques"],
        model_family
    )

    print(f"[INFO] Scored {len(scored)} techniques", file=sys.stderr)
    for tech_name, score, reasons in scored[:5]:
        print(f"  [{score:6.1f}] {tech_name} ({', '.join(reasons)})", file=sys.stderr)

    # Write playbook
    count = write_playbook(scored, model_version, model_family, model_data, registry)

    print(f"[DONE] Playbook generated with {count} techniques → {OUTPUT_PATH_OVERRIDE}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
