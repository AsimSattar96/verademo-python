#!/usr/bin/env python3
"""
Parses osv-scanner-baseline.json to extract baseline vulnerability count (CRITICAL + HIGH).

Usage:
  python3 scripts/parse-baseline.py ../osv-scanner-baseline.json

Returns: integer count of CRITICAL + HIGH vulnerabilities
"""

import sys
import json


def parse_osv_baseline(file_path):
    """Parse osv-scanner-baseline.json and count CRITICAL + HIGH vulnerabilities."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Could not find {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)

    count = 0
    results = data.get('results', [])

    for result in results:
        packages = result.get('packages', [])
        for package in packages:
            vulns = package.get('vulnerabilities', [])
            for vuln in vulns:
                severity = vuln.get('database_specific', {}).get('severity', '')
                if severity in ('CRITICAL', 'HIGH'):
                    count += 1

    return count


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/parse-baseline.py <osv-scanner-baseline.json>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    baseline = parse_osv_baseline(file_path)
    print(baseline)
