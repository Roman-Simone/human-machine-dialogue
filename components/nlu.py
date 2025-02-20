import yaml
import json
import ollama
import logging
from copy import deepcopy
from utils.history import History

class NLU():
    '''
    class NLU to handle the NLU slot filling task
    '''

    def __init__(self, model, prompt_path, eval_mode = True):
        '''
        NLU class constructor
        '''
        
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.prompt_path = prompt_path
        self.history = History()
        self.history.limit = 5
        self.eval_mode = eval_mode
        with open(self.prompt_path, "r") as file:
            self.system_prompt = yaml.safe_load(file)


    def __call__(self, pre_nlu_input: list, user_input:str, system_response: str) -> list:
        '''
        take the intents of the request and return the NLU slot filling of the request in a list of dictionaries.
        
        Args:
            pre_nlu_input (list): intents of the request in a dictionary format.
            user_input (str): user input request (natural language).
            system_response (str): system response. Dictionary.
            
        Returns:
            ret_nlu_cleaned (list): list of dictionaries with the NLU slot filling of the request.
        '''

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
                else:
                    continue
            elif intent.get("intent") == "terminate_system":
                self.logger.debug("Intent terminate_system")
                if len(pre_nlu_input) == 1:
                    return ["terminate_system"]
                else:
                    continue
            else:
                self.logger.error("Intent not recognized")
                system_prompt = self.system_prompt["nlu"]["prompt_out_of_context"]

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
        '''
        Function to clean the response dictionary.

        Args:
            response (dict): response dictionary.
        
        Returns:
            final_dict (dict): cleaned response dictionary
        '''
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
        '''
        Function to query the model with the pre_nlu input and the system prompt.
        
        Args:
            pre_nlu_input (str): pre_nlu input.
            system_prompt (str): system prompt.
            
        Returns:
            output (str): response from the model.
        '''

        with open(self.prompt_path, "r") as file:
            data = yaml.safe_load(file)
        
        messages = [{
            'role': 'system',
            'content': system_prompt
        }] 

        if self.eval_mode:
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

        output =  response['message']['content']

        return output

