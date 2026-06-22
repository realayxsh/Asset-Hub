import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar
from cogs.events._antinuke_base import AntiNukeBase

log = logging.getLogger(__name__)


class antiwebhook(AntiNukeBase):

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel: discord.abc.GuildChannel):
        asyncio.create_task(self._handle(channel))

    async def _handle(self, channel: discord.abc.GuildChannel):
        try:
            guild = channel.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return
            entry = await self._get_recent_entry(guild, discord.AuditLogAction.webhook_create)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return
            reason = f"AntiNuke: unauthorized webhook by {entry.user}"
            try:
                webhooks = await channel.webhooks()
                for wh in webhooks:
                    if wh.user and wh.user.id == entry.user.id:
                        await wh.delete(reason=reason)
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Webhook Created", entry.user, data["punishment"], {"Channel": channel.name})
            ))
        except Exception as err:
            log.error("antiwebhook: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antiwebhook(client))
