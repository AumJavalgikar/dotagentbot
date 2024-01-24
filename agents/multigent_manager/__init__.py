from typing import List, Optional

from nextpy.ai.agent.base_agent import BaseAgent

from agents.utils import initialize_dotagent_client


class MultiAgentManager:

    def __init__(self,
                 agents: List[BaseAgent],
                 messages: Optional[List[str]] = None,
                 termination_message: str = 'TERMINATE SUCCESSFULLY',
                 error_message: str = 'ERROR',
                 mode: str = 'BROADCAST',
                 rounds: int = 5,
                 round_robin: bool = True,
                 llm=None,
                 memory=None,
                 async_mode=False):

        if messages is None:
            messages = []

        self.engine = initialize_dotagent_client(
            llm=llm, file_name='multiagent_manager', memory=memory, async_mode=async_mode)
        self.solution_summarizer = initialize_dotagent_client(
            llm=llm, file_name='solution_summarizer', memory=memory, async_mode=async_mode)

        self.agents = agents
        self.agent_dict = {agent.name: agent for agent in agents}
        self.messages = messages
        self.termination_message = termination_message
        self.error_message = error_message
        self.mode = mode
        self.rounds = rounds
        self.round_robin = round_robin
        self.current_agent = 0  # Used to keep track of next agent in sequence

    @property
    def agent_string(self):
        return ','.join([agent.name for agent in self.agents])

    def run_sequence(self, context):
        self.messages.append(['User', context])
        while self.rounds > 0 and not self._termination_message_received():

            print(
                f'{"-"*5}Messaging next agent : {self.agents[self.current_agent].name}{"-"*5}\n\n')

            self._message_next_agent()

            print(f'{self.messages[-1][0]}\n\n{self.messages[-1][1]}')

            if self.current_agent == 0 and not self.round_robin:
                break

            self.rounds -= 1
        return self.messages
    
    async def a_run_sequence(self, context):
        self.messages.append(['User', context])
        while self.rounds > 0 and not self._termination_message_received():

            print(
                f'{"-"*5}Messaging next agent : {self.agents[self.current_agent].name}{"-"*5}\n\n')

            await self._a_message_next_agent()

            print(f'{self.messages[-1][0]}\n\n{self.messages[-1][1]}')

            if self.current_agent == 0 and not self.round_robin:
                break

            self.rounds -= 1
        return self.messages

    def run_auto(self, context):
        self.messages.append(['User', context])
        while self.rounds > 0 and not self._termination_message_received():
            next_agent = self._choose_next_agent()
            print(f'{"-" * 5}Messaging next agent : {next_agent}{"-" * 5}\n\n')

            self._message_next_agent(next_agent)

            print(f'{self.messages[-1][0]}\n\n{self.messages[-1][1]}')

            self.rounds -= 1
        final_solution = self.solution_summarizer(
            messages=self._parse_messages()).get('answer')
        print(final_solution)
        return [self.messages, final_solution]

    async def _a_message_next_agent(self, next_agent=None):
        if next_agent is None:
            next_agent = self.agents[self.current_agent]
            self.current_agent = (self.current_agent + 1) % len(self.agents)
        
        if next_agent.async_mode:
            received_message = await next_agent.a_receive(
                self.agent_string, self._parse_messages(), self.termination_message)
        else:
            received_message = next_agent.receive(
                self.agent_string, self._parse_messages(), self.termination_message)
    
        self.messages.append([next_agent.name, received_message])

    def _message_next_agent(self, next_agent=None):
        if next_agent is None:
            next_agent = self.agents[self.current_agent]
            self.current_agent = (self.current_agent + 1) % len(self.agents)
              
        assert not next_agent.async_mode, "Don't use run_sequence for async agents, use a_run_sequence instead"
        
        received_message = next_agent.receive(
            self.agent_string, self._parse_messages(), self.termination_message)
        
        self.messages.append([next_agent.name, received_message])

    def _termination_message_received(self):
        return self.termination_message in self.messages[-1][1]

    def _parse_messages(self):
        return f'\n\n{"-"*20}'.join([f'{index}) {message[0]}\n{message[1]}' for index, message in enumerate(self.messages)])

    def _choose_next_agent(self):
        output = self.engine(agents=self.agent_string,
                             messages=self._parse_messages())
        print(f"Chosen next agent as {output.get('answer')}")
        return self.agent_dict[output.get('answer')]
