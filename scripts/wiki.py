#!/usr/bin/env python3
"""
wiki.py — Wiki CRUD + session checkpoint manager for adversarial AI testing.

Operations:
  save_payload(payload_text, metadata) → filename
  save_response(response_text, sha256) → filename
  save_checkpoint(session_state) → checkpoint_file
  load_checkpoint(target_slug) → session_state | None
  search(query) → [matching filenames]
  log_entry(text) → appends to log

Cross-session persistence. Git-friendly (one file per session).
~100 lines.
"""
import sys, json, os, argparse, hashlib, glob, re
from datetime import datetime

WIKI_DIR = os.path.expanduser("~/.hermes/wiki/brainstorm-ctf-pro")

def ensure_wiki():
    os.makedirs(f"{WIKI_DIR}/payloads", exist_ok=True)
    os.makedirs(f"{WIKI_DIR}/responses", exist_ok=True)
    os.makedirs(f"{WIKI_DIR}/checkpoints", exist_ok=True)
    os.makedirs(f"{WIKI_DIR}/logs", exist_ok=True)

def _ts():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def save_payload(payload_text, metadata=None):
    ensure_wiki()
    sha = hashlib.sha256(payload_text.encode()).hexdigest()[:16]
    path = f"{WIKI_DIR}/payloads/{sha}.json"
    entry = {"sha256": sha, "timestamp": _ts(), "payload": payload_text, "metadata": metadata or {}}
    with open(path, "w") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    return f"payloads/{sha}.json"

def save_response(response_text, payload_sha, metadata=None):
    ensure_wiki()
    sha = hashlib.sha256(response_text.encode()).hexdigest()[:16]
    path = f"{WIKI_DIR}/responses/{sha}.json"
    entry = {"sha256": sha, "payload_sha256": payload_sha, "timestamp": _ts(), "response": response_text, "metadata": metadata or {}}
    with open(path, "w") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    return f"responses/{sha}.json"

def save_checkpoint(session_state):
    """Save full session state for resume. session_state is a dict."""
    ensure_wiki()
    target = session_state.get("target", "unknown")
    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', target[:40])
    path = f"{WIKI_DIR}/checkpoints/{slug}.json"
    session_state["_last_checkpoint"] = _ts()
    # Keep only the last 5 checkpoints per target
    old = glob.glob(f"{WIKI_DIR}/checkpoints/{slug}_*.json")
    old.sort()
    for f in old[:-4]:
        try:
            os.remove(f)
        except OSError:
            pass
    cp_path = f"{WIKI_DIR}/checkpoints/{slug}_{_ts()}.json"
    with open(cp_path, "w") as f:
        json.dump(session_state, f, indent=2, ensure_ascii=False)
    return cp_path

def load_checkpoint(target_slug=None):
    """Load latest checkpoint for a target. Returns None if none found."""
    ensure_wiki()
    pattern = f"{WIKI_DIR}/checkpoints/{target_slug}_*.json" if target_slug else f"{WIKI_DIR}/checkpoints/*.json"
    files = glob.glob(pattern)
    if not files:
        # Try matching by target slug inside files
        files = glob.glob(f"{WIKI_DIR}/checkpoints/*.json")
        if files and target_slug:
            for f in sorted(files, reverse=True):
                try:
                    with open(f) as fh:
                        data = json.load(fh)
                    if data.get("target", "").startswith(target_slug):
                        return data
                except (json.JSONDecodeError, IOError):
                    continue
        return None
    files.sort(reverse=True)
    try:
        with open(files[0]) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def list_targets():
    """List all targets with checkpoints."""
    ensure_wiki()
    files = glob.glob(f"{WIKI_DIR}/checkpoints/*.json")
    targets = {}
    for f in sorted(files, reverse=True):
        try:
            with open(f) as fh:
                data = json.load(fh)
            t = data.get("target", "unknown")
            if t not in targets:
                targets[t] = {"file": f, "timestamp": data.get("_last_checkpoint", ""),
                              "iterations": data.get("iteration", 0), "status": data.get("status", "unknown")}
        except (json.JSONDecodeError, IOError):
            continue
    return targets

