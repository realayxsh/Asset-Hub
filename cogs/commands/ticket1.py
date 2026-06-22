import discord
from discord.ext import commands
import json

from utils.emojis import e
class devansh16(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Ticket commands"""  

    def help_custom(self):
		      emoji = f'{e.ticket}'
		      label = "Ticket"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Tickets__(self, ctx: commands.Context):
        """`sendpanel`"""
       
    

    
   

