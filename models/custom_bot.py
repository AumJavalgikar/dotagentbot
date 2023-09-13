import discord
from discord.ext import commands
import traceback
import sys
from dotagent import compiler
from dotagent.memory import SummaryMemory


class DiscordBot(commands.Bot):
    def __init__(self, openai_key, *args, **kwargs):
        query_llm = compiler.llms.OpenAI(model="gpt-3.5-turbo-16k", api_key=openai_key)
        self.query_client = initialize_dotagent_client(llm=query_llm, file_name='query', memory=SummaryMemory())
        super().__init__(*args, **kwargs)

    async def on_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        exc = ctx.command.qualified_name
        exc += ' caused the following error:\n'
        exc += ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        exc = f'{ctx.command.qualified_name} caused the following error:\n{"".join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))}\n'
        print(exc, file=sys.stderr)


def initialize_dotagent_client(llm, file_name, memory):
    template = get_template(file_name)
    client = compiler(template=template, llm=llm, stream=False, memory=memory)
    return client


def get_template(file_name):
    try:
        with open(file_name) as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError('NOTE : Store your templates in ./templates as .hbs files.')
