from dotagent import compiler
from pathlib import Path


def initialize_dotagent_client(llm, file_name, memory):
    template = _get_template(file_name)
    client = compiler(template=template, llm=llm, memory=memory, async_mode=True)
    return client


def _get_template(file_name):
    try:
        return Path(f'./templates/{file_name}.hbs').read_text()
    except FileNotFoundError:
        raise FileNotFoundError('NOTE : Store your templates in ./templates as .hbs files.')