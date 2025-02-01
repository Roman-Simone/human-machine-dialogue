import yaml
import ollama
import logging
from utils.history import History


class PreNLU():
    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.logger = logging.getLogger(__name__)
        self.history = History()

    def __call__(self, user_input = " "):
        
        
        pre_nlu = self.query_model(user_input)
        return pre_nlu
    

    def query_model(self, user_input: str):
        

        system = yaml.safe_load(self.prompt_path)

        system = system['pre_nlu']['prompt']
        
        messages = [{
            'role': 'system',
            'content': system
        }] + self.history.get_history()

        messages.append({
            'role': 'user',
            'content': user_input
        })

        self.history.add('user', user_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']
    