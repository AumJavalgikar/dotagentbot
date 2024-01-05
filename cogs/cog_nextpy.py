import asyncio

from discord.commands.context import ApplicationContext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from models.custom_bot import DiscordBot
from nextpy.ai.engine import Program
from discord.ext import commands


class cog_nextpy(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @slash_command(name='nextpy', description='ask anything about nextpy!')
    @commands.cooldown(1, 3, commands.BucketType.user)  # This command can only be user once every 3 seconds
    async def query(self, ctx: ApplicationContext, query: str):
        await ctx.defer()
        response: Program = await self.bot.nextpy_client.run(user_text=query)
        await ctx.respond(response[:2000])


def setup(client):
    client.add_cog(cog_nextpy(client))