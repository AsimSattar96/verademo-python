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

        # Look for common patterns in pip-audit output
        # The format typically has package name, version, vulnerability ID, fix version
        # Severity is usually inferred from context or headers

        # For now, count each vulnerability entry
        # pip-audit SCAN-RESULTS.md should have vulnerabilities listed
        # Each line with a CVE/PYSEC ID is a vulnerability

        if 'PYSEC-' in line or 'CVE-' in line:
            # Count the severity if it's marked in the same line or nearby
            # For pip-audit, we need to check if there's a severity marker
            # If not in the line, we'd need to check the JSON report instead

            # This is a heuristic: count occurrences
            if 'critical' in line_lower:
                critical_count += 1
            elif 'high' in line_lower:
                high_count += 1
            else:
                # If no severity marker in the SCAN-RESULTS.md line,
                # assume high (conservative estimate)
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
