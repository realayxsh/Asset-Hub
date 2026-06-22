import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar
from cogs.events._antinuke_base import AntiNukeBase

log = logging.getLogger(__name__)


class antibot(AntiNukeBase):

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.bot:
            return
        asyncio.create_task(self._handle(member))

    async def _handle(self, member: discord.Member):
        try:
            guild = member.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.bot_add)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return

            reason = f"AntiNuke: unauthorized bot added by {entry.user}"
            punishment = data["punishment"]
            try:
                await guild.kick(member, reason=reason)
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, punishment, reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Bot Added", entry.user, punishment, {"Bot": str(member)})
            ))
        except Exception as err:
            log.error("antibot: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antibot(client))
