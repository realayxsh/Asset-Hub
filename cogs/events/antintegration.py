import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar
from cogs.events._antinuke_base import AntiNukeBase

log = logging.getLogger(__name__)


class antintegration(AntiNukeBase):

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild: discord.Guild):
        asyncio.create_task(self._handle(guild))

    async def _handle(self, guild: discord.Guild):
        try:
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return
            entry = await self._get_recent_entry(guild, discord.AuditLogAction.integration_create)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return
            reason = f"AntiNuke: unauthorized integration by {entry.user}"
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild, self._log_embed("Integration Added", entry.user, data["punishment"])
            ))
        except Exception as err:
            log.error("antintegration: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antintegration(client))
