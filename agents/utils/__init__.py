from nextpy.ai import engine
from pathlib import Path
from dotenv import load_dotenv
import os




load_dotenv('secrets/secrets.env')

def initialize_dotagent_client(llm, file_name, memory, **kwargs):
    template = _get_template(file_name)
    client = engine(template=template, llm=llm, memory=memory, **kwargs)
    return client


def _get_template(file_name):
    try:
        return Path(f'./agents/templates/{file_name}.hbs').read_text()
    except FileNotFoundError:
        raise FileNotFoundError('NOTE : Store your templates in ./templates as .hbs files.')