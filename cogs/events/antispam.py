import discord
from discord.ext import commands
import datetime
import re
import asyncio
import logging
from core import Dilbar, Cog
from utils.Tools import getConfig, getanti
from utils.emojis import e

log = logging.getLogger(__name__)


class AntiSpam(Cog):
    def __init__(self, client: Dilbar):
        self.client = client
        self.spam_cd = commands.CooldownMapping.from_cooldown(4, 7, commands.BucketType.member)

    def _is_exempt(self, message: discord.Message, data: dict) -> bool:
        wled = data.get("whitelisted", [])
        wlrole_id = data.get("wlrole")
        author = message.author
        if str(author.id) in wled:
            return True
        if getattr(author, "guild_permissions", None) and author.guild_permissions.administrator:
            return True
        if wlrole_id:
            wlrole = message.guild.get_role(wlrole_id)
            if wlrole and wlrole in author.roles:
                return True
        return False

    async def _send_automod_log(self, guild: discord.Guild, embed: discord.Embed):
        try:
            ch_id = getConfig(guild.id).get("automodlog")
            if ch_id:
                ch = guild.get_channel(int(ch_id))
                if ch:
                    await ch.send(embed=embed)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        asyncio.create_task(self._handle(message))

    async def _handle(self, message: discord.Message):
        try:
            data = getConfig(message.guild.id)
            if self._is_exempt(message, data):
                return

            invite_re = re.compile(r"(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?")
            link_re   = re.compile(r"https?://\S+")
            author    = message.author
            now       = discord.utils.utcnow()

            # ── Anti-Spam ──────────────────────────────────────────────
            if data.get("antiSpam"):
                bucket = self.spam_cd.get_bucket(message)
                retry  = bucket.update_rate_limit()
                if retry:
                    try:
                        await author.timeout(
                            now + datetime.timedelta(minutes=15),
                            reason="DILBAR < 3 | Anti Spam"
                        )
                    except Exception:
                        pass
                    embed = discord.Embed(
                        color=0x2f3136,
                        description=f"{e.green_tick} | {author.mention} muted **15 min** for spamming"
                    )
                    try:
                        embed.set_author(name=str(author), icon_url=author.display_avatar.url)
                    except Exception:
                        pass
                    await message.channel.send(embed=embed, delete_after=8)

                    log_embed = discord.Embed(
                        title="🔨 Automod — Spam Detected",
                        color=0xFF8C00,
                        timestamp=now
                    )
                    log_embed.add_field(name="User", value=f"{author.mention} (`{author.id}`)", inline=True)
                    log_embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                    log_embed.add_field(name="Action", value="Timeout 15min", inline=True)
                    asyncio.create_task(self._send_automod_log(message.guild, log_embed))
                    return

            # ── Anti-Link ──────────────────────────────────────────────
            if data.get("antiLink"):
                invite_matches = invite_re.findall(message.content)
                link_matches   = link_re.findall(message.content)

                if invite_matches or link_matches:
                    try:
                        await message.delete()
                    except Exception:
                        pass
                    reason = "DILBAR < 3 | Anti Discord Invites" if invite_matches else "DILBAR < 3 | Anti Link"
                    try:
                        await author.timeout(now + datetime.timedelta(minutes=15), reason=reason)
                    except Exception:
                        pass
                    label = "invite link" if invite_matches else "external link"
                    embed = discord.Embed(
                        color=0x2f3136,
                        description=f"{e.green_tick} | {author.mention} muted **15 min** for posting a {label}"
                    )
                    try:
                        embed.set_author(name=str(author), icon_url=author.display_avatar.url)
                    except Exception:
                        pass
                    await message.channel.send(embed=embed, delete_after=8)

                    log_embed = discord.Embed(
                        title="🔨 Automod — Link Blocked",
                        color=0xFF8C00,
                        timestamp=now
                    )
                    log_embed.add_field(name="User", value=f"{author.mention} (`{author.id}`)", inline=True)
                    log_embed.add_field(name="Type", value=label.title(), inline=True)
                    log_embed.add_field(name="Action", value="Timeout 15min", inline=True)
                    asyncio.create_task(self._send_automod_log(message.guild, log_embed))
        except Exception as err:
            log.error("antispam: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(AntiSpam(client))
