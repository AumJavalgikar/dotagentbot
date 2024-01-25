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
    async def nextpythread(self, ctx: ApplicationContext, query: str):
        channel: TextChannel = ctx.channel
        thread = await channel.create_thread(name='Nextpy help', type=discord.ChannelType.public_thread)
        await thread.add_user(ctx.user)
        view = MultiAgentChat(bot=self.bot, thread=thread)
        await thread.send("Thanks for using NextPy! We will be with you shortly.")
        # await ctx.respond('', view=view)
        result = await view.run_chat(query=query)
        await self.send_response(thread, result[-1][1].replace('TERMINATE SUCCESSFULLY', ''))
    
    async def send_response(self, thread, response):
        if len(response) < 2000:
            await thread.send(embed=discord.Embed(description=response))
        else:
            while len(response) >= 2000:
                await thread.send(embed=discord.Embed(description=response[:2000]))
                response = response[2000:]
            await thread.send(embed=discord.Embed(description=response))
        

def setup(client):
    client.add_cog(cog_nextpy_thread(client))