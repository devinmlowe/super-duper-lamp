#!/usr/bin/env python3
import sys

# Check for argument
if len(sys.argv) != 2:
    print("Usage: hello.py <name>")
    sys.exit(1)

name = sys.argv[1]
print(f"Hello {name}!")