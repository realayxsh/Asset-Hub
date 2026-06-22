import os
import discord
from discord.ext import commands
from utils.Tools import getConfig, getanti
from core import Dilbar, Cog
import datetime
import logging
import asyncio
import aiohttp
from discord.ext import tasks

log = logging.getLogger(__name__)


class antiban(Cog):
    def __init__(self, client: Dilbar):
        self.client = client
        self.headers = {"Authorization": f"Bot {os.getenv('TOKEN', '')}"}
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def cog_unload(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _send_antinuke_log(self, guild: discord.Guild, embed: discord.Embed):
        try:
            data = getConfig(guild.id)
            log_id = data.get("antinukelog")
            if log_id:
                ch = guild.get_channel(int(log_id))
                if ch:
                    await ch.send(embed=embed)
        except Exception:
            pass

    async def _punish_member(self, guild: discord.Guild, user_id: int, punishment: str, reason: str):
        try:
            session = await self._get_session()
            if punishment == "ban":
                async with session.put(
                    f"https://discord.com/api/v10/guilds/{guild.id}/bans/{user_id}",
                    json={"delete_message_seconds": 0, "reason": reason}
                ) as r:
                    log.info("Antinuke ban %s in %s — status %s", user_id, guild.id, r.status)
            elif punishment == "kick":
                async with session.delete(
                    f"https://discord.com/api/v10/guilds/{guild.id}/members/{user_id}",
                    json={"reason": reason}
                ) as r:
                    log.info("Antinuke kick %s in %s — status %s", user_id, guild.id, r.status)
            elif punishment == "none":
                mem = guild.get_member(user_id)
                if mem:
                    safe_roles = [r for r in mem.roles if not r.permissions.administrator and r != guild.default_role]
                    await mem.edit(roles=safe_roles, reason=reason)
        except discord.Forbidden:
            pass
        except Exception as err:
            log.error("Antinuke punish error: %s", err)

    async def _get_recent_entry(self, guild: discord.Guild, action: discord.AuditLogAction):
        """Fetch the most recent audit log entry for the given action (last 5 seconds)."""
        after = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)
        async for entry in guild.audit_logs(limit=1, action=action, after=after):
            return entry
        return None

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        asyncio.create_task(self._handle_ban(guild, user))

    async def _handle_ban(self, guild: discord.Guild, user: discord.User):
        try:
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return
            wled = data["whitelisted"]
            wlrole_id = data.get("wlrole")
            punishment = data["punishment"]

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.ban)
            if not entry:
                return

            actor = entry.user
            if actor.id == self.client.user.id or actor.id == guild.owner_id:
                return
            if str(actor.id) in wled:
                return

            member = guild.get_member(actor.id)
            if member and wlrole_id:
                wlrole = guild.get_role(wlrole_id)
                if wlrole and wlrole in member.roles:
                    return

            reason = f"AntiNuke: unauthorized ban by {actor} ({actor.id})"
            try:
                await guild.unban(discord.Object(id=user.id), reason=reason)
            except Exception:
                pass

            asyncio.create_task(self._punish_member(guild, actor.id, punishment, reason))

            embed = discord.Embed(
                title="🛡️ Anti-Nuke — Ban Detected",
                color=0xFF4444,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Attacker", value=f"{actor.mention} (`{actor.id}`)", inline=True)
            embed.add_field(name="Victim", value=f"{user.mention} (`{user.id}`)", inline=True)
            embed.add_field(name="Action Taken", value=punishment.upper(), inline=True)
            embed.add_field(name="Victim Unbanned", value="✅ Yes", inline=True)
            asyncio.create_task(self._send_antinuke_log(guild, embed))
        except Exception as err:
            log.error("_handle_ban error: %s", err)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        asyncio.create_task(self._handle_unban(guild, user))

    async def _handle_unban(self, guild: discord.Guild, user: discord.User):
        try:
            data = getConfig(guild.id)
            if getanti(guild.id) == "off":
                return
            wled = data["whitelisted"]
            wlrole_id = data.get("wlrole")
            punishment = data["punishment"]

            entry = await self._get_recent_entry(guild, discord.AuditLogAction.unban)
            if not entry:
                return

            actor = entry.user
            if actor.id == self.client.user.id or actor.id == guild.owner_id:
                return
            if str(actor.id) in wled:
                return

            member = guild.get_member(actor.id)
            if member and wlrole_id:
                wlrole = guild.get_role(wlrole_id)
                if wlrole and wlrole in member.roles:
                    return

            reason = f"AntiNuke: unauthorized unban by {actor} ({actor.id})"
            try:
                await guild.ban(discord.Object(id=user.id), reason=reason)
            except Exception:
                pass

            asyncio.create_task(self._punish_member(guild, actor.id, punishment, reason))

            embed = discord.Embed(
                title="🛡️ Anti-Nuke — Unban Detected",
                color=0xFF8C00,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Attacker", value=f"{actor.mention} (`{actor.id}`)", inline=True)
            embed.add_field(name="Victim", value=f"{user.mention} (`{user.id}`)", inline=True)
            embed.add_field(name="Action Taken", value=punishment.upper(), inline=True)
            asyncio.create_task(self._send_antinuke_log(guild, embed))
        except Exception as err:
            log.error("_handle_unban error: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antiban(client))
