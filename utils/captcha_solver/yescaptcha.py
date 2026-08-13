# This file is part of owo-dusk.
#
# Copyright (c) 2024-present EchoQuill
#
# Portions of this file are based on code by EchoQuill, licensed under the
# GNU General Public License v3.0 (GPL-3.0).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import os
import aiohttp
import json
from gatesolve import GateSolve

class captchaClient:
    def __init__(self, api):
        # api is the GateSolve API key (optional, can be read from env)
        self.api = api or os.getenv("GATESOLVE_API_KEY")
        if not self.api:
            raise ValueError("GateSolve API key is required. Set GATESOLVE_API_KEY environment variable.")
        self.balance = 999  # dummy balance – GateSolve has a free tier; we ignore balance checks
        self._site_key = "a6a1d5ce-612d-472d-8e37-7601408fbc09"  # OwO's site key
        self._payload = {
            "authorize": True,
            "integration_type": 0,
            "permissions": "0",
            "location_context": {
                "guild_id": "10000",
                "channel_id": "10000",
                "channel_type": 10000,
            },
        }
        self._auth_url = r"https://discord.com/api/v9/oauth2/authorize?client_id=408785106942164992&response_type=code&redirect_uri=https://owobot.com/api/auth/discord/redirect&scope=identify guilds"

    # Dummy balance methods – GateSolve has free credits; we don't need to check balance.
    def get_yescaptcha_balance_sync(self):
        return 999

    async def get_yescaptcha_balance(self, session: aiohttp.ClientSession) -> int:
        return 999

    async def update_balance(self):
        self.balance = 999

    async def solve_hcaptcha_logic(self, retries=3):
        """
        Solve hCaptcha using GateSolve API.
        Returns the captcha token.
        """
        client = GateSolve(api_key=self.api)
        try:
            token = client.solve(
                "hcaptcha",
                site_key=self._site_key,
                page_url="https://owobot.com/captcha"
            )
            return token
        except Exception as e:
            print(f"GateSolve solving error: {e}")
            return None

    async def solve_owo_bot_captcha(self, discord_headers, tries):
        """
        Main entry point called by the bot to solve the captcha.
        Returns True if solved, False otherwise.
        """
        # Set up the OAuth flow (same as original)
        discord_headers["Referer"] = self._auth_url

        async with aiohttp.ClientSession() as session:
            # 1. OAuth authorize
            async with session.post(
                self._auth_url,
                json=self._payload,
                headers=discord_headers,
                allow_redirects=True,
            ) as oauth_resp:
                if oauth_resp.status != 200:
                    print(f"OAuth failed with HTTP {oauth_resp.status}")
                    return False
                oauth_text = await oauth_resp.text()

            # 2. Follow redirect if present
            try:
                oauth_json = json.loads(oauth_text)
                redirect_url = oauth_json.get("location")
                if redirect_url:
                    async with session.get(redirect_url) as redirect_resp:
                        if redirect_resp.status != 200:
                            print(f"Redirect failed with HTTP {redirect_resp.status}")
                            return False
            except Exception as e:
                print(f"OAuth parsing failed: {e}")
                print(f"Raw response: {oauth_text}")
                return False

            # 3. Hit captcha page to set cookies
            async with session.get("https://owobot.com/captcha") as captcha_resp:
                if captcha_resp.status != 200:
                    print(f"Captcha page failed with HTTP {captcha_resp.status}")
                    return False

            # 4. Verify session is active
            async with session.get("https://owobot.com/api/auth") as auth_resp:
                if auth_resp.status != 200:
                    print(f"Auth check failed with HTTP {auth_resp.status}")
                    return False
                auth_data = await auth_resp.json()
            if not auth_data:
                print("Auth data None")
                return False

            # 5. Solve using GateSolve
            try:
                solution = await self.solve_hcaptcha_logic(tries)
                if not solution:
                    print("No solution result from GateSolve")
                    return False
            except Exception as e:
                print(f"Solver Error: {e}")
                return False

            # 6. Submit the solution
            async with session.post(
                "https://owobot.com/api/captcha/verify",
                json={"token": solution},
                headers={
                    "Referer": "https://owobot.com/captcha",
                    "Origin": "https://owobot.com",
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                },
            ) as verify_resp:
                if verify_resp.status == 200:
                    return True
                else:
                    error_text = await verify_resp.text()
                    print(f"Verification failed (Status {verify_resp.status})")
                    print(f"Server Response: {error_text}")
                    return False
