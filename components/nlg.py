import yaml
import ollama
import logging
from utils.history import History

class NLG():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.history = History()
        self.logger = logging.getLogger(__name__)
        with open(self.prompt_path, "r") as file:
            self.system_prompt = yaml.safe_load(file)
    

    def __call__(self, nba_input = " "):


        

        action = self.query_model(nba_input)

        return action
        
    def query_model(self, nba_input: str, system = " "):

        
        messages = [{
            'role': 'system',
            'content': system
        }] 

        messages.append({
            'role': 'user',
            'content': f"History User: {self.history.get_history()}"
        })

        messages.append({
            'role': 'user',
            'content': nba_input
        })

        self.history.add('user', nba_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']
    