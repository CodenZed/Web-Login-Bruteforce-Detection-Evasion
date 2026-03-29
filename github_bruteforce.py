#!/usr/bin/env python3
"""
GitHub BruteForceAI v2.0 - Authorized Pentest Tool
"""

import argparse
import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════════════╗
║          GitHub BruteForceAI v2.0 - Pentest Tool     ║
║             Authorized Security Assessment           ║
╚══════════════════════════════════════════════════════╝
"""

async def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(description="GitHub login pentest tool")
    parser.add_argument('-t', '--target', required=True, help='Targets file (one username per line)')
    parser.add_argument('-w', '--wordlist', required=True, help='Passwords file')
    parser.add_argument('--mode', choices=['bruteforce', 'spray'], default='spray', help='Attack mode')
    parser.add_argument('-T', '--threads', type=int, default=3, help='Threads (max 10)')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between attempts')
    parser.add_argument('--webhook', help='Discord/Slack webhook URL')
    
    args = parser.parse_args()
    
    from brute_github_core import GitHubBruteForceCore
    core = GitHubBruteForceCore(
        targets_file=args.target,
        wordlist_file=args.wordlist,
        mode=args.mode,
        threads=args.threads,
        delay=args.delay,
        webhook=args.webhook
    )
    
    await core.run()
    print("🎉 Done! Check github_results.db and logs.")

if __name__ == "__main__":
    asyncio.run(main())