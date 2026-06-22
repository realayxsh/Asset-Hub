import discord
import asyncio
import logging
from discord.ext import commands
from utils.Tools import getConfig, getanti
from utils.emojis import e
from core import Dilbar, Cog

log = logging.getLogger(__name__)


class antipinginv(Cog):
    """Anti @everyone / @here ping protection with automod logging."""

    def __init__(self, client: Dilbar):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        if not message.mention_everyone:
            return
        asyncio.create_task(self._handle(message))

    async def _handle(self, message: discord.Message):
        try:
            data = getConfig(message.guild.id)
            if getanti(message.guild.id) == "off":
                return

            wled = data.get("whitelisted", [])
            wlrole_id = data.get("wlrole")
            author = message.author

            if str(author.id) in wled:
                return
            if author.guild_permissions.administrator:
                return
            if wlrole_id:
                wlrole = message.guild.get_role(wlrole_id)
                if wlrole and wlrole in author.roles:
                    return

            try:
                await message.delete()
            except Exception:
                pass

            now = discord.utils.utcnow()
            try:
                await author.timeout(
                    now + __import__("datetime").timedelta(minutes=15),
                    reason="DILBAR < 3 | Anti Everyone/Here Ping"
                )
            except Exception:
                pass

            embed = discord.Embed(
                color=0x2f3136,
                description=(
                    f"{e.green_tick} | {author.mention} was timed out **15 minutes** "
                    f"for pinging **@everyone / @here**"
                )
            )
            try:
                embed.set_author(name=str(author), icon_url=author.display_avatar.url)
            except Exception:
                pass
            await message.channel.send(embed=embed, delete_after=10)

            log_id = data.get("automodlog")
            if log_id:
                ch = message.guild.get_channel(int(log_id))
                if ch:
                    log_embed = discord.Embed(
                        title="🔨 Automod — Mass Ping",
                        color=0xFF8C00,
                        timestamp=discord.utils.utcnow()
                    )
                    log_embed.add_field(name="User", value=f"{author.mention} (`{author.id}`)", inline=True)
                    log_embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                    log_embed.add_field(name="Action", value="Timeout 15min", inline=True)
                    asyncio.create_task(ch.send(embed=log_embed))
        except Exception as err:
            log.error("antiping: %s", err)


async def setup(client: Dilbar):
    await client.add_cog(antipinginv(client))
