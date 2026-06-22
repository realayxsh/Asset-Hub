import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar
from cogs.events._antinuke_base import AntiNukeBase

log = logging.getLogger(__name__)


class antiemostick(AntiNukeBase):

    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild: discord.Guild, before: list, after: list):
        if len(after) >= len(before):
            return
        asyncio.create_task(self._handle(guild, before, after))

    async def _handle(self, guild: discord.Guild, before: list, after: list):
        try:
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return
            entry = await self._get_recent_entry(guild, discord.AuditLogAction.sticker_delete)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return
            reason = f"AntiNuke: unauthorized sticker delete by {entry.user}"
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Sticker Deleted", entry.user, data["punishment"],
                                 {"Count": f"{len(before) - len(after)} deleted"})
            ))
        except Exception as err:
            log.error("antiemostick: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antiemostick(client))
