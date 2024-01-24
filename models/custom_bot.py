import discord
from discord.ext import commands
import traceback
import sys
from nextpy.ai import engine
from nextpy.ai.memory import SummaryMemory
from pathlib import Path
from agents import QueryAgent, IntervieweeAgent, InterviewerAgent, DnDAgent, NextpyAgent
from typing import Dict, Tuple, Callable, Any
import os
import requests

def initialize_nextpy_agent(functions_before_call: Tuple[Callable, Tuple[Any], Tuple[Any]]=None, 
                            functions_after_call: Tuple[Callable, Tuple[Any], Tuple[Any]]=None) -> NextpyAgent:
    RAG_api_base = os.getenv('AZURE_ENDPOINT')
    RAG_deployment_id = os.getenv('DEPLOYMENT_ID')
    RAG_api_version = '2023-08-01-preview'
    RAG_llm_requestssession = setup_byod(RAG_api_base, RAG_deployment_id, RAG_api_version)
    nextpy_client = NextpyAgent(requestsession=RAG_llm_requestssession, functions_after_call=functions_after_call, functions_before_call=functions_before_call)
    return nextpy_client

def setup_byod(RAG_api_base, RAG_deployment_id, RAG_api_version):
    
        """Sets up the OpenAI Python SDK to use your own data for the chat endpoint.
    
        :param deployment_id: The deployment ID for the model to use with your own data.
    
        To remove this configuration, simply set openai.requestssession to None.
        """
    
        class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):
    
            def send(byod, request, **kwargs):
                request.url = f"{RAG_api_base}/openai/deployments/{RAG_deployment_id}/extensions/chat/completions?api-version={RAG_api_version}"
                return super().send(request, **kwargs)
    
        session = requests.Session()
    
        # Mount a custom adapter which will use the extensions endpoint for any call using the given deployment_id
        session.mount(
            prefix=f"{RAG_api_base}/openai/deployments/{RAG_deployment_id}",
            adapter=BringYourOwnDataAdapter()
        )
    
        return session

class DiscordBot(commands.Bot):
    def __init__(self, openai_key, *args, **kwargs):
        self.nextpy_client = initialize_nextpy_agent()

        self.llm = engine.llms.OpenAI(
            model="gpt-3.5-turbo",
            api_type="azure",
            api_key=openai_key,
            api_base="https://zenoptestopenai.openai.azure.com/",
            api_version="2023-07-01-preview",
            deployment_id="gpt-35-turbo-dec",
            caching=False,
        )
        self.query_client = QueryAgent(llm=self.llm, memory=SummaryMemory())
        self.interviewer_clients: Dict[int, InterviewerAgent] = {}
        self.interviewee_client = IntervieweeAgent(llm=self.llm, memory=SummaryMemory())
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