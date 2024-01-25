from typing import Any, Dict, Union
import logging
from agents.utils import _get_template
import openai
import os
from agents.assistant_agent import AssistantAgent


class NextpyAgent(AssistantAgent):

    def __init__(self, requestsession, functions_before_call=None, functions_after_call=None, async_mode=False):
        self.requestsession = requestsession
        self.name = 'Retrival Augmented Nextpy Agent'
        self.functions_before_call= functions_before_call
        self.functions_after_call= functions_after_call
        self.async_mode = async_mode
        # Not calling super.init() here as we don't need an engine for this agent.

    async def arun(self, **kwargs) -> Union[str, Dict[str, Any]]:
        openai.api_base = os.getenv('AZURE_ENDPOINT')  # Add your endpoint here
        openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')  # Add your OpenAI API key here
        deployment_id = os.getenv('DEPLOYMENT_ID')  # Add your deployment ID here

        search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        search_key = os.getenv('AZURE_SEARCH_KEY')
        search_index_name = os.getenv('SEARCH_INDEX_NAME')

        message_text = [{"role": "user", "content": kwargs.get('user_text')}]

        openai.api_type = "azure"
        openai.api_version = "2023-08-01-preview"
        openai.requestssession = self.requestsession

        completion = openai.ChatCompletion.create(
            messages=message_text,
            deployment_id=deployment_id,
            dataSources=[  # camelCase is intentional, as this is the format the API expects
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "key": search_key,
                        "indexName": search_index_name,
                    }
                }
            ]
        )
        print(completion)
        return completion


    def run(self, **kwargs) -> Union[str, Dict[str, Any]]:
        openai.api_base = os.getenv('AZURE_ENDPOINT')  # Add your endpoint here
        openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')  # Add your OpenAI API key here
        deployment_id = os.getenv('DEPLOYMENT_ID')  # Add your deployment ID here

        search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        search_key = os.getenv('AZURE_SEARCH_KEY')
        search_index_name = os.getenv('SEARCH_INDEX_NAME')
        message_text = [{"role": "system", "content": "Read the given conversation and retrieve relevant information."},
                        {"role": "user", "content": kwargs.get('user_text')}]

        openai.api_type = "azure"
        openai.api_version = "2023-08-01-preview"
        openai.requestssession = self.requestsession

        completion = openai.ChatCompletion.create(
            messages=message_text,
            deployment_id=deployment_id,
            dataSources=[  # camelCase is intentional, as this is the format the API expects
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "key": search_key,
                        "indexName": search_index_name,
                    }
                }
            ]
        )
        return completion

    @AssistantAgent.function_call_decorator
    def receive(self, agents, messages, termination_message):
        output = self.run(user_text=messages)
        return output.get('choices')[0].get('message').get('content')
    
    @AssistantAgent.function_call_decorator
    async def a_receive(self, agents, messages, termination_message):
        output = await self.arun(user_text=messages)
        return output.get('choices')[0].get('message').get('content')