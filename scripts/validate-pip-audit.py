#!/usr/bin/env python3
"""
Validates pip-audit results against Critical/High vulnerability threshold.

Usage:
  python3 scripts/validate-pip-audit.py <audit-report.json>

Exit codes:
  0 - No critical/high vulnerabilities found
  1 - Critical/high vulnerabilities found
"""

import json
import sys


def validate_pip_audit(report_path):
    """Parse pip-audit JSON report and check for critical/high vulnerabilities."""
    try:
        with open(report_path, 'r') as f:
            audit_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Could not find audit report at {report_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Could not parse {report_path} as JSON")
        sys.exit(1)

    # Count vulnerabilities by severity
    vulnerabilities = audit_data.get('vulnerabilities', [])

    critical_count = 0
    high_count = 0
    moderate_count = 0

    for vuln in vulnerabilities:
        severity = vuln.get('vulnerability', {}).get('severity', 'unknown').lower()
        if severity == 'critical':
            critical_count += 1
        elif severity == 'high':
            high_count += 1
        elif severity in ('moderate', 'medium'):
            moderate_count += 1

    print("\n🔍 pip-audit Vulnerability Summary:")
    print(f"  🔴 Critical: {critical_count}")
    print(f"  🟠 High:     {high_count}")
    print(f"  🟡 Moderate: {moderate_count}")
    print(f"  Total:       {len(vulnerabilities)}")

    total_critical_high = critical_count + high_count

    if total_critical_high > 0:
        print(f"\n❌ Found {total_critical_high} critical/high vulnerabilities that need fixing.")
        print("Check SCAN-RESULTS.md for the recommended fixes.")
        return False
    else:
        print(f"\n✅ No critical or high vulnerabilities detected!")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate-pip-audit.py <audit-report.json>")
        sys.exit(1)

    report_path = sys.argv[1]
    success = validate_pip_audit(report_path)
    sys.exit(0 if success else 1)
