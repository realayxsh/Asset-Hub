import discord
from discord.ext import commands


from utils.emojis import e
class ver1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Verification Commands"""
  
    def help_custom(self):
		      emoji = f'{e.verified}'
		      label = "Verification"
		      description = "Show You Commands Of Verification"
		      return emoji, label, description

    @commands.group()
    async def __Verification__(self, ctx: commands.Context):
        """`verification enable` , `verification disable` , `verification config`"""