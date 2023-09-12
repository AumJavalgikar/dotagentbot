import datetime
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from discord import Option
from discord import OptionChoice
import traceback
import sys
from openagent import compiler
from openagent.memory import SummaryMemory
import asyncio
import importlib


load_dotenv('secrets/secrets.env')
TOKEN = os.getenv('DISCORD_TOKEN')
dev_id = os.getenv('DEV_ID')
guild_ids = map(int, os.getenv('GUILD_IDS').split(','))
openai_key = os.getenv('OPENAI_KEY')
intents = discord.Intents.default()


class DiscordBot(commands.Bot):
    def __init__(self):
        self.openagent_client = initialize_dotagent_client()
        super().__init__(intents=intents)
        self.persistent_views_added = False

    async def on_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        exc = ctx.command.qualified_name
        exc += ' caused the following error:\n'
        exc += ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        exc = f'{ctx.command.qualified_name} caused the following error:\n{"".join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))}\n'
        print(exc, file=sys.stderr)


bot = DiscordBot()


def initialize_dotagent_client():
    llm = compiler.llms.OpenAI(model="gpt-3.5-turbo-16k", api_key=openai_key)
    memory = SummaryMemory()
    client = compiler(template='''{{#system~}} You are a helpful and friendly AI bot of 'dotagent technologies', 
    their manifesto is "We have a dream: Open and democratic AGI , free from blackbox censorship and control imposed 
    by private corporations under the disguise of alignment. We once had this with the web but lost this liberty to 
    the corporate giants of the mobile era, whose duopoly has imposed a fixed 30% tax on all developers. Our moonshot 
    : A network of domain specific AI agents , collaborating so seamlessly that it feels like AGI. Contribute to 
    democratizing the LAST technological frontier.". {{~/system}} 

    {{#user~}}
    I want a response to the following question:
    {{query}}
    Answer the question in a friendly and cheerful manner.
    {{~/user}}

    {{#assistant~}}
    {{gen 'answer' temperature=0 max_tokens=500}}
    {{~/assistant}}
    ''', llm=llm, stream=False, memory=memory)
    return client


def check_if_it_is_me(ctx):
    return ctx.author.id == dev_id


@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    await bot.change_presence(activity=discord.Game('dotagent'))


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond("This command is currently on cooldown.")
    else:
        raise error


@bot.slash_command(name='load', description='Load a cog', guild_ids=guild_ids)
@commands.check(check_if_it_is_me)
async def _load(ctx, extension:  Option(
                str,
                choices=[OptionChoice(name=filename.strip('.py')) for filename in os.listdir('./cogs') if filename.endswith('.py')])
                  ):
    try:
        await ctx.defer()
        bot.load_extension(f'cogs.{extension}')
        cog = bot.get_cog(f'{extension}')
        commands = cog.get_commands()
        # print(cog)
        # print(commands)
        for cmd in commands:
            bot.add_application_command(cmd)
        await bot.sync_commands(bot.application_commands, force=True)
        bot.reload_extension(f'cogs.{extension}')
        await ctx.send("command added!")
        # bot.reload_extension(f'cogs.{extension}')
        await ctx.respond(f'loaded cog {extension}')
    except discord.errors.ExtensionAlreadyLoaded:
        await ctx.respond(f'cog is already loaded')
    except discord.errors.ExtensionNotFound:
        await ctx.respond(f'cog does not exist!')


@bot.slash_command(name='unload', description='unload a cog', guild_ids=guild_ids)
@commands.check(check_if_it_is_me)
async def _unload(ctx, extension:  Option(
                str,
                choices=[OptionChoice(name=filename.strip('.py')) for filename in os.listdir('./cogs') if filename.endswith('.py')])
                  ):
    try:
        await ctx.defer()
        cog = bot.get_cog(f'{extension}')
        bot.unload_extension(f'cogs.{extension}')
        commands = cog.get_commands()
        # print(cog)
        # print(commands)
        # return
        for cmd in commands:
            bot.remove_application_command(cmd)
        await bot.sync_commands(bot.application_commands, force=True)
        await ctx.send("command removed!")
        await ctx.respond(f'unloaded cog {extension}')
    except discord.errors.ExtensionNotLoaded:
        await ctx.respond(f'cog is already unloaded')
    except discord.errors.ExtensionNotFound:
        await ctx.respond(f'cog does not exist!')


@bot.slash_command(name='reload', description='reload a cog', guild_ids=guild_ids)
@commands.check(check_if_it_is_me)
async def _reload(ctx,
                  extension:  Option(
                str,
                choices=[OptionChoice(name=filename.strip('.py')) for filename in os.listdir('./cogs') if filename.endswith('.py')])
                  ):
    try:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.respond(f'reloaded cog {extension}')
    except discord.errors.ExtensionNotLoaded:
        bot.load_extension(f'cogs.{extension}')
        await ctx.respond(f'reloaded cog {extension}')
    except discord.errors.ExtensionNotFound:
        await ctx.respond(f'cog does not exist!')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)