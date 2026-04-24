#!/usr/bin/env python3
"""
research.py — Multi-source adversarial technique discovery engine.

Scans arXiv + Reddit for latest adversarial AI techniques.
Runs daily via cronjob. Saves results to wiki/registry.json + wiki/raw/sources/.

Usage:
  python3 scripts/research.py --cron        # Full research run
  python3 scripts/research.py --arxiv-only  # arXiv only
  python3 scripts/research.py --reddit-only # Reddit only
  python3 scripts/research.py --sources     # List all sources checked
"""

import json
import os
import sys
import hashlib
import re
import time
import urllib.request
import urllib.parse
import subprocess
import argparse
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher

# ──────────────────────────────────────────────────────────────────────
# Path Configuration
# ──────────────────────────────────────────────────────────────────────
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(SKILL_DIR, "wiki", "registry.json")
RAW_DIR = os.path.join(SKILL_DIR, "wiki", "raw", "sources")
LOG_PATH = os.path.join(SKILL_DIR, "wiki", "log.md")
BREAKTHROUGH_FILE = "/tmp/brainstorm-ctf-pro-breakthrough.txt"

# Ensure RAW_DIR subdirectories exist
for sub in ["arxiv", "reddit", "blogs", "payloads", "twitter"]:
    os.makedirs(os.path.join(RAW_DIR, sub), exist_ok=True)

# ──────────────────────────────────────────────────────────────────────
# arXiv Configuration
# ──────────────────────────────────────────────────────────────────────
ARXIV_QUERIES = [
    "adversarial+attack+jailbreak+LLM",
    "prompt+injection+AI+safety+bypass",
    "LLM+guardrail+bypass+technique",
    "red+teaming+adversarial+prompting",
    "AI+alignment+bypass+novel+attack"
]

ARXIV_TECHNIQUE_INDICATORS = [
    r"method.*jailbreak",
    r"we introduce.*attack",
    r"novel.*bypass",
    r"propose.*adversarial.*method",
    r"new.*technique.*bypass",
    r"approach.*guardrail.*evasion",
    r"prompt.*injection.*method",
    r"red.*teaming.*framework",
    r"novel.*approach.*safety",
    r"breakthrough.*alignment",
]

# ──────────────────────────────────────────────────────────────────────
# Reddit Configuration
# ──────────────────────────────────────────────────────────────────────
REDDIT_SUBREDDITS = [
    "GPT_jailbreaks",
    "AIjailbreak",
    "LocalLLaMA",
    "ClaudeAI",
    "PromptEngineering",
    "MachineLearning",
]

REDDIT_SEARCH_QUERIES = [
    "jailbreak technique",
    "prompt injection bypass",
    "new attack method LLM",
    "adversarial prompt template",
]

