import json
import ollama
import logging
from copy import deepcopy
from utils.history import History

class NLU():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.prompt_path = prompt_path
        self.history = History()
    
    def __call__(self, user_input = " "):

        nlu_response = self.query_model(user_input)

        try:
            response = json.loads(nlu_response)
        except:
            self.logger.error("Error parsing NLU response")
        
        nlu_cleaned_response = self.clean_response(response)
        
        return nlu_cleaned_response

    def clean_response(self, response: dict) -> dict:
            final_dict = deepcopy(response)
            for key, value in response.items():
                if value == None:
                    del final_dict[key]
                elif isinstance(value, dict):
                    cleaned_dict = self.clean_response(deepcopy(value))
                    if len(cleaned_dict) == 0:
                        del final_dict[key]
                    else:
                        final_dict[key] = cleaned_dict
            return final_dict
        
    def query_model(self, user_input: str):

        system= open(self.prompt_path, 'r').read()
        
        messages = [{
            'role': 'system',
            'content': system
        }] #+ self.history.get_history()

        messages.append({
            'role': 'user',
            'content': user_input
        })

        self.history.add('user', user_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']