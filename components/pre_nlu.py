import yaml
import json
import ollama
import logging
from copy import deepcopy
from utils.history import History


class PreNLU():
    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.logger = logging.getLogger(__name__)
        self.history = History()

    def __call__(self, user_input = " "):
        
        pre_nlu_llama = self.query_model(user_input)

        self.history.add('user', user_input)

        self.logger.debug(f"\nPre NLU llama: \n INPUT-> {self.history.get_history()} \n OUTPUT-> {pre_nlu_llama}\n")

        try:
            pre_nlu_json = json.loads(pre_nlu_llama)
        except:
            self.logger.error("Error parsing NLU response")

        pre_nlu_clean = self.clean_response(pre_nlu_json)
        
        return pre_nlu_clean
    
    
    def clean_response(self, response: dict) -> dict:
        final_dict = deepcopy(response)
        for element in response:
            for key, value in element.items():
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

        system = data["pre_nlu"]["prompt"]
        
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
            'content': user_input
        })

        response = ollama.chat(model=self.model, messages=messages)

        output =  response['message']['content']

        return output
    