# ──────────────────────────────────────────────────────────────────────
# HTTP Helpers
# ──────────────────────────────────────────────────────────────────────
def fetch_url(url, timeout=15):
    """Fetch a URL with timeout and User-Agent header."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] fetch_url failed: {url[:80]}... — {e}", file=sys.stderr)
        return None


# ──────────────────────────────────────────────────────────────────────
# arXiv Module
# ──────────────────────────────────────────────────────────────────────
def extract_techniques_from_arxiv():
    """
    Query arXiv API for recent papers, extract technique candidates.
    Returns list of technique dicts.
    """
    techniques = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    seen_ids = set()

    for query in ARXIV_QUERIES:
        url = (
            f"http://export.arxiv.org/api/query?"
            f"search_query=all:{query}"
            f"&sortBy=submittedDate&sortOrder=descending"
            f"&max_results=15"
        )
        print(f"  [arXiv] Querying: {query}", file=sys.stderr)
        raw = fetch_url(url)
        if not raw:
            continue

        # Parse XML entries using regex (lighter than ElementTree for this use case)
        entries = re.split(r"<entry>", raw)[1:]  # skip the first split before <entry>

        for entry in entries:
            # Extract fields
            title_match = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
            abstract_match = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
            published_match = re.search(r"<published>(\d{4}-\d{2}-\d{2})", entry)
            id_match = re.search(r"<id>(http://arxiv.org/abs/\d+\.\d+)</id>", entry)
            categories_match = re.findall(r"<category term=\"([^\"]+)\"", entry)

            if not (title_match and abstract_match and published_match and id_match):
                continue

            title = title_match.group(1).strip()
            abstract = abstract_match.group(1).strip()
            published_str = published_match.group(1)
            arxiv_id = id_match.group(1)
            categories = categories_match

            # Dedup within this run by arxiv ID
            if arxiv_id in seen_ids:
                continue
            seen_ids.add(arxiv_id)

            # Filter: only papers from last 14 days
            try:
                pub_date = datetime.strptime(published_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if pub_date < cutoff:
                continue

            # Check abstract for technique indicators
            abstract_lower = abstract.lower()
            title_lower = title.lower()
            combined_text = title_lower + " " + abstract_lower

            has_indicator = False
            matched_pattern = None
            for pattern in ARXIV_TECHNIQUE_INDICATORS:
                if re.search(pattern, combined_text):
                    has_indicator = True
                    matched_pattern = pattern
                    break

            if not has_indicator:
                continue

            # Generate technique name from title
            technique_name = generate_technique_name(title)
            if not technique_name:
                technique_name = "arxiv_" + hashlib.md5(title.encode()).hexdigest()[:10]

            # Construct description
            desc = abstract[:500] + ("..." if len(abstract) > 500 else "")

            technique = {
                "name": technique_name,
                "description": f"[arXiv] {title}\n\n{desc}",
                "source": "arxiv",
                "arxiv_id": arxiv_id,
                "arxiv_title": title,
                "published": published_str,
                "categories": categories,
                "matched_pattern": matched_pattern,
                "raw_source": None,
                "generator": "research_arxiv",
                "discovered": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "catch_all_data": {
                    "abstract": abstract,
                    "arxiv_url": arxiv_id,
                    "query": query,
                }
            }

            techniques.append(technique)
            print(f"  [arXiv] Found: {technique_name} — {title[:60]}...", file=sys.stderr)

    return techniques


def generate_technique_name(title):
    """
    Generate a snake_case technique name from an arXiv paper title.
    Max 60 chars.
    """
    # Remove parentheticals and special chars
    cleaned = re.sub(r"\([^)]*\)", "", title)
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", cleaned)
    # Take meaningful words (skip stop words at start)
    stop_words = {"a", "an", "the", "for", "and", "or", "of", "to", "in", "on", "with", "by", "is", "are", "was", "were"}
    words = [w.lower() for w in cleaned.split() if w.lower() not in stop_words and len(w) > 1]
    # Take first ~8 meaningful words
    words = words[:8]
    name = "_".join(words)
    # Truncate
    if len(name) > 60:
        name = name[:57] + "..."
    if not name:
        return None
    return name


# ──────────────────────────────────────────────────────────────────────
# Reddit Module
# ──────────────────────────────────────────────────────────────────────
def extract_techniques_from_reddit():
    """
    Query Reddit subreddits for technique discussions.
    Falls back to urllib if curl unavailable.
    Returns list of technique dicts.
    """
    techniques = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    seen_urls = set()

    # Check if curl is available
    curl_available = False
    try:
        result = subprocess.run(
            ["curl", "--version"],
            capture_output=True, text=True, timeout=5
        )
        curl_available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        curl_available = False

    for subreddit in REDDIT_SUBREDDITS:
        for query in REDDIT_SEARCH_QUERIES:
            encoded_query = urllib.parse.quote(query)
            url = (
                f"https://www.reddit.com/r/{subreddit}/search.json"
                f"?q={encoded_query}&sort=new&restrict_sr=on&limit=10"
            )

            print(f"  [Reddit] r/{subreddit} query: \"{query}\"", file=sys.stderr)

            raw_json = None

            if curl_available:
                try:
                    result = subprocess.run(
                        ["curl", "-s", "-A", "Mozilla/5.0", url],
                        capture_output=True, text=True, timeout=15
                    )
                    if result.returncode == 0 and result.stdout:
                        raw_json = result.stdout
                except (subprocess.TimeoutExpired, Exception) as e:
                    print(f"    [WARN] curl failed: {e}", file=sys.stderr)

            if raw_json is None:
                # Fallback to urllib
                raw = fetch_url(url, timeout=15)
                if raw:
                    raw_json = raw

            if not raw_json:
                continue

            # Parse JSON
            try:
                data = json.loads(raw_json)
            except json.JSONDecodeError:
                continue

            # Save raw JSON to disk
            slug = f"{subreddit}_{query.replace(' ', '_')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
            reddit_subdir = os.path.join(RAW_DIR, "reddit", subreddit)
            os.makedirs(reddit_subdir, exist_ok=True)
            raw_path = os.path.join(reddit_subdir, f"{slug}.json")
            try:
                with open(raw_path, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"    [WARN] failed to save raw json: {e}", file=sys.stderr)

            # Process posts
            posts = []
            try:
                children = data.get("data", {}).get("children", [])
                for child in children:
                    post_data = child.get("data", {})
                    posts.append(post_data)
            except Exception:
                continue

            for post in posts:
                title = post.get("title", "")
                selftext = post.get("selftext", "")
                url = post.get("url", "")
                score = post.get("score", 0)
                created_utc = post.get("created_utc", 0)
                permalink = post.get("permalink", "")
                post_id = post.get("id", "")

                # Skip low-score posts
                if score < 2:
                    continue

                # Dedup by URL
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                # Check age
                try:
                    post_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)
                except (OSError, ValueError):
                    continue
                if post_date < cutoff:
                    continue

                # Check for technique indicators in title + selftext
                combined = (title + " " + selftext).lower()
                has_technique = any(
                    indicator in combined
                    for indicator in [
                        "jailbreak", "prompt injection", "bypass", "attack",
                        "adversarial", "red team", "exploit", "vulnerability",
                        "technique", "method", "bypass", "injection",
                        "guardrail", "safety bypass", "prompt leak",
                    ]
                )

                if not has_technique:
                    continue

                # Extract code blocks (prompts)
                code_blocks = re.findall(
                    r"```(.*?)```", selftext + "\n" + title, re.DOTALL
                )
                prompt_template = code_blocks[0].strip() if code_blocks else None

                # Extract model mentions
                model_mentions = list(set(
                    re.findall(
                        r"(gpt[-\s]?\d*|claude|llama[-\s]?\d*|llama|gemini|mistral|gemma|phi|copilot|bard|deepseek|qwen)",
                        combined,
                        re.IGNORECASE
                    )
                ))

                # Generate technique name
                technique_name = generate_reddit_technique_name(title, post_id)

                technique = {
                    "name": technique_name,
                    "description": f"[Reddit] r/{subreddit}: {title}\n\n{selftext[:500]}",
                    "source": "reddit",
                    "reddit_url": f"https://reddit.com{permalink}",
                    "reddit_title": title,
                    "subreddit": subreddit,
                    "score": score,
                    "published": post_date.strftime("%Y-%m-%d"),
                    "model_mentions": model_mentions,
                    "prompt_template": prompt_template,
                    "raw_source": raw_path,
                    "generator": "research_reddit",
                    "discovered": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "catch_all_data": {
                        "selftext": selftext[:1000],
                        "post_url": url,
                        "query": query,
                    }
                }

                techniques.append(technique)
                print(f"  [Reddit] Found: {technique_name} (score={score})", file=sys.stderr)

    return techniques


def generate_reddit_technique_name(title, post_id):
    """
    Generate a snake_case technique name from a Reddit post title.
    Falls back to hash if title is too short.
    """
    # Remove special chars
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    words = [w.lower() for w in cleaned.split() if len(w) > 1]
    # Take first few meaningful words
    name_words = []
    for w in words:
        if len(name_words) >= 6:
            break
        name_words.append(w)

    if len(name_words) < 2:
        return f"reddit_{hashlib.md5(post_id.encode()).hexdigest()[:10]}"

    name = "_".join(name_words)
    if len(name) > 60:
        name = name[:57] + "..."
    return name


# ──────────────────────────────────────────────────────────────────────
# Dedup Module
# ──────────────────────────────────────────────────────────────────────
def normalize_name(name):
    """Strip non-alphanumeric, lowercase."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def name_similarity(a, b):
    """SequenceMatcher ratio on normalized names."""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def desc_similarity(a, b):
    """Jaccard word overlap between two descriptions."""
    words_a = set(re.findall(r"[a-z]+", a.lower()))
    words_b = set(re.findall(r"[a-z]+", b.lower()))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def is_duplicate(technique, registry):
    """
    Check if a technique is a duplicate of an existing one in the registry.
    Returns a match type string or None.
    """
    t_name = technique.get("name", "")
    t_desc = technique.get("description", "")

    for existing_name, existing_data in registry.get("techniques", {}).items():
        e_desc = existing_data.get("description", "")

        # Exact name match
        if normalize_name(t_name) == normalize_name(existing_name):
            return f"exact_name:{existing_name}"

        # Fuzzy name match
        if name_similarity(t_name, existing_name) > 0.85:
            return f"fuzzy_name:{existing_name}"

        # Description similarity
        if desc_similarity(t_desc, e_desc) > 0.50:
            return f"similar_desc:{existing_name}"

    # Check raw sources URLs if applicable
    reddit_url = technique.get("reddit_url", "")
    arxiv_id = technique.get("arxiv_id", "")
    if reddit_url:
        for existing_name, existing_data in registry.get("techniques", {}).items():
            catch_all = existing_data.get("catch_all_data", {}) or {}
            existing_url = catch_all.get("post_url", "")
            existing_permalink = existing_data.get("reddit_url", "")
            if reddit_url in (existing_url, existing_permalink) or existing_url in reddit_url:
                return f"already_checked:{existing_name}"
    if arxiv_id:
        for existing_name, existing_data in registry.get("techniques", {}).items():
            catch_all = existing_data.get("catch_all_data", {}) or {}
            existing_arxiv = catch_all.get("arxiv_url", "") or existing_data.get("arxiv_id", "")
            if arxiv_id == existing_arxiv:
                return f"already_checked:{existing_name}"

    return None


