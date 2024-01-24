import asyncio
import discord
from discord.commands.context import ApplicationContext
from discord.commands import (slash_command,message_command)
from models.custom_bot import DiscordBot
from models.views import MultiAgentChat
from discord.ext import commands
from discord import TextChannel


class cog_nextpy_thread(commands.Cog):

    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @slash_command(name='nextpythread', description='Starts a context based thread to solve nextpy issues')
    @commands.cooldown(1, 3, commands.BucketType.user)  # This command can only be used once every 3 seconds
    async def query(self, ctx: ApplicationContext, query: str):
        channel: TextChannel = ctx.channel
        thread = await channel.create_thread(name=self.title, type=discord.ChannelType.public_thread)
        await thread.add_user(ctx.user)
        view = MultiAgentChat(bot=self.bot, thread=thread)
        await thread.send("Thanks for using NextPy! We will be with you shortly.")
        result = view.run_chat(query=query)    
        await thread.send(result[-1][1].replace('TERMINATE SUCCESSFULLY', ''))

def setup(client):
    client.add_cog(cog_nextpy_thread(client))