#!/usr/bin/env python3
"""A simple Python script to parse JSON from a file or standard input."""
import json
import argparse
import sys

def parse_json(source):
    """Parse JSON from a file-like object."""
    try:
        return json.load(source)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error parsing JSON: {e}\n")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Parse JSON file or string.')
    parser.add_argument('file', nargs='?',
                        help='Path to JSON file (if omitted, read from stdin)')
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, 'r') as f:
                data = parse_json(f)
        except FileNotFoundError:
            sys.stderr.write(f"File not found: {args.file}\n")
            sys.exit(1)
    else:
        data = parse_json(sys.stdin)

    # Pretty-print the parsed JSON
    print(json.dumps(data, indent=4))

if __name__ == '__main__':
    main()