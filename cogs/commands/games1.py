import discord
from discord.ext import commands


from utils.emojis import e
class devansh96(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Games commands"""
  
    def help_custom(self):
		      emoji = f'{e.games}'
		      label = "Games"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Games__(self, ctx: commands.Context):
        """`akinator` , `chess` , `hangman` , `typerace` , `rps` , `reaction` , `tick-tack-toe` , `wordle` , `2048` , `memory-game` , `number-slider` , `battleship` , `country-guesser`"""