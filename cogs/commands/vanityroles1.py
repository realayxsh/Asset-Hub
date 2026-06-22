import discord
from discord.ext import commands


from utils.emojis import e
class devansh7(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Vanityroles commands"""
  
    def help_custom(self):
		      emoji = f'{e.premium}'
		      label = "Vanityroles"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Vanityroles__(self, ctx: commands.Context):
        """`vanityroles` , `vanityroles show` , `vanityroles config` , `vanityroles reset` , `vanityroles setup`"""