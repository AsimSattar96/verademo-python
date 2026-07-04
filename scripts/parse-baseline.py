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
    """Parse pip-audit SCAN-RESULTS.md and count critical + high vulnerabilities."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Could not find {file_path}", file=sys.stderr)
        sys.exit(1)

    critical_count = 0
    high_count = 0

    # Parse the tabular format: each row with CVE/PYSEC has severity
    # Lines look like: "django                4.2.13    PYSEC-2024-58       4.2.14,5.0.7"
    # We need to look for severity indicators in the line

    lines = content.split('\n')
    for line in lines:
        line_lower = line.lower()

        # Count each vulnerability entry (CVE/PYSEC ID line)
        if 'pysec-' in line_lower or 'cve-' in line_lower:
            # Check for severity in the line
            if 'critical' in line_lower:
                critical_count += 1
            elif 'high' in line_lower:
                high_count += 1
            else:
                # If no severity marker, assume high (conservative)
                high_count += 1

    total = critical_count + high_count
    return total


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/parse-baseline.py <SCAN-RESULTS.md>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    baseline = parse_pip_baseline(file_path)
    print(baseline)
