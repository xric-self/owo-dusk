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

import asyncio
import re

from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

from core.cogs._BASE import BaseCog

"""
SHOP-
100-110 - limited time items
200-274 - wallpapers (one time buy)
1-7 - rings
"""

cash_regex = r"for \*\*(\d+)\*\* <:cowoncy:\d+>"

# Mapping from item name (as in config) to the numeric ID used in `owo buy`
ITEM_NAME_TO_ID = {
    "commonRing": "1",
    "uncommonRing": "2",
    "rareRing": "3",
    "epicRing": "4",
    "mythicalRing": "5",
    "legendaryRing": "6",
    "fabledRing": "7",
}


class Shop(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.cmd = {
            "cmd_name": "buy",
            "cmd_arguments": "",
            "prefix": True,
            "checks": True,
            "id": "shop",
        }

    @property
    def settings(self):
        return self.bot.settings_dict.commands.shop

    async def cog_load(self):
        if not self.settings.enabled:
            try:
                asyncio.create_task(self.bot.unload_cog("core.cogs.shop"))
            except ExtensionNotLoaded:
                pass
        else:
            asyncio.create_task(self.send_buy(startup=True))

    async def cog_unload(self):
        await self.bot.remove_queue(id="shop")

    async def send_buy(self, startup=False):
        if startup:
            await self.bot.sleep_till(self.bot.settings_dict.cooldowns.shortCooldown)
        else:
            await self.bot.remove_queue(id="shop")
            await self.bot.sleep(self.settings.get_cd())

        # Get the list of item names from the config (e.g., ["commonRing"])
        items_to_buy_names = self.settings.get_items_to_buy(
            cur_cash=self.bot.user_status["balance"],
            cash_check=self.bot.settings_dict.cashCheck,
        )

        # --- FIX 1: If empty, retry after a short delay ---
        if not items_to_buy_names:
            print("[Shop] No items to buy – skipping this cycle.")
            await asyncio.sleep(30)
            await self.send_buy()
            return

        # --- FIX 2: Convert the chosen name to its numeric ID ---
        chosen_name = self.bot.random.choice(items_to_buy_names)
        item_id = ITEM_NAME_TO_ID.get(chosen_name)

        if item_id:
            self.cmd["cmd_arguments"] = item_id  # Send `owo buy 1` instead of `owo buy commonRing`
            await self.bot.put_queue(self.cmd)
        else:
            print(f"[Shop] Unknown item name '{chosen_name}' – skipping.")
            await asyncio.sleep(30)
            await self.send_buy()

    @commands.Cog.listener()
    async def on_message(self, message):
        nick = self.bot.get_nick(message)

        if not message.channel.id == self.bot.cm.id:
            return
        if nick not in message.content:
            return

        if "**, you bought a " in message.content:
            self.bot.update_cash(
                int(re.search(cash_regex, message.content).group(1)), reduce=True
            )
            await self.send_buy()


async def setup(bot):
    await bot.add_cog(Shop(bot))
