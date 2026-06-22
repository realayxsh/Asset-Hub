from __future__ import annotations
from discord.ext import commands
from utils.Tools import *
from utils.emojis import e
from discord import *
from utils.config import OWNER_IDS, No_Prefix
import json, discord
import typing
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator

from typing import Optional


class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client
      
    @commands.command(name="slist")
    @commands.is_owner()
    async def slist(self, ctx):
        devansh37 = ([devansh for devansh in self.client.guilds])
        devansh37 = sorted(devansh37,
                         key=lambda devansh: devansh.member_count,
                         reverse=True)
        entries = [
            f"`[{i}]` | [{g.name}](https://discord.com/channels/{g.id}) - {g.member_count}"
            for i, g in enumerate(devansh37, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=f"Server List of DILBAR < 3 - {len(self.client.guilds)}",
            color=0x2f3136,
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    



    @commands.command(name="restart", help="Restarts the client.")
    @commands.is_owner()
    async def _restart(self, ctx: Context):
        await ctx.reply("Restarting!")
        restart_program()
      
    @commands.command(name="sync", help="Syncs all database.")
    @commands.is_owner()
    async def _sync(self, ctx):
        await ctx.reply("Syncing...", mention_author=False)
        with open('anti.json', 'r') as f:
            data = json.load(f)
        for guild in self.client.guilds:
            if str(guild.id) not in data['guild']:
                data['guilds'][str(guild.id)] = 'on'
                with open('anti.json', 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                pass
        with open('config.json', 'r') as f:
            data = json.load(f)
        for op in data["guilds"]:
            g = self.client.get_guild(int(op))
            if not g:
                data["guilds"].pop(str(op))
                with open('config.json', 'w') as f:
                    json.dump(data, f, indent=4)

    @commands.group(name="blacklist",
                    help="let's you add someone in blacklist",
                    aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            with open("blacklist.json") as file:
                blacklist = json.load(file)
                entries = [
                    f"`[{no}]` | <@!{mem}> (ID: {mem})"
                    for no, mem in enumerate(blacklist['ids'], start=1)
                ]
                paginator = Paginator(source=DescriptionEmbedPaginator(
                    entries=entries,
                    title=
                    f"List of Blacklisted users of DILBAR < 3 - {len(blacklist['ids'])}",
                    description="",
                    per_page=10,
                    color=0x2f3136),
                                      ctx=ctx)
                await paginator.paginate()

    @blacklist.command(name="add")
    @commands.is_owner()
    async def blacklist_add(self, ctx: Context, member: discord.Member):
        try:
            with open('blacklist.json', 'r') as bl:
                blacklist = json.load(bl)
                if str(member.id) in blacklist["ids"]:
                    embed = discord.Embed(
                        title="Error!",
                        description=f"{member.name} is already blacklisted",
                        color=discord.Colour(0x2f3136))
                    await ctx.reply(embed=embed, mention_author=False)
                else:
                    add_user_to_blacklist(member.id)
                    embed = discord.Embed(
                        title="Blacklisted",
                        description=f"Successfully Blacklisted {member.name}",
                        color=discord.Colour(0x2f3136))
                    with open("blacklist.json") as file:
                        blacklist = json.load(file)
                        embed.set_footer(
                            text=
                            f"There are now {len(blacklist['ids'])} users in the blacklist"
                        )
                        await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(title="Error!",
                                  description=f"An Error Occurred",
                                  color=discord.Colour(0x2f3136))
            await ctx.reply(embed=embed, mention_author=False)

    @blacklist.command(name="remove")
    @commands.is_owner()
    async def blacklist_remove(self, ctx, member: discord.Member = None):
        try:
            remove_user_from_blacklist(member.id)
            embed = discord.Embed(
                title="User removed from blacklist",
                description=
                f"{e.green_tick} | **{member.name}** has been successfully removed from the blacklist",
                color=0x2f3136)
            with open("blacklist.json") as file:
                blacklist = json.load(file)
                embed.set_footer(
                    text=
                    f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**{member.name}** is not in the blacklist.",
                color=0x2f3136)
            embed.set_thumbnail(url=f"{self.client.user.display_avatar.url}")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.group(
        name="np",
        help="Allows you to add someone in no prefix list (owner only command)"
    )
    @commands.is_owner()
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="list")
    @commands.is_owner()
    async def np_list(self, ctx):
        with open("info.json") as f:
            np = json.load(f)
            nplist = np["np"]
            npl = ([await self.client.fetch_user(nplu) for nplu in nplist])
            npl = sorted(npl, key=lambda nop: nop.created_at)
            entries = [
                f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) (ID: {mem.id})"
                for no, mem in enumerate(npl, start=1)
            ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=f"No Prefix of DILBAR < 3 - {len(nplist)}",
                description="",
                per_page=10,
                color=0x2f3136),
                                  ctx=ctx)
            await paginator.paginate()

    @_np.command(name="add", help="Add user to no prefix")
    @commands.is_owner()
    async def np_add(self, ctx, user: discord.User):
        with open('info.json', 'r') as idk:
            data = json.load(idk)
        np = data["np"]
        if user.id in np:
            embed = discord.Embed(
                description=
                f"**The User You Provided Already In My No Prefix**",
                color=0x2f3136)
            await ctx.reply(embed=embed)
            return
        else:
            data["np"].append(user.id)
        with open('info.json', 'w') as idk:
            json.dump(data, idk, indent=4)
            embed1 = discord.Embed(
                description=
                f"{e.green_tick} | Added no prefix to {user} for all",
                color=0x2f3136)
          
            await ctx.reply(embed=embed1)

    @_np.command(name="remove", help="Remove user from no prefix")
    @commands.is_owner()
    async def np_remove(self, ctx, user: discord.User):
        with open('info.json', 'r') as idk:
            data = json.load(idk)
        np = data["np"]
        if user.id not in np:
            embed = discord.Embed(
                description="**{} is not in no prefix!**".format(user),
                color=0x2f3136)
            await ctx.reply(embed=embed)
            return
        else:
            data["np"].remove(user.id)
        with open('info.json', 'w') as idk:
            json.dump(data, idk, indent=4)
            embed2 = discord.Embed(
                description=
                f"{e.green_tick} | Removed no prefix from {user} for all",
                color=0x2f3136)

            await ctx.reply(embed=embed2)

    @commands.group(name="bdg", help="Allows owner to add badges for a user")
    @commands.is_owner()
    async def _badge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_badge.command(name="add",
                    aliases=["give"],
                    help="Add some badges to a user.")
    @commands.is_owner()
    async def badge_add(self, ctx, member: discord.Member, *, badge: str):
        ok = getbadges(member.id)
        if badge.lower() in ["own", "owner", "king"]:
            idk = f"**{e.king} OWNER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed2 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `OWNER` Badge To {member}**",
                color=0x2f3136)
            await ctx.reply(embed=embed2)
        elif badge.lower() in ["staff", "support staff"]:
            idk = f"**{e.staff_badge} STAFF**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed3 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `STAFF` Badge To {member}**",
                color=0x2f3136)
            await ctx.reply(embed=embed3)
        elif badge.lower() in ["partner"]:
            idk = f"**{e.partners} PARTNER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed4 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `PARTNER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed4)
        elif badge.lower() in ["sponsor"]:
            idk = f"**{e.owners} SPONSER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed5 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `SPONSER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed5)
        elif badge.lower() in [
                "friend", "friends", "homies", "owner's friend"
        ]:
            idk = f"**{e.friends} FRIENDS**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed1 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `FRIENDS` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed1)
        elif badge.lower() in ["early", "supporter", "support"]:
            idk = f"**{e.early_support} SUPPORTER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed6 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `SUPPORTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed6)

        elif badge.lower() in ["vip"]:
            idk = f"**{e.vip_badge} VIP**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed7 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `VIP` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed7)

        elif badge.lower() in ["bug", "hunter"]:
            idk = f"**{e.bug_hunter2} BUG HUNTER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embed8 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `BUG HUNTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed8)
        elif badge.lower() in ["all"]:
            idk = f"**{e.king} OWNER\n{e.staff_badge} STAFF\n{e.partners} PARTNER\n{e.owners} SPONSER\n{e.friends} FRIENDS\n{e.early_support} SUPPORTER\n{e.vip_badge} VIP\n{e.bug_hunter2} BUG HUNTER**"
            ok.append(idk)
            makebadges(member.id, ok)
            embedall = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Added `All` Badges To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embedall)
        else:
            hacker = discord.Embed(
                                   description="**Invalid Badge**",
                                   color=0x2f3136)
            
            await ctx.reply(embed=hacker)

    @_badge.command(name="remove",
                    help="Remove badges from a user.",
                    aliases=["re"])
    @commands.is_owner()
    async def badge_remove(self, ctx, member: discord.Member, *, badge: str):
        ok = getbadges(member.id)
        if badge.lower() in ["own", "owner", "king"]:
            idk = f"**{e.crown} OWNER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed2 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `OWNER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed2)

        elif badge.lower() in ["staff", "support staff"]:
            idk = f"**{e.staff_anim} STAFF**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed3 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `STAFF` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed3)

        elif badge.lower() in ["partner"]:
            idk = f"**{e.partnered_owner} PARTNER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed4 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `PARTNER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed4)

        elif badge.lower() in ["sponsor"]:
            idk = f"**{e.diamond} SPONSER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed5 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `SPONSER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed5)

        elif badge.lower() in [
                "friend", "friends", "homies", "owner's friend"
        ]:
            idk = f"**{e.vip_friends} FRIENDS**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed1 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `FRIENDS` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed1)

        elif badge.lower() in ["early", "supporter", "support"]:
            idk = f"**{e.early_anim} SUPPORTER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed6 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `SUPPORTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed6)

        elif badge.lower() in ["vip"]:
            idk = f"**{e.vip} VIP**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed7 = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `VIP` Badge To {member}**",
                color=0x2f3136)
           
            await ctx.reply(embed=embed7)

        elif badge.lower() in ["bug", "hunter"]:
            idk = f"**{e.bug_anim} BUG HUNTER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embed8 = discord.Embed(
                
                description=
                f"**Successfully Removed `BUG HUNTER` Badge To {member}**",
                color=0x2f3136)
            
            await ctx.reply(embed=embed8)
        elif badge.lower() in ["all"]:
            idk = f"**{e.crown_anim} OWNER\n{e.staff_anim2} STAFF\n{e.partner_anim} PARTNER\n{e.sponsor} SPONSER\n{e.friends2} FRIENDS\n{e.supporter} SUPPORTER\n{e.vip2} VIP\n{e.bug_hunter} BUG HUNTER**"
            ok.remove(idk)
            makebadges(member.id, ok)
            embedall = discord.Embed(
                
                description=
                f"{e.green_tick} | **Successfully Removed `All` Badges From {member}**",
                color=0x2f3136)
            await ctx.reply(embed=embedall)
        else:
            hacker = discord.Embed(
                                   description="**Invalid Badge**",
                                   color=0x2f3136)
            await ctx.reply(embed=hacker)




    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, user: discord.User, *, message: str):
        """ DM the user of your choice """
        try:
            await user.send(message)
            await ctx.send(f"{e.green_tick} | Successfully Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")           



    @commands.group()
    @commands.is_owner()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))
            
            
    @change.command(name="nickname")
    @commands.is_owner()
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"{e.green_tick} | Successfully changed nickname to **{name}**")
            else:
                await ctx.send(f"{e.green_tick} | Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)



    @commands.command()
    @commands.is_owner()
    async def globalban(self, ctx, *, user: discord.User = None):
        if user is None:
            return await ctx.send(
                "You need to define the user"
            )
        for guild in self.client.guilds:
            for member in guild.members:
                if member == user:
                    await user.ban(reason="lund le lo")
               
        
