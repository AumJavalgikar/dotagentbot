from dotagent.memory import BaseMemory
from pydantic import BaseModel
from typing import List, Dict, Any
from dotagent.schema import BaseMessage
from .prompt import INTERVIEWER_SUMMARIZER_TEMPLATE
from dotagent import compiler
from pydantic import Field


def extract_text(string):
    """function for getting the user prompt and llm response from the compiler output"""
    end_string="<|im_end|>"
    start_string="New summary:<|im_end|>\n\n<|im_start|>assistant\n"
    string = string.replace(start_string, "", 1)
    start_index = string.find(start_string)
    end_index = string.find(end_string, start_index + len(start_string))
    return string[start_index + len(start_string):end_index]


class InterviewerMemory(BaseMemory, BaseModel):
    current_summary: str = ""
    messages_in_summary: List[Dict[BaseMessage, Any]] = []
    max_questions: int = Field()
    interview_goals: list = Field()

    def add_memory(self, prompt: str, llm_response: Any) -> None:
        """Add a self-created message to the store"""
        for conversation in self.messages:
            if conversation['prompt'] == prompt and conversation['llm_response'] == llm_response:
                break
        else:
            self.messages.append({'prompt': prompt, 'llm_response': llm_response})

    def get_memory(self, **kwargs) -> str:
        """Retrieve entire memory from the store."""

        # Create llm instance
        llm = compiler.llms.OpenAI(model="gpt-3.5-turbo")

        new_messages = [item for item in self.messages if item not in self.messages_in_summary]
        if len(new_messages) != 0:
            messages_to_text = ""
            for conversation in new_messages:
                messages_to_text = messages_to_text + "\n" + "Interviewee response to last question:" + conversation['prompt'] + "\n" + "Interviewer next response:" + conversation[
                    'llm_response'] + "\n"
                self.messages_in_summary.append(conversation)

            summarizer = compiler(template=INTERVIEWER_SUMMARIZER_TEMPLATE, llm=llm, stream=False,
                                  max_questions=self.max_questions, interview_goals=self.interview_goals, async_mode=True)
            summarized_memory = summarizer(summary=self.current_summary, new_lines=messages_to_text)
            print(f'current summary : {summarizer.get("result")}')
            self.current_summary = extract_text(summarized_memory.text)
            summarized_memory = "Current conversation:\n" + self.current_summary

        else:
            summarized_memory = self.current_summary

        return summarized_memory

    def remove_memory(self, prompt: str, llm=Any) -> None:
        """Remove a memory from the store."""

        for conversation in self.messages:
            if conversation['prompt'] == prompt:
                # update messages
                self.messages.remove(conversation)

                # update current summary
                if len(self.messages) != 0:
                    messages_to_text = ""
                    self.messages_in_summary.clear()
                    for conversation in self.messages:
                        messages_to_text = messages_to_text + "\n" + "Interviewer: " + conversation[
                            'llm_response'] + "Interviewee: " + conversation['prompt'] + "\n"
                        self.messages_in_summary.append(conversation)

                    summarizer = compiler(template=INTERVIEWER_SUMMARIZER_TEMPLATE, llm=llm, stream=False,
                                  max_questions=self.max_questions, interview_goals=self.interview_goals, async_mode=True)
                    summarized_memory = await summarizer(summary="", new_lines=messages_to_text)
                    summarized_memory = "Current conversation:\n" + extract_text(summarized_memory.text)
                    self.current_summary = summarized_memory

                else:
                    self.current_summary = ""

                break

    def clear(self) -> None:
        """Clear all memories."""
        self.messages.clear()
        self.messages_in_summary.clear()
        self.current_summary = ""