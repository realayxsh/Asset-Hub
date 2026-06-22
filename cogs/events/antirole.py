import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar
from cogs.events._antinuke_base import AntiNukeBase

log = logging.getLogger(__name__)


class antirole(AntiNukeBase):

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        asyncio.create_task(self._handle_create(role))

    async def _handle_create(self, role: discord.Role):
        try:
            guild = role.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.role_create)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return

            reason = f"AntiNuke: unauthorized role create by {entry.user}"
            try:
                await role.delete(reason=reason)
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Role Created", entry.user, data["punishment"], {"Role": role.name})
            ))
        except Exception as err:
            log.error("antirole create: %s", err)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        asyncio.create_task(self._handle_delete(role))

    async def _handle_delete(self, role: discord.Role):
        try:
            guild = role.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.role_delete)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return

            if role.is_bot_managed() or role.is_integration():
                return

            reason = f"AntiNuke: unauthorized role delete by {entry.user}"
            try:
                new_role = await guild.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable,
                    reason=reason,
                )
                await new_role.edit(position=role.position)
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Role Deleted", entry.user, data["punishment"], {"Role": role.name, "Restored": "✅"})
            ))
        except Exception as err:
            log.error("antirole delete: %s", err)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        asyncio.create_task(self._handle_update(before, after))

    async def _handle_update(self, before: discord.Role, after: discord.Role):
        try:
            guild = after.guild
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.role_update)
            if not entry:
                return
            if self._is_safe(entry.user.id, guild, data["whitelisted"], data.get("wlrole")):
                return

            reason = f"AntiNuke: unauthorized role update by {entry.user}"
            try:
                await after.edit(
                    name=before.name,
                    permissions=before.permissions,
                    colour=before.colour,
                    hoist=before.hoist,
                    mentionable=before.mentionable,
                    reason=reason,
                )
            except Exception:
                pass
            asyncio.create_task(self._punish(guild, entry.user.id, data["punishment"], reason))
            asyncio.create_task(self._send_log(
                guild,
                self._log_embed("Role Updated", entry.user, data["punishment"], {"Role": before.name})
            ))
        except Exception as err:
            log.error("antirole update: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antirole(client))
