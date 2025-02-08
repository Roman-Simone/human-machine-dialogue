import yaml
import json
import ollama
import logging
from copy import deepcopy
from utils.history import History

class NLU():

    def __init__(self, model, prompt_path, useHistory = True):
        
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.prompt_path = prompt_path
        self.history = History()
        self.useHistory = useHistory
        with open(self.prompt_path, "r") as file:
            self.system_prompt = yaml.safe_load(file)


    def __call__(self, pre_nlu_input: list, user_input:str, system_response: str) -> list:

        ret_nlu_cleaned = []

        self.history.add('system', system_response)

        for intent in pre_nlu_input:

            if intent.get("intent") == "get_exercise":
                self.logger.debug("Intent get_exercise")
                system_prompt = self.system_prompt["nlu"]["prompt_get_exercise"]
            elif intent.get("intent") == "get_plan":
                self.logger.debug("Intent get_plan")
                system_prompt = self.system_prompt["nlu"]["prompt_get_plan"]
            elif intent.get("intent") == "get_information":
                self.logger.debug("Intent get_information")
                system_prompt = self.system_prompt["nlu"]["prompt_get_information"]
            elif intent.get("intent") == "save_exercise":
                self.logger.debug("Intent save_exercise")
                system_prompt = self.system_prompt["nlu"]["prompt_save_exercise"]
            elif intent.get("intent") == "add_favorite":
                self.logger.debug("Intent add_favorite")
                system_prompt = self.system_prompt["nlu"]["prompt_add_favorite"]
            elif intent.get("intent") == "remove_favorite":
                self.logger.debug("Intent remove_favorite")
                system_prompt = self.system_prompt["nlu"]["prompt_remove_favorite"]
            elif intent.get("intent") == "list_favorite":
                self.logger.debug("Intent list_favorite")
                system_prompt = self.system_prompt["nlu"]["prompt_list_favorite"]
            elif intent.get("intent") == "give_evaluation":
                self.logger.debug("Intent give_evaluation")
                system_prompt = self.system_prompt["nlu"]["prompt_give_evaluation"]
            elif intent.get("intent") == "out_of_context":
                self.logger.debug("Intent out_of_context")
                if len(pre_nlu_input) == 1:
                    system_prompt = self.system_prompt["nlu"]["prompt_out_of_context"]
                continue
            else:
                self.logger.error("Intent not recognized")

            flag_repeat = True
            while flag_repeat:
                nlu_response = self.query_model(pre_nlu_input=str(intent), system_prompt=system_prompt)

                self.logger.debug(f"\nNLU llama:\n {nlu_response}")

                try:
                    nlu_response_json = json.loads(nlu_response)
                    flag_repeat = False
                except:
                    self.logger.error("Error parsing NLU response")
            

            if type(nlu_response_json) is dict:
                nlu_cleaned_response = self.clean_response(nlu_response_json)
                ret_nlu_cleaned.append(nlu_cleaned_response)
            else:
                self.logger.error("NLU response is not a dictionary")
        
        self.history.add('user', user_input)
        
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


    def query_model(self, pre_nlu_input: str, system_prompt: str) -> str:

        with open(self.prompt_path, "r") as file:
            data = yaml.safe_load(file)
        
        messages = [{
            'role': 'system',
            'content': system_prompt
        }] 

        if self.useHistory:
            for message in self.history.get_history():
                messages.append({
                    'role': message['role'],
                    'content': f"History {message['role']}: {message['content']}"
                })
        else:
            messages.append({
                'role': 'system',
                'content': "Hi what can I do for you today?"
            })

        messages.append({
            'role': 'user',
            'content': pre_nlu_input
        })

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']



