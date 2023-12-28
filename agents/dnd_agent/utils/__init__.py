from typing import Any, Dict, Union
from nextpy.ai.agent.base_agent import BaseAgent
import logging
from agents.utils import initialize_dotagent_client
from nextpy.ai import engine


class DnDUtilityAgent(BaseAgent):

    def __init__(self, llm=None, memory=None, **kwargs):
        super().__init__(llm=llm, **kwargs)
        if llm is None:
            llm = engine.llms.OpenAI(model='gpt-3.5-turbo-16k')

        self.theme_agent = initialize_dotagent_client(llm=llm, file_name='theme', memory=memory, async_mode=True)
        self.class_agent = initialize_dotagent_client(llm=llm, file_name='class', memory=memory, async_mode=True)
        self.character_agent = initialize_dotagent_client(llm=llm, file_name='character', memory=memory, async_mode=True)
        self.return_complete = True
    def agent_type(self):
        return "chat"

    async def run(self, gen_type: str, **kwargs) -> Union[str, Dict[str, Any]]:
        """Run the agent to generate a response to the user query."""

        _knowledge_variable = self.get_knowledge_variable

        if _knowledge_variable:
            if kwargs.get(_knowledge_variable):
                query = kwargs.get(_knowledge_variable)
                retrieved_knowledge = self.get_knowledge(query)
                output = self.engine(RETRIEVED_KNOWLEDGE=retrieved_knowledge, **kwargs, silent=True)
            else:
                raise ValueError("knowledge_variable not found in input kwargs")
        else:
            if gen_type.lower() == 'description':
                output = await self.theme_agent(**kwargs)
            elif gen_type.lower() == 'class':
                output = await self.class_agent(**kwargs)
            elif gen_type.lower() == 'character':
                output = await self.character_agent(**kwargs)
            else:
                output = await self.engine(**kwargs)

        if self.return_complete:
            return output
        _output_key = self.output_key if self.output_key is not None else self.get_output_key(output)

        if output.variables().get(_output_key):
            return output[_output_key]
        else:
            logging.warning("Output key not found in output, so full output returned")
            return output
