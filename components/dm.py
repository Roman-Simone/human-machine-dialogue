import ollama
from utils.history import History

class DM():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.history = History()

    def __call__(self, nlu_input = " "):
        return self.query_model(nlu_input)
        
    def query_model(self, nlu_input: str):

        system= open(self.prompt_path, 'r').read()
        
        messages = [{
            'role': 'system',
            'content': system
        }] #+ self.history.get_history()

        messages.append({
            'role': 'system',
            'content': nlu_input
        })

        self.history.add('user', nlu_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']