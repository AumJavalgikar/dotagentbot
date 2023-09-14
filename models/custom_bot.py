import discord
from discord.ext import commands
import traceback
import sys
from dotagent import compiler
from dotagent.memory import SummaryMemory
from pathlib import Path
from agents import QueryAgent, IntervieweeAgent, InterviewerAgent


class DiscordBot(commands.Bot):
    def __init__(self, openai_key, *args, **kwargs):
        open_ai_llm = compiler.llms.OpenAI(model="gpt-3.5-turbo-16k", api_key=openai_key)
        self.query_client = QueryAgent(llm=open_ai_llm, memory=SummaryMemory())
        self.interviewer_client = InterviewerAgent(llm=open_ai_llm, memory=SummaryMemory())
        self.interviewee_client = IntervieweeAgent(llm=open_ai_llm, memory=SummaryMemory())
        self.interviewer_threads = []
        self.interviewee_threads = []
        # self.interview_client = initialize_dotagent_client(llm=query_llm, file_name='interview', memory=SummaryMemory())
        super().__init__(*args, **kwargs)

    async def on_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        exc = ctx.command.qualified_name
        exc += ' caused the following error:\n'
        exc += ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        exc = f'{ctx.command.qualified_name} caused the following error:\n{"".join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))}\n'
        print(exc, file=sys.stderr)



