import yaml
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

        ret_nlu_cleaned = []

        nlu_response = self.query_model(user_input)

        try:
            nlu_response_json = json.loads(nlu_response)
        except:
            self.logger.error("Error parsing NLU response")
        
        if type(nlu_response_json) is list:
            for intent in nlu_response_json:
                nlu_cleaned_response = self.clean_response(intent)
                ret_nlu_cleaned.append(nlu_cleaned_response)
        elif type(nlu_response_json) is dict:
            nlu_cleaned_response = self.clean_response(nlu_response_json)
            ret_nlu_cleaned.append(nlu_cleaned_response)
        
        return ret_nlu_cleaned

    def clean_response(self, response: dict) -> dict:
            final_dict = deepcopy(response)
            for key, value in response.items():
                if value == None:
                    final_dict[key] = "null"
                elif isinstance(value, dict):
                    cleaned_dict = self.clean_response(deepcopy(value))
                    if len(cleaned_dict) == 0:
                        del final_dict[key]
                    else:
                        final_dict[key] = cleaned_dict
            return final_dict
        
    def query_model(self, user_input: str):

        with open(self.prompt_path, "r") as file:
            data = yaml.safe_load(file)

        system = data["nlu"]["prompt"]
        
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