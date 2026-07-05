#!/usr/bin/env python3
"""
Parses SCAN-RESULTS.md to extract baseline vulnerability count (critical + high).

For pip-audit format.

Usage:
  python3 scripts/parse-baseline.py ../SCAN-RESULTS.md

Returns: integer count of critical + high vulnerabilities
"""

import sys


def parse_pip_baseline(file_path):
    """Parse pip-audit SCAN-RESULTS.md and count vulnerabilities from JSON."""
    import json
    import re

    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Could not find {file_path}", file=sys.stderr)
        sys.exit(1)

    # Extract JSON from markdown code block
    match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
    if not match:
        print(f"❌ Could not find JSON in {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)

    count = 0
    for dep in data.get('dependencies', []):
        vulns = dep.get('vulns', [])
        count += len(vulns)

    return count


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/parse-baseline.py <SCAN-RESULTS.md>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    baseline = parse_pip_baseline(file_path)
    print(baseline)
