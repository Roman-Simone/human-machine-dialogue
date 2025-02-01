import ollama
import logging
from utils.history import History

class NLG():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.history = History()
        self.logger = logging.getLogger(__name__)
    

    def __call__(self, nba_input = " "):

        # if "confirmation" in nba_input:
        #     nba_input = nba_input.replace("confermation", "confirmation

        action =  self.query_model(nba_input)

        return action
        
    def query_model(self, nba_input: str):

        system= open(self.prompt_path, 'r').read()
        
        messages = [{
            'role': 'system',
            'content': system
        }] #+ self.history.get_history()

        messages.append({
            'role': 'system',
            'content': nba_input
        })

        self.history.add('user', nba_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']
    