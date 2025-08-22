#!/usr/bin/env python3
import sys, json, argparse, os

parser = argparse.ArgumentParser(description="Escape text for JSON string content.")
parser.add_argument("text", nargs="*", help="Text to escape (optional if using --file or stdin).")
parser.add_argument("--file", "-f", help="Read raw text from a file.")
parser.add_argument("--bare", action="store_true",
                    help="Output without outer quotes (rarely needed).")
args = parser.parse_args()

if args.file:
    with open(args.file, "r", encoding="utf-8") as fh:
        raw = fh.read()
elif not sys.stdin.isatty():
    raw = sys.stdin.read()
elif args.text:
    raw = " ".join(args.text)
else:
    sys.stderr.write("No input. Provide text args, pipe via stdin, or use --file.\n")
    sys.exit(1)

escaped = json.dumps(raw)
if args.bare:
    # Strip the outer quotes of the JSON string (not usually what you want)
    print(escaped[1:-1])
else:
    print(escaped)