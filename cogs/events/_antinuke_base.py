"""Shared base class for all anti-nuke event cogs."""
from __future__ import annotations
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


class AntiNukeBase(Cog):
    """Base class providing a persistent aiohttp session, punish, and log helpers."""

    def __init__(self, client: Dilbar):
        self.client = client
        self._headers = {"Authorization": f"Bot {os.getenv('TOKEN', '')}"}
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self._session

    async def cog_unload(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _is_safe(
        self,
        actor_id: int,
        guild: discord.Guild,
        wled: list,
        wlrole_id,
    ) -> bool:
        if actor_id == self.client.user.id:
            return True
        if actor_id == guild.owner_id:
            return True
        if str(actor_id) in wled:
            return True
        if wlrole_id:
            mem = guild.get_member(actor_id)
            if mem:
                wlrole = guild.get_role(wlrole_id)
                if wlrole and wlrole in mem.roles:
                    return True
        return False

    async def _get_recent_entry(
        self,
        guild: discord.Guild,
        action: discord.AuditLogAction,
        seconds: int = 5,
    ):
        after = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=seconds)
        async for entry in guild.audit_logs(limit=1, action=action, after=after):
            return entry
        return None

    async def _punish(
        self,
        guild: discord.Guild,
        actor_id: int,
        punishment: str,
        reason: str,
    ):
        try:
            session = await self._get_session()
            if punishment == "ban":
                async with session.put(
                    f"https://discord.com/api/v10/guilds/{guild.id}/bans/{actor_id}",
                    json={"delete_message_seconds": 0, "reason": reason},
                ) as r:
                    log.info("AntiNuke BAN %s in %s → %s", actor_id, guild.id, r.status)
            elif punishment == "kick":
                async with session.delete(
                    f"https://discord.com/api/v10/guilds/{guild.id}/members/{actor_id}",
                    json={"reason": reason},
                ) as r:
                    log.info("AntiNuke KICK %s in %s → %s", actor_id, guild.id, r.status)
            elif punishment == "none":
                mem = guild.get_member(actor_id)
                if mem:
                    safe = [
                        r for r in mem.roles
                        if not r.permissions.administrator and r != guild.default_role
                    ]
                    await mem.edit(roles=safe, reason=reason)
        except discord.Forbidden:
            pass
        except Exception as err:
            log.error("_punish: %s", err)

    async def _send_log(self, guild: discord.Guild, embed: discord.Embed):
        try:
            ch_id = getConfig(guild.id).get("antinukelog")
            if ch_id:
                ch = guild.get_channel(int(ch_id))
                if ch:
                    await ch.send(embed=embed)
        except Exception:
            pass

    def _log_embed(
        self,
        title: str,
        actor: discord.User | discord.Member,
        punishment: str,
        extra: dict | None = None,
    ) -> discord.Embed:
        embed = discord.Embed(
            title=f"🛡️ Anti-Nuke — {title}",
            color=0xFF4444,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Attacker", value=f"{actor.mention} (`{actor.id}`)", inline=True)
        embed.add_field(name="Punishment", value=punishment.upper(), inline=True)
        if extra:
            for k, v in extra.items():
                embed.add_field(name=k, value=str(v), inline=True)
        return embed
