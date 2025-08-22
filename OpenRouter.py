#!/usr/bin/env python3
# OpenRouter.py — tiny chat client for OpenRouter with file-backed conversation state
# Usage examples:
#   python OpenRouter.py "Hello!"                         # new conversation (prints id)
#   python OpenRouter.py "Continue..." --cid 123e-...     # continue existing conversation
#   python OpenRouter.py "Hi" --model openrouter/auto     # choose model
#   python OpenRouter.py "Hi" --json                      # JSON output (text + cid)
#
# Tip (a-Shell): mark executable:  chmod +x OpenRouter.py

import os, sys, json, uuid, argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("This script requires the 'requests' package. Try: pip install requests", file=sys.stderr)
    sys.exit(1)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/auto"  # good default on OpenRouter

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except Exception:
    # Fallback to current working directory if __file__ isn't available
    SCRIPT_DIR = Path.cwd().resolve()

ASSETS_DIR = SCRIPT_DIR / "assets"
STORE_DIR = ASSETS_DIR / ".openrouter_chats"
KEY_FILE = ASSETS_DIR / ".openrouter_key"

def read_api_key():
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    if KEY_FILE.exists():
        try:
            k = KEY_FILE.read_text().strip()
            if k:
                return k
        except Exception:
            pass

    # If non-interactive, fail with helpful message
    if not sys.stdin.isatty():
        print("Missing OpenRouter API key. Set OPENROUTER_API_KEY or put it in ~/.openrouter_key", file=sys.stderr)
        sys.exit(2)

    try:
        key = input("OpenRouter API key not found. Paste key now (or leave empty to abort): ").strip()
    except EOFError:
        print("No input available. Aborting.", file=sys.stderr)
        sys.exit(2)

    if not key:
        print("No API key provided. Aborting.", file=sys.stderr)
        sys.exit(2)

    # Ask whether to save the key to ~/.openrouter_key
    try:
        resp = input(f"Save key to {KEY_FILE} for future use? [Y/n]: ").strip().lower()
    except EOFError:
        resp = "y"

    if resp in ("", "y", "yes"):
        try:
            KEY_FILE.write_text(key + "\n", encoding="utf-8")
            try:
                os.chmod(KEY_FILE, 0o600)
            except Exception:
                pass
            print(f"Saved key to {KEY_FILE}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: failed to save key: {e}", file=sys.stderr)

    return key

def load_history(cid: str):
    path = STORE_DIR / f"{cid}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            # Corrupt or empty; start fresh
            return []
    return []

def save_history(cid: str, messages):
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    path = STORE_DIR / f"{cid}.json"
    path.write_text(json.dumps(messages, ensure_ascii=False, indent=2))

def parse_args():
    p = argparse.ArgumentParser(description="Minimal OpenRouter chat client.")
    p.add_argument("message", help="User message to send.")
    p.add_argument("--cid", help="Conversation ID to continue. If omitted, a new one is created.")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    p.add_argument("--system", default=None, help="Optional system prompt (only added once at start).")
    p.add_argument("--json", action="store_true", help="Output JSON with {'text','conversation_id'}.")
    p.add_argument("--title", default="aShell Chat", help="Optional X-Title header for OpenRouter dashboard.")
    p.add_argument("--referer", default="https://local", help="Optional HTTP-Referer header.")
    return p.parse_args()

def ensure_system_once(messages, system_text):
    if not system_text:
        return messages
    # Only add a system message if none exists yet
    has_system = any(m.get("role") == "system" for m in messages)
    if not has_system:
        return [{"role": "system", "content": system_text}] + messages
    return messages

def main():
    args = parse_args()
    api_key = read_api_key()

    # Determine conversation id
    cid = args.cid or str(uuid.uuid4())

    # Load & prepare history
    messages = load_history(cid)
    messages = ensure_system_once(messages, args.system)
    messages.append({"role": "user", "content": args.message})

    # Build request
    payload = {
        "model": args.model,
        "messages": messages,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # These two are optional but recommended by OpenRouter
        "HTTP-Referer": args.referer,
        "X-Title": args.title,
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.HTTPError as e:
        # Print server error message if available
        try:
            err = r.json()
            msg = err.get("error", err)
        except Exception:
            msg = str(e)
        print(f"OpenRouter API error: {msg}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(4)

    # Extract assistant reply (OpenAI-style schema)
    try:
        reply = data["choices"][0]["message"]["content"]
    except Exception:
        print(f"Unexpected response format: {json.dumps(data)[:500]}", file=sys.stderr)
        sys.exit(5)

    # Persist updated history
    messages.append({"role": "assistant", "content": reply})
    save_history(cid, messages)

    if args.json:
        print(json.dumps({"conversation_id": cid, "text": reply}, ensure_ascii=False))
    else:
        # Plain output for easy piping; include cid hint on a separate line
        print(reply)
        print(f"\n[conversation_id: {cid}]", file=sys.stderr)

if __name__ == "__main__":
    main()
