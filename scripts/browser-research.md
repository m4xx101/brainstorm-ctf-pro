# Browser-Based Research Fallback

**When to use this:** `research.py --cron` returned 0 results from arXiv/Reddit and wrote `wiki/raw/sources/.browser-fallback-needed.json`. Use this workflow to scrape those sources via Hermes browser tools.

## Quick Start

```bash
# Check if fallback is needed
cat wiki/raw/sources/.browser-fallback-needed.json 2>/dev/null
```

If it exists, follow the steps below for each source listed.

---

## Step 1: Load Fallback Signal

```python
from hermes_tools import read_file
import json

# Read what sources need browser fallback
signal_raw = read_file("wiki/raw/sources/.browser-fallback-needed.json")
signal = json.loads(signal_raw["content"])
for source in signal["sources_requiring_browser"]:
    print(f"  Fallback needed: {source['source']} — {source['reason']}")
    print(f"  {len(source['urls'])} URLs to check")
```

---

## Step 2: arXiv Browser Scrape

If arXiv returned 0 via HTTP API, scrape the arXiv search page directly:

```python
# For each arXiv query URL from the signal:
for url in arxiv_urls:
    1. browser_navigate(url)
    2. browser_scroll(down)  # Load results
    3. browser_snapshot(full=True)
    4. Look for paper entries: title links, abstract text, published dates
    5. For papers from last 14 days:
       - Check title + abstract for technique indicators:
         "jailbreak", "bypass", "adversarial", "injection", "red team",
         "guardrail", "alignment", "attack method"
       - Extract: title, arXiv ID (from URL), published date, abstract (first 500 chars)
    6. Save to: wiki/raw/sources/arxiv/<snake_case_title>.md

After done: read the signal to get next URL. Repeat.
```

**arXiv search URL format:** `https://arxiv.org/search/?query={search_term}&searchtype=all&start=0`

**Key technique indicators** (paper must match at least one):
- Method/technique describing a jailbreak
- Novel bypass approach
- Red teaming framework
- Prompt injection method
- Guardrail evasion

---

## Step 3: Reddit Browser Scrape (old.reddit.com)

If Reddit JSON API returned 0 (typically 403 blocked), use old.reddit.com which renders as static HTML:

```python
# For each Reddit URL from the signal:
for url in reddit_urls:
    1. browser_navigate(url)  # e.g., https://old.reddit.com/r/GPT_jailbreaks/search?q=jailbreak+technique&sort=new&restrict_sr=on
    2. browser_scroll(down)  # Load more results
    3. browser_snapshot(full=True)
    4. Find all post links (look for `a` tags with class `search-title` or `title`)
    5. For each post whose title contains technique keywords:
       - Note the title and score (look for `score` spans or `tagline`)
       - browser_click(post_title_link) to open
       - browser_snapshot(full=True) to read selftext
       - browser_back() to return to search results
    6. Extract: title, selftext (including any code blocks), score, permalink, subreddit
    7. Save to: wiki/raw/sources/reddit/<subreddit>/<snake_case_title>.md

After done: read the signal to get next URL. Repeat.
```

**Reddit search URL format:** `https://old.reddit.com/r/{subreddit}/search?q={query}&sort=new&restrict_sr=on`

**Technique keywords** (post must match at least one):
- `jailbreak`, `prompt injection`, `bypass`, `attack`, `adversarial`
- `red team`, `exploit`, `vulnerability`, `technique`, `method`
- `guardrail`, `safety bypass`, `prompt leak`

**Post score filter:** Skip posts with score < 2 (low engagement).

---

## Step 4: Save Results to Registry

After scraping all browser sources, save newly discovered techniques to the registry:

```python
from hermes_tools import terminal
import json

# Format each discovered technique as a registry-compatible entry
# Run the dedup + save logic:
terminal("python3 scripts/research.py --cron")
# This will pick up the raw saved files and process them
# Or manually add to registry:
# json.load(open("wiki/registry.json"))
```

---

## Step 5: Clean Up

```bash
# Remove fallback signal so it won't trigger again:
rm -f wiki/raw/sources/.browser-fallback-needed.json

# Regenerate playbook with new knowledge:
python3 scripts/generate-playbook.py --model-version "{target_model}"
```

---

## Verification

- [ ] All browser URLs from the signal were visited
- [ ] Raw sources saved to `wiki/raw/sources/arxiv/` and `wiki/raw/sources/reddit/`
- [ ] Registry updated with new techniques
- [ ] Fallback signal file removed
- [ ] Playbook regenerated