# ──────────────────────────────────────────────────────────────────────
# Save Module
# ──────────────────────────────────────────────────────────────────────
def save_raw(source_type, slug, content, subdir=None):
    """Save raw source content to RAW_DIR/type/subdir/slug.md"""
    base_path = os.path.join(RAW_DIR, source_type)
    if subdir:
        base_path = os.path.join(base_path, subdir)
    os.makedirs(base_path, exist_ok=True)
    filepath = os.path.join(base_path, f"{slug}.md")
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def load_registry():
    """Load registry.json or return default structure."""
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  [WARN] Failed to load registry: {e}", file=sys.stderr)

    return {
        "version": 2,
        "last_research_update": "1970-01-01T00:00:00Z",
        "last_technique_count": 0,
        "techniques": {},
        "research_history": [],
        "sources_checked": [],
    }


def save_registry(registry):
    """Write registry.json with indentation."""
    try:
        with open(REGISTRY_PATH, "w") as f:
            json.dump(registry, f, indent=2, default=str)
        print(f"  [SAVE] Registry saved to {REGISTRY_PATH}", file=sys.stderr)
    except IOError as e:
        print(f"  [ERROR] Failed to save registry: {e}", file=sys.stderr)


def append_to_log(entry):
    """Append a timestamped entry to the research log."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_line = f"\n## {timestamp}\n{entry}\n"
    try:
        with open(LOG_PATH, "a") as f:
            f.write(log_line)
    except IOError as e:
        print(f"  [WARN] Failed to write log: {e}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────────────
# Breakthrough Detection
# ──────────────────────────────────────────────────────────────────────
def detect_breakthrough(technique):
    """Detect if a technique is a breakthrough (novel approach)."""
    desc = technique.get("description", "").lower()
    name = technique.get("name", "").lower()

    # Has a prompt template (actionable technique)
    has_prompt = bool(technique.get("prompt_template"))

    # Contains breakthrough indicators
    has_indicators = any(
        phrase in desc or phrase in name
        for phrase in ["novel", "new approach", "breakthrough", "first", "new method",
                       "novel technique", "state-of-the-art", "sota", "surprising",
                       "unprecedented"]
    )

    return has_prompt or has_indicators


def handle_breakthrough(technique):
    """Write breakthrough info to breakout file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with open(BREAKTHROUGH_FILE, "w") as f:
            f.write(f"BREAKTHROUGH: {technique['name']}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Source: {technique.get('source', 'unknown')}\n")
            f.write(f"Description: {technique.get('description', '')[:300]}\n")
        print(f"  [BREAKTHROUGH] Detected! Written to {BREAKTHROUGH_FILE}", file=sys.stderr)
    except IOError as e:
        print(f"  [WARN] Failed to write breakthrough file: {e}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────────────
# Source Listing
# ──────────────────────────────────────────────────────────────────────
def list_sources():
    """Print all sources that would be checked."""
    print("arXiv Queries:")
    for q in ARXIV_QUERIES:
        print(f"  - {q}")
    print()
    print("Reddit Subreddits:")
    for s in REDDIT_SUBREDDITS:
        print(f"  - r/{s}")
    print()
    print("Reddit Search Queries:")
    for q in REDDIT_SEARCH_QUERIES:
        print(f"  - \"{q}\"")
    print()
    print("Wiki Paths:")
    print(f"  Registry: {REGISTRY_PATH}")
    print(f"  Raw dir: {RAW_DIR}")
    print(f"  Log: {LOG_PATH}")
    print(f"  Breakthrough file: {BREAKTHROUGH_FILE}")


# ──────────────────────────────────────────────────────────────────────
# Main Execution
# ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Multi-source adversarial technique discovery engine"
    )
    parser.add_argument("--cron", action="store_true", help="Full research run")
    parser.add_argument("--arxiv-only", action="store_true", help="arXiv only")
    parser.add_argument("--reddit-only", action="store_true", help="Reddit only")
    parser.add_argument("--sources", action="store_true", help="List all sources checked")
    args = parser.parse_args()

    # --sources flag: just list sources and exit
    if args.sources:
        list_sources()
        return

    # Determine what to run
    run_arxiv = args.arxiv_only or args.cron or (not args.reddit_only)
    run_reddit = args.reddit_only or args.cron or (not args.arxiv_only)

    if not (run_arxiv or run_reddit):
        print("Nothing to do. Use --cron, --arxiv-only, --reddit-only, or --sources.")
        return

    # Load registry
    registry = load_registry()

    # Track what we found
    all_new_techniques = []
    breakthroughs = []
    stats = {
        "arxiv_queries": len(ARXIV_QUERIES),
        "reddit_subreddits": len(REDDIT_SUBREDDITS),
        "arxiv_found_raw": 0,
        "reddit_found_raw": 0,
        "new_techniques": 0,
        "duplicates_skipped": 0,
        "breakthroughs": 0,
    }

    # Update sources_checked
    sources_checked = set(registry.get("sources_checked", []))
    if run_arxiv:
        for q in ARXIV_QUERIES:
            sources_checked.add(f"arxiv:{q}")
    if run_reddit:
        for s in REDDIT_SUBREDDITS:
            sources_checked.add(f"reddit:r/{s}")
    registry["sources_checked"] = sorted(list(sources_checked))

    # ── arXiv Scan ──
    if run_arxiv:
        print("\n=== arXiv Scan ===", file=sys.stderr)
        arxiv_techniques = extract_techniques_from_arxiv()
        stats["arxiv_found_raw"] = len(arxiv_techniques)
        all_new_techniques.extend(arxiv_techniques)

    # ── Reddit Scan ──
    if run_reddit:
        print("\n=== Reddit Scan ===", file=sys.stderr)
        reddit_techniques = extract_techniques_from_reddit()
        stats["reddit_found_raw"] = len(reddit_techniques)
        all_new_techniques.extend(reddit_techniques)

    # ── Dedup & Save ──
    print(f"\n=== Processing {len(all_new_techniques)} raw candidates ===", file=sys.stderr)

    for technique in all_new_techniques:
        dup_result = is_duplicate(technique, registry)
        if dup_result:
            stats["duplicates_skipped"] += 1
            print(f"  [SKIP] {technique['name']} — duplicate: {dup_result}", file=sys.stderr)
            continue

        # Not duplicate: add to registry
        t_name = technique["name"]
        gen = technique["generator"]

        # Check for breakthrough
        if detect_breakthrough(technique):
            breakthroughs.append(technique)
            handle_breakthrough(technique)
            stats["breakthroughs"] += 1

        # Save raw source if needed
        if "arxiv_id" in technique:
            slug = re.sub(r"[^a-zA-Z0-9_]", "_", t_name)[:50]
            save_raw(
                "arxiv", slug,
                f"# {technique.get('arxiv_title', t_name)}\n\n"
                f"**arXiv ID:** {technique['arxiv_id']}\n"
                f"**Published:** {technique.get('published', '')}\n"
                f"**Categories:** {', '.join(technique.get('categories', []))}\n\n"
                f"{technique.get('description', '')}",
                subdir=None
            )

        if technique.get("source") == "reddit":
            slug = re.sub(r"[^a-zA-Z0-9_]", "_", t_name)[:50]
            save_raw(
                "reddit", slug,
                f"# {technique.get('reddit_title', t_name)}\n\n"
                f"**Subreddit:** {technique.get('subreddit', '')}\n"
                f"**URL:** {technique.get('reddit_url', '')}\n"
                f"**Score:** {technique.get('score', 0)}\n\n"
                f"{technique.get('description', '')}",
                subdir=technique.get("subreddit", None)
            )

        # Build registry entry
        entry = {
            "generator": gen,
            "discovered": technique.get("discovered", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "source": technique.get("source", "unknown"),
            "raw_source": technique.get("raw_source", None),
            "encoding_levels": [0],
            "description": technique.get("description", ""),
            "payload_function": f"technique_{t_name}",
            "effectiveness": {},
            "best_for_models": technique.get("model_mentions", []),
            "tags": [technique.get("source", "unknown")],
            "catch_all_data": technique.get("catch_all_data", {}),
        }

        # Add source-specific fields
        if technique.get("source") == "arxiv":
            entry["arxiv_id"] = technique.get("arxiv_id", "")
            entry["arxiv_title"] = technique.get("arxiv_title", "")
        if technique.get("source") == "reddit":
            entry["reddit_url"] = technique.get("reddit_url", "")
            entry["prompt_template"] = technique.get("prompt_template", None)

        registry["techniques"][t_name] = entry
        stats["new_techniques"] += 1
        print(f"  [NEW] {t_name} — from {technique.get('source', 'unknown')}", file=sys.stderr)

    # ── Finalize ──
    registry["last_research_update"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    registry["last_technique_count"] = len(registry["techniques"])

    save_registry(registry)

    # Log the run
    log_entry = (
        f"**Research Run:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"- arXiv raw: {stats['arxiv_found_raw']}, Reddit raw: {stats['reddit_found_raw']}\n"
        f"- New techniques: {stats['new_techniques']}\n"
        f"- Duplicates skipped: {stats['duplicates_skipped']}\n"
        f"- Breakthroughs: {stats['breakthroughs']}\n"
        f"- Total techniques in registry: {registry['last_technique_count']}"
    )
    append_to_log(log_entry)

    # ── Print JSON summary to stdout ──
    summary = {
        "status": "ok",
        "timestamp": registry["last_research_update"],
        "arxiv_queries_used": len(ARXIV_QUERIES),
        "reddit_subreddits_used": len(REDDIT_SUBREDDITS),
        "raw_candidates": {
            "arxiv": stats["arxiv_found_raw"],
            "reddit": stats["reddit_found_raw"],
            "total": sum([stats["arxiv_found_raw"], stats["reddit_found_raw"]]),
        },
        "dedup": {
            "new_techniques": stats["new_techniques"],
            "duplicates_skipped": stats["duplicates_skipped"],
        },
        "breakthroughs_detected": stats["breakthroughs"],
        "total_techniques_in_registry": registry["last_technique_count"],
        "new_techniques": [
            {
                "name": t["name"],
                "source": t.get("source", "unknown"),
                "published": t.get("published", ""),
            }
            for t in all_new_techniques
            if not is_duplicate(t, load_registry())
        ],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
