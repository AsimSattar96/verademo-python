#!/usr/bin/env python3
"""
Scores a participant's work by comparing current vulnerabilities to baseline.

Creates a leaderboard event file and pushes to the leaderboard repo.

Usage (in GitHub Actions):
  python3 scripts/score-and-leaderboard.py \
    --repo-name verademo-python \
    --username octocat \
    --baseline-count 25 \
    --current-count 8 \
    --timestamp 2026-07-09T10:53:55.01234Z \
    --leaderboard-repo github-owner/leaderboard \
    --github-token ${{ secrets.LEADERBOARD_TOKEN }}
"""

import json
import sys
import subprocess
import argparse
import hashlib
import tempfile
import os


ADJECTIVES = [
    'caffeinated', 'clever', 'bold', 'swift', 'paranoid', 'hashed', 'patched',
    'verified', 'compiled', 'quantum', 'legendary', 'cosmic', 'ethereal',
    'fearless', 'valiant', 'reckless', 'dashing', 'mighty', 'keen', 'fierce',
    'brilliant', 'vivid', 'noble', 'wild', 'sharp', 'quick', 'bright',
    'agile', 'robust', 'sleek', 'vigilant', 'dynamic', 'precise',
]

NOUNS = [
    'phoenix', 'dragon', 'fortress', 'sentinel', 'guardian', 'beacon', 'artifact',
    'package', 'monitor', 'auditor', 'watchtower', 'vault', 'cipher', 'shield',
    'armor', 'knight', 'warrior', 'oracle', 'prophet', 'champion',
    'protector', 'warden', 'steward', 'curator', 'keeper', 'defender', 'ally',
    'companion', 'partner', 'agent',
]


def generate_alias(username):
    """Generate deterministic fun alias from username."""
    hash_obj = hashlib.sha256(username.lower().encode())
    hash_int = int(hash_obj.hexdigest(), 16)

    adj_idx = hash_int % len(ADJECTIVES)
    hash_int //= len(ADJECTIVES)
    noun_idx = hash_int % len(NOUNS)

    return f"{ADJECTIVES[adj_idx]}-{NOUNS[noun_idx]}"


def create_event_file(repo_name, alias, baseline_count, current_count, timestamp):
    """Create leaderboard event JSON."""
    score = baseline_count - current_count

    event = {
        "participant_alias": alias,
        "repo": repo_name,
        "score": score,
        "time": timestamp,
    }

    return event


def push_to_leaderboard(event, repo_name, alias, timestamp, leaderboard_repo, github_token):
    """Push event file to leaderboard repo."""
    # Format: 2026-07-09T10:53:55.01234Z-alias.json
    filename = f"{timestamp}-{alias}.json"
    file_path = f"events/{repo_name}/{filename}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Configure git
        subprocess.run(['git', 'config', '--global', 'user.name', 'wad-scorer'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.email', 'wad@veracode.com'], check=True)

        # Clone with auth
        clone_url = f"https://x-access-token:{github_token}@github.com/{leaderboard_repo}.git"
        subprocess.run(['git', 'clone', clone_url, tmpdir], check=True)

        # Create directory if needed
        event_dir = os.path.join(tmpdir, 'events', repo_name)
        os.makedirs(event_dir, exist_ok=True)

        # Write event file
        event_file = os.path.join(tmpdir, file_path)
        with open(event_file, 'w') as f:
            json.dump(event, f, indent=2)

        # Commit and push
        os.chdir(tmpdir)
        subprocess.run(['git', 'add', file_path], check=True)
        subprocess.run(
            ['git', 'commit', '-m', f"Score: {alias} - {event['score']} vulns fixed"],
            check=True
        )
        subprocess.run(['git', 'push'], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Score participant work and push to leaderboard')
    parser.add_argument('--repo-name', required=True, help='Original repo name')
    parser.add_argument('--username', required=True, help='GitHub username of participant')
    parser.add_argument('--baseline-count', type=int, required=True, help='Baseline vulnerability count')
    parser.add_argument('--current-count', type=int, required=True, help='Current vulnerability count')
    parser.add_argument('--timestamp', required=True, help='ISO timestamp')
    parser.add_argument('--leaderboard-repo', required=True, help='Leaderboard repo (owner/repo)')
    parser.add_argument('--github-token', required=True, help='GitHub token with push access')

    args = parser.parse_args()

    # Generate alias
    alias = generate_alias(args.username)
    print(f"✅ Alias: {alias}")

    # Create event
    event = create_event_file(
        args.repo_name,
        alias,
        args.baseline_count,
        args.current_count,
        args.timestamp
    )
    print(f"✅ Score: {event['score']}")

    # Push to leaderboard
    try:
        push_to_leaderboard(
            event,
            args.repo_name,
            alias,
            args.timestamp,
            args.leaderboard_repo,
            args.github_token
        )
        print(f"✅ Pushed to leaderboard!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push to leaderboard: {e}", file=sys.stderr)
        sys.exit(1)
