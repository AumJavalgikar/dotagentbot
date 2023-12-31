from discord.commands.context import ApplicationContext
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from models.custom_bot import DiscordBot
from discord.ext import commands
from models.views import DnDUtilityView, DnDUtilityAgent


class cog_dnd(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @slash_command(name='dnd', description='Play dungeons and dragons')
    # @commands.cooldown(1, 3, commands.BucketType.user)  # This command can only be user once every 3 seconds
    async def command_name(self, ctx: ApplicationContext):
        view = DnDUtilityView(description='Please enter the theme to generate a prompt for DnD master!', bot=self.bot)
        await ctx.respond(embed=view.embed, view=view)


def setup(client):
    client.add_cog(cog_dnd(client))