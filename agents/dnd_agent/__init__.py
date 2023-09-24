from typing import Any, Dict, Union
from dotagent.agent.base_agent import BaseAgent
import logging
from agents.utils import initialize_dotagent_client
from .utils import DnDUtilityAgent
from dotagent import compiler
from dotagent.compiler import Program


class DnDAgent(BaseAgent):

    def __init__(self, system_prompt,
                 final_class,
                 final_race,
                 final_area,
                 final_attributes,
                 llm=None, memory=None, **kwargs):
        super().__init__(**kwargs)
        if llm is None:
            llm = compiler.llms.OpenAI(model='gpt-3.5-turbo-16k')
        self.system_prompt = system_prompt
        self.player_class = final_class,
        self.player_race = final_race,
        self.current_area = final_area,
        self.final_attributes = final_attributes,
        self.compiler: Program = initialize_dotagent_client(llm=llm, file_name='dnd', memory=memory, async_mode=True)
        self.output_key = 'followup'

    def agent_type(self):
        return "chat"

    async def run(self, **kwargs) -> Union[str, Dict[str, Any]]:
        """Run the agent to generate a response to the user query."""

        _knowledge_variable = self.get_knowledge_variable

        if _knowledge_variable:
            if kwargs.get(_knowledge_variable):
                query = kwargs.get(_knowledge_variable)
                retrieved_knowledge = self.get_knowledge(query)
                output = self.compiler(RETRIEVED_KNOWLEDGE=retrieved_knowledge, **kwargs, silent=True)
            else:
                raise ValueError("knowledge_variable not found in input kwargs")
        else:
            output = await self.compiler(dungeon_master_info=self.system_prompt, **kwargs)

        if self.return_complete:
            return output
        print(f'Output of entire query : {output}')
        _output_key = self.output_key if self.output_key is not None else self.get_output_key(output)

        if output.variables().get(_output_key):
            return output[_output_key]
        else:
            logging.warning("Output key not found in output, so full output returned")
            return output
