from collections import Counter
from typing import Any, Dict, Literal

# Required by Red
import discord
from redbot.core import checks, commands
from redbot.core.bot import Red
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class BadgeTools(commands.Cog):
    """Various commands to show the stats about users' profile badges."""

    __author__ = ["siu3334", "<@306810730055729152>", "Fixator10"]
    __version__ = "0.0.4"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad!"""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    def __init__(self, bot: Red):
        self.bot = bot
        self.emojis = self.bot.loop.create_task(self.init())
        self.valid = [
            "staff",
            "partner",
            "hypesquad",
            "bug_hunter",
            "hypesquad_bravery",
            "hypesquad_brilliance",
            "hypesquad_balance",
            "early_supporter",
            "team_user",
            "system",
            "bug_hunter_level_2",
            "verified_bot",
            "verified_bot_developer",
        ]

    # credits to jack1142
    async def red_get_data_for_user(self, *, user_id: int) -> Dict[str, Any]:
        # this cog does not story any data
        return {}

    # credits to jack1142
    async def red_delete_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> None:
        # this cog does not story any data
        pass

    def cog_unload(self):
        if self.emojis:
            self.emojis.cancel()

    # Credits to flaree (taken from https://github.com/flaree/Flare-Cogs/blob/master/userinfo/userinfo.py#L33)
    # Thanks flare <3
    async def init(self):
        await self.bot.wait_until_ready()
        self.status_emojis = {
            "mobile": discord.utils.get(self.bot.emojis, id=749067110931759185),
            "online": discord.utils.get(self.bot.emojis, id=749221433552404581),
            "away": discord.utils.get(self.bot.emojis, id=749221433095356417),
            "dnd": discord.utils.get(self.bot.emojis, id=749221432772395140),
            "offline": discord.utils.get(self.bot.emojis, id=749221433049088082),
            "streaming": discord.utils.get(self.bot.emojis, id=749221434039205909),
        }
        self.badge_emojis = {
            "staff": discord.utils.get(self.bot.emojis, id=790550232387289088),
            "early_supporter": discord.utils.get(self.bot.emojis, id=706198530837970998),
            "hypesquad_balance": discord.utils.get(self.bot.emojis, id=706198531538550886),
            "hypesquad_bravery": discord.utils.get(self.bot.emojis, id=706198532998299779),
            "hypesquad_brilliance": discord.utils.get(self.bot.emojis, id=706198535846101092),
            "hypesquad": discord.utils.get(self.bot.emojis, id=706198537049866261),
            "verified_bot_developer": discord.utils.get(self.bot.emojis, id=706198727953612901),
            "bug_hunter": discord.utils.get(self.bot.emojis, id=749067110847742062),
            "bug_hunter_level_2": discord.utils.get(self.bot.emojis, id=706199712402898985),
            "partner": discord.utils.get(self.bot.emojis, id=748668634871889930),
            "verified_bot": discord.utils.get(self.bot.emojis, id=710561078488334368),
        }

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def badgecount(self, ctx: commands.Context):
        """Shows the summary of badgecount of the server."""
        guild = ctx.guild

        count = Counter()
        # Credits to Fixator10 for improving this snippet
        # Thanks Fixator <3
        async for usr in AsyncIter(guild.members):
            async for flag in AsyncIter(usr.public_flags.all()):
                count[flag.name] += 1

        pad = len(str(len(ctx.guild.members)))
        msg = "".join(
            f"{self.badge_emojis[k]} `{str(v).zfill(pad)}` : {k.replace('_', ' ').title()}\n"
            for k, v in sorted(count.items())
        )

        e = discord.Embed(colour=await ctx.embed_color())
        e.set_footer(text=f"For Guild: {guild.name}", icon_url=str(guild.icon_url))
        e.add_field(name="Badge Count:", value=msg)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def inbadge(self, ctx: commands.Context, badge: str):
        """Returns the list of users with X profile badge in the server."""

        guild = ctx.guild

        badgeslist = ", ".join(self.valid)
        warn = (
            f"That is invalid Discord user profile badge name!"
            f" It needs to be either of:\n\n{badgeslist}"
        )
        if badge.lower() not in self.valid:
            return await ctx.send(warn)

        list_of = []
        # Thanks Fixator <3
        async for usr in AsyncIter(sorted(guild.members, key=lambda x: x.joined_at)):
            async for flag in AsyncIter(usr.public_flags.all()):
                if flag.name == badge:
                    list_of.append(
                        "{status}  {name}#{tag}\n".format(
                            status=f"{self.status_emojis['mobile']}"
                            if usr.is_on_mobile()
                            else f"{self.status_emojis['streaming']}"
                            if any(
                                a.type is discord.ActivityType.streaming
                                for a in usr.activities
                            )
                            else f"{self.status_emojis['online']}"
                            if usr.status.name == "online"
                            else f"{self.status_emojis['offline']}"
                            if usr.status.name == "offline"
                            else f"{self.status_emojis['dnd']}"
                            if usr.status.name == "dnd"
                            else f"{self.status_emojis['away']}",
                            name=usr.name,
                            tag=usr.discriminator,
                        )
                    )
        output = "".join(list_of)
        total = len([m for m in list_of])

        embed_list = []
        for page in pagify(output, ["\n"], page_length=1000):
            em = discord.Embed(colour=await ctx.embed_color())
            em.description = page
            em.set_footer(text=f"Found {total} users with {badge.replace('_', ' ').title()} badge")
            embed_list.append(em)
        if not embed_list:
            return await ctx.send("No results.")
        elif len(embed_list) == 1:
            return await ctx.send(embed=embed_list[0])
        else:
            await menu(ctx, embed_list, DEFAULT_CONTROLS, timeout=60.0)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def boosters(self, ctx: commands.Context):
        """Returns the list of active boosters of the server."""

        guild = ctx.guild

        b_list = "{status}  {name}#{tag}"
        all_boosters = [
            b_list.format(
                status=f"{self.status_emojis['mobile']}"
                if usr.is_on_mobile()
                else f"{self.status_emojis['streaming']}"
                if any(
                    a.type is discord.ActivityType.streaming
                    for a in usr.activities
                )
                else f"{self.status_emojis['online']}"
                if usr.status.name == "online"
                else f"{self.status_emojis['offline']}"
                if usr.status.name == "offline"
                else f"{self.status_emojis['dnd']}"
                if usr.status.name == "dnd"
                else f"{self.status_emojis['away']}",
                name=usr.name,
                tag=usr.discriminator,
            )
            for usr in sorted(guild.premium_subscribers, key=lambda x: x.premium_since)
        ]
        output = "\n".join(all_boosters)
        footer = (
            f"This server currently has {guild.premium_subscription_count} boosts "
            f"thanks to these {len(guild.premium_subscribers)} awesome people! ❤️"
        )

        embed_list = []
        for page in pagify(output, ["\n"], page_length=1000):
            em = discord.Embed(colour=await ctx.embed_color())
            em.description = page
            em.set_footer(text=footer)
            embed_list.append(em)
        if not embed_list:
            return await ctx.send("No results.")
        elif len(embed_list) == 1:
            return await ctx.send(embed=embed_list[0])
        else:
            await menu(ctx, embed_list, DEFAULT_CONTROLS, timeout=60.0)
