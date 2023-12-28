import discord
from discord.ext import commands
import traceback
import sys
from nextpy.ai import engine
from nextpy.ai.memory import SummaryMemory
from pathlib import Path
from agents import QueryAgent, IntervieweeAgent, InterviewerAgent, DnDAgent
from typing import Dict

class DiscordBot(commands.Bot):
    def __init__(self, openai_key, *args, **kwargs):
        llm_azure = engine.llms.OpenAI(
            "gpt-3.5-turbo-dec",
            api_type="azure",
            api_key=openai_key,
            api_base="https://zenoptestopenai.openai.azure.com/",
            api_version="2023-07-01-preview",
            deployment_id="DEPLOYMENT_NAME_IN_AZURE",
            caching=False,
        )
        self.query_client = QueryAgent(llm=llm_azure, memory=SummaryMemory())
        self.interviewer_clients: Dict[int, InterviewerAgent] = {}
        self.interviewee_client = IntervieweeAgent(llm=llm_azure, memory=SummaryMemory())
        self.interviewer_threads = []
        self.interviewee_threads = []
        self.dnd_threads = []
        self.dnd_clients: Dict[int, DnDAgent] = {}
        # self.interview_client = initialize_dotagent_client(llm=query_llm, file_name='interview', memory=SummaryMemory())
        super().__init__(*args, **kwargs)

    async def on_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        exc = ctx.command.qualified_name
        exc += ' caused the following error:\n'
        exc += ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        exc = f'{ctx.command.qualified_name} caused the following error:\n{"".join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))}\n'
        print(exc, file=sys.stderr)