def search(query):
    """Search payloads and responses for matching text."""
    ensure_wiki()
    results = []
    q = query.lower()
    for dirname in ["payloads", "responses", "logs"]:
        for f in glob.glob(f"{WIKI_DIR}/{dirname}/*.json"):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                text = json.dumps(data).lower()
                if q in text:
                    results.append({"file": f.replace(f"{WIKI_DIR}/", ""), "type": dirname,
                                    "sha256": data.get("sha256", "")[:16], "timestamp": data.get("timestamp", "")})
            except (json.JSONDecodeError, IOError):
                continue
    return results

def log_entry(text, session_id=None):
    """Append a line to the session log."""
    ensure_wiki()
    sid = session_id or _ts()
    path = f"{WIKI_DIR}/logs/{sid[:16]}.md"
    with open(path, "a") as f:
        f.write(f"[{_ts()}] {text}\n")
    return path

def bootstrap():
    """Create wiki dirs and initial structure."""
    ensure_wiki()
    readme_path = f"{WIKI_DIR}/README.md"
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("# Brainstorm-CTF-Pro Wiki\n\nAuto-generated session data.\n\n"
                    "## Directory Layout\n\n"
                    "- `payloads/` — raw payloads, indexed by SHA256\n"
                    "- `responses/` — model responses, indexed by SHA256\n"
                    "- `checkpoints/` — session state snapshots for resume\n"
                    "- `logs/` — session log entries\n")
    return WIKI_DIR

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki Manager for Brainstorm-CTF-Pro")
    parser.add_argument("action", nargs="?", choices=["save_payload", "save_response", "save_checkpoint",
                                            "load_checkpoint", "list", "search", "log", "bootstrap"],
                        default=None, help="Action to perform")
    parser.add_argument("--action", dest="action2", choices=["save_payload", "save_response", "save_checkpoint",
                                            "load_checkpoint", "list", "search", "log", "bootstrap"],
                        default=None, help="Action to perform (alternative to positional)")
    parser.add_argument("--payload", default="")
    parser.add_argument("--response", default="")
    parser.add_argument("--metadata", default="{}")
    parser.add_argument("--payload-sha", default="")
    parser.add_argument("--target", default="")
    parser.add_argument("--query", default="")
    parser.add_argument("--text", default="")
    parser.add_argument("--session", default="")
    parser.add_argument("--file", help="Read input from file")
    args = parser.parse_args()
    action = args.action or args.action2
    if not action:
        parser.print_help()
        sys.exit(1)

    if args.file:
        with open(args.file) as f:
            content = f.read()
    else:
        content = ""

    if action == "bootstrap":
        path = bootstrap()
        print(json.dumps({"wiki_dir": path, "status": "initialized"}))
    elif action == "save_payload":
        text = content or args.payload
        meta = json.loads(args.metadata) if args.metadata else {}
        print(json.dumps({"path": save_payload(text, meta)}))
    elif action == "save_response":
        text = content or args.response
        meta = json.loads(args.metadata) if args.metadata else {}
        print(json.dumps({"path": save_response(text, args.payload_sha, meta)}))
    elif action == "save_checkpoint":
        state = json.loads(content or args.payload) if (content or args.payload) else {"target": args.target or "test"}
        print(json.dumps({"path": save_checkpoint(state)}))
    elif action == "load_checkpoint":
        data = load_checkpoint(args.target)
        if data:
            print(json.dumps(data))
        else:
            print(json.dumps({"error": "No checkpoint found", "target": args.target}))
    elif action == "list":
        print(json.dumps(list_targets(), indent=2))
    elif action == "search":
        results = search(args.query)
        print(json.dumps(results, indent=2))
    elif action == "log":
        path = log_entry(args.text or content, args.session)
        print(json.dumps({"path": path}))
