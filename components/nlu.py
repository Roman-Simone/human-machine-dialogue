import ollama
from utils.history import History

class NLU():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.history = History()
    
    def __call__(self, user_input = " "):
        return self.query_model(user_input)
        

    def query_model(self, user_input: str):

        system= open(self.prompt_path, 'r').read()
        
        messages = [{
            'role': 'system',
            'content': system
        }]

        messages.append({
            'role': 'user',
            'content': user_input
        })

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']