from discord.commands.context import ApplicationContext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from models.custom_bot import DiscordBot
from discord.ext import commands


class cog_interview(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @slash_command(name='interview', description='desc')
    # @commands.cooldown(1, 3, commands.BucketType.user)  # This command can only be user once every 3 seconds
    async def interview(self, ctx: ApplicationContext):
        pass


def setup(client):
    client.add_cog(cog_interview(client))