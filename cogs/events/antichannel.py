import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar
from cogs.events._antinuke_base import AntiNukeBase

log = logging.getLogger(__name__)


class antichannel(AntiNukeBase):

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        asyncio.create_task(self._handle_create(channel))

    async def _handle_create(self, channel: discord.abc.GuildChannel):
        try:
            guild = channel.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.channel_create)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return

            reason = f"AntiNuke: unauthorized channel create by {entry.user}"
            try:
                await channel.delete(reason=reason)
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Channel Created", entry.user, data["punishment"], {"Channel": channel.name})
            ))
        except Exception as err:
            log.error("antichannel create: %s", err)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        asyncio.create_task(self._handle_delete(channel))

    async def _handle_delete(self, channel: discord.abc.GuildChannel):
        try:
            guild = channel.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.channel_delete)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return

            reason = f"AntiNuke: unauthorized channel delete by {entry.user}"
            try:
                cloned = await channel.clone(reason=reason)
                await cloned.edit(position=channel.position)
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Channel Deleted", entry.user, data["punishment"], {"Channel": channel.name, "Restored": "✅"})
            ))
        except Exception as err:
            log.error("antichannel delete: %s", err)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        asyncio.create_task(self._handle_update(before, after))

    async def _handle_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        try:
            guild = after.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.channel_update)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return

            reason = f"AntiNuke: unauthorized channel update by {entry.user}"
            try:
                await after.edit(
                    name=before.name,
                    overwrites=before.overwrites,
                    reason=reason,
                )
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Channel Updated", entry.user, data["punishment"], {"Channel": before.name})
            ))
        except Exception as err:
            log.error("antichannel update: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antichannel(client))
