import os
import discord
from discord.ext import commands
import datetime
import logging
import asyncio
import aiohttp
from utils.Tools import getConfig, getanti
from core import Cog, Dilbar

log = logging.getLogger(__name__)


class antiguild(Cog):
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
                    log.info("Antinuke ban %s — %s", user_id, r.status)
            elif punishment == "kick":
                async with session.delete(
                    f"https://discord.com/api/v10/guilds/{guild.id}/members/{user_id}",
                    json={"reason": reason}
                ) as r:
                    log.info("Antinuke kick %s — %s", user_id, r.status)
            elif punishment == "none":
                mem = guild.get_member(user_id)
                if mem:
                    safe_roles = [r for r in mem.roles if not r.permissions.administrator and r != guild.default_role]
                    await mem.edit(roles=safe_roles, reason=reason)
        except discord.Forbidden:
            pass
        except Exception as err:
            log.error("Punish error: %s", err)

    async def _get_recent_entry(self, guild: discord.Guild, action: discord.AuditLogAction):
        after = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)
        async for entry in guild.audit_logs(limit=1, action=action, after=after):
            return entry
        return None

    async def _restore_guild(self, before: discord.Guild, after: discord.Guild, reason: str):
        try:
            kwargs: dict = dict(
                name=before.name,
                description=before.description,
                verification_level=before.verification_level,
                rules_channel=before.rules_channel,
                afk_channel=before.afk_channel,
                afk_timeout=before.afk_timeout,
                default_notifications=before.default_notifications,
                explicit_content_filter=before.explicit_content_filter,
                system_channel=before.system_channel,
                system_channel_flags=before.system_channel_flags,
                public_updates_channel=before.public_updates_channel,
                reason=reason,
            )
            if before.icon:
                kwargs["icon"] = await before.icon.read()
            elif after.icon:
                kwargs["icon"] = None
            await after.edit(**kwargs)
        except Exception as err:
            log.error("Guild restore error: %s", err)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        asyncio.create_task(self._handle_guild_update(before, after))

    async def _handle_guild_update(self, before: discord.Guild, after: discord.Guild):
        try:
            data = getConfig(before.id)
            if getanti(before.id) == "off":
                return
            wled = data["whitelisted"]
            wlrole_id = data.get("wlrole")
            punishment = data["punishment"]

            entry = await self._get_recent_entry(after, discord.AuditLogAction.guild_update)
            if not entry:
                return

            actor = entry.user
            if actor.id == self.client.user.id or actor.id == after.owner_id:
                return
            if str(actor.id) in wled:
                return

            member = after.get_member(actor.id)
            if member and wlrole_id:
                wlrole = after.get_role(wlrole_id)
                if wlrole and wlrole in member.roles:
                    return

            reason = f"AntiNuke: unauthorized guild edit by {actor} ({actor.id})"
            asyncio.create_task(self._restore_guild(before, after, reason))
            asyncio.create_task(self._punish_member(after, actor.id, punishment, reason))

            embed = discord.Embed(
                title="🛡️ Anti-Nuke — Guild Update Detected",
                color=0xFF4444,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Attacker", value=f"{actor.mention} (`{actor.id}`)", inline=True)
            embed.add_field(name="Action Taken", value=punishment.upper(), inline=True)
            embed.add_field(name="Guild Restored", value="✅ Yes", inline=True)
            asyncio.create_task(self._send_antinuke_log(after, embed))
        except Exception as err:
            log.error("_handle_guild_update: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antiguild(client))
