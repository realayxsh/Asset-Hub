import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar
from cogs.events._antinuke_base import AntiNukeBase

log = logging.getLogger(__name__)


class antiemojiu(AntiNukeBase):

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: list, after: list):
        if len(after) <= len(before):
            return
        asyncio.create_task(self._handle_upload(guild))

    async def _handle_upload(self, guild: discord.Guild):
        try:
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return
            entry = await self._get_recent_entry(guild, discord.AuditLogAction.emoji_create)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return
            reason = f"AntiNuke: unauthorized emoji upload by {entry.user}"
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild, self._log_embed("Emoji Uploaded", entry.user, data["punishment"])
            ))
        except Exception as err:
            log.error("antiemojiu: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antiemojiu(client))
