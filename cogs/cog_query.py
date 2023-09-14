import asyncio

from discord.commands.context import ApplicationContext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from models.custom_bot import DiscordBot
from dotagent.compiler import Program
from discord.ext import commands
from dotenv import load_dotenv
import os
from dotagent import compiler
from agents import QueryAgent
from dotagent.memory import SummaryMemory


class cog_query(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @slash_command(name='query', description='query the agent')
    @commands.cooldown(1, 3, commands.BucketType.user)  # This command can only be user once every 3 seconds
    async def query(self, ctx: ApplicationContext, query: str):
        await ctx.defer()
        response: Program = await self.bot.query_client.run(query=query)
        await ctx.respond(response)


def setup(client):
    client.add_cog(cog_query(client))