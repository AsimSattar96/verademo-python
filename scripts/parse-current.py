#!/usr/bin/env python3
"""
Parses OSV Scanner JSON report to count current CRITICAL + HIGH vulnerabilities.

Usage:
  python3 scripts/parse-current.py <audit-report.json>

Returns: integer count of CRITICAL + HIGH vulnerabilities
"""

import sys
import json


def parse_current(report_path):
    """Parse OSV Scanner JSON and count CRITICAL + HIGH vulnerabilities."""
    try:
        with open(report_path, 'r') as f:
            content = f.read().strip()
            if not content:
                print(f"❌ Report file is empty: {report_path}", file=sys.stderr)
                sys.exit(1)
            data = json.loads(content)
    except FileNotFoundError:
        print(f"❌ Could not find {report_path}", file=sys.stderr)
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
        print("Usage: python3 scripts/parse-current.py <audit-report.json>", file=sys.stderr)
        sys.exit(1)

    report_path = sys.argv[1]
    count = parse_current(report_path)
    print(count)
