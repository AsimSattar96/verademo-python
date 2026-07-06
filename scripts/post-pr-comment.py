#!/usr/bin/env python3
"""
Posts a scoring update comment to a GitHub PR using the GitHub CLI.

Usage:
  python3 scripts/post-pr-comment.py \
    --baseline <count> \
    --current <count> \
    --score <count> \
    --timestamp <iso-timestamp> \
    --scanner <scanner-name>

Environment variables:
  GH_TOKEN - GitHub token (required for gh CLI)
"""

import sys
import subprocess
import argparse


def post_comment(baseline, current, score, timestamp, scanner):
    """Generate and post comment to PR using gh CLI."""
    status = '❌'
    if current == 0:
        status = '✅'
    elif score > 0:
        status = '🟡'

    body = f"""{status} **Scoring Update**

| Metric | Value |
|--------|-------|
| Baseline | {baseline} vulnerabilities |
| Current | {current} vulnerabilities |
| Fixed | {score} vulnerabilities |
| Timestamp | {timestamp} |

Run `osv-scanner --lockfile={scanner}` locally to see details."""

    try:
        result = subprocess.run(
            ['gh', 'pr', 'comment', '--body', body],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            print(f"❌ Failed to post comment: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        print(f"✅ Posted comment to PR")
    except FileNotFoundError:
        print(f"❌ gh CLI not found. Install GitHub CLI: https://cli.github.com/", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Post scoring update comment to PR')
    parser.add_argument('--baseline', type=int, required=True, help='Baseline vulnerability count')
    parser.add_argument('--current', type=int, required=True, help='Current vulnerability count')
    parser.add_argument('--score', type=int, required=True, help='Vulnerabilities fixed')
    parser.add_argument('--timestamp', required=True, help='ISO timestamp of scan')
    parser.add_argument('--scanner', required=True, help='Scanner lockfile name (e.g., package-lock.json)')

    args = parser.parse_args()

    post_comment(args.baseline, args.current, args.score, args.timestamp, args.scanner)
