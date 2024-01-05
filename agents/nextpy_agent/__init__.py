from typing import Any, Dict, Union
import logging
from agents.utils import _get_template
import openai
import os


class NextpyAgent():

    def __init__(self, requestsession):
        self.requestsession = requestsession

    async def run(self, **kwargs) -> Union[str, Dict[str, Any]]:
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
