import re
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
        with open(self.prompt_path, "r") as file:
            self.system_prompt = yaml.safe_load(file)


    def __call__(self, user_input = " ", system_response = " ") -> dict:
        
        flag_repeat = True

        self.history.add('system', system_response)

        while(flag_repeat):

            pre_nlu_llama = self.query_model(user_input)

            try:
                pre_nlu_llama_clean = self.clean_json_string(pre_nlu_llama)
                pre_nlu_json = json.loads(pre_nlu_llama_clean)
                pre_nlu_clean = self.clean_response(pre_nlu_json)
                flag_repeat = False
            except:
                self.logger.error("Error parsing PRE-NLU response")

        self.history.add('user', user_input)

        self.logger.debug(f"\nPre NLU llama: \n INPUT-> {self.history.get_history()} \n OUTPUT-> {pre_nlu_llama}\n")

        return pre_nlu_clean


    def clean_json_string(self, input_str: str) -> str:
        # Extract content between the first '[' and the last ']'
        match = re.search(r'\[.*\]', input_str, re.DOTALL)
        return match.group(0) if match else input_str

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


    def query_model(self, user_input: str) -> str:

        system = self.system_prompt['pre_nlu']['prompt']
        
        messages = [{
            'role': 'system',
            'content': system
        }] 

        messages.append({
            'role': 'user',
            'content': f"History dialogue: {self.history.get_history()}"
        })

        messages.append({
            'role': 'user',
            'content': user_input
        })

        response = ollama.chat(model=self.model, messages=messages)

        output =  response['message']['content']

        return output

