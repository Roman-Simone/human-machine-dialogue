import re
import yaml
import json
import ollama
import logging
from copy import deepcopy
from utils.history import History


class PreNLU():
    """ 
    PreNLU class to handle the intent classificatio task.
    """

    def __init__(self, model, prompt_path, eval_mode = True):
        """
        PreNLU class constructor.
        """
        
        self.model = model
        self.prompt_path = prompt_path
        self.logger = logging.getLogger(__name__)
        self.history = History()
        self.history.limit = 5
        self.eval_mode = eval_mode
        with open(self.prompt_path, "r") as file:
            self.system_prompt = yaml.safe_load(file)
        
        self.valid_intents = ["get_exercise", "get_plan", "get_information", "save_exercise", "add_favorite", "remove_favorite", "list_favorite", "give_evaluation", "out_of_context", "terminate_system"]


    def __call__(self, user_input = " ", system_response = " ") -> list:
        '''
        take user input request (natural language) and return a list of the input text divided in the various intents.

        Args:
            user_input (str): user input request (natural language).
            system_response (str): system response. To be used in the conversation history.

        Returns:
            pre_nlu_clean (list): list of the input text divided in the various intents.
        '''

        flag_repeat = True

        self.history.add('system', system_response)

        while(flag_repeat):

            pre_nlu_llama = self.query_model(user_input)

            try:
                pre_nlu_llama_clean = self.clean_json_string(pre_nlu_llama)
                pre_nlu_json = json.loads(pre_nlu_llama_clean)
                if type(pre_nlu_json) == dict:
                    pre_nlu_json = [pre_nlu_json]
                pre_nlu_clean = self.clean_response(pre_nlu_json)

                flag_repeat = False
                for intent in pre_nlu_clean:
                    if intent.get("intent") not in self.valid_intents:
                        self.logger.error("Intent not recognized")
                        flag_repeat = True
                
            except:
                self.logger.error("Error parsing PRE-NLU response \n pre_nlu_llama: {pre_nlu_llama}")

        self.history.add('user', user_input)

        self.logger.debug(f"\nPre NLU llama: \n INPUT-> {self.history.get_history()} \n OUTPUT-> {pre_nlu_llama}\n")

        return pre_nlu_clean


    def clean_json_string(self, input_str: str) -> str:
        '''
        Function to clean the json string, return only the part of string with list.
        
        Args:
            input_str (str): input string.
            
        Returns:
            str: cleaned string.
        '''
        match = re.search(r'\[.*\]', input_str, re.DOTALL)
        return match.group(0) if match else input_str


    def clean_response(self, response: dict) -> dict:
        ''' 
        Function to clean the response from the model.

        Args:
            response (dict): response from the model.
        
        Returns:
            final_dict (dict): cleaned response.
        '''
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
        '''
        Function to query the model.
        
        Args:  
            user_input (str): user input.
            
        Returns:
            output (str): model output.
        '''

        system = self.system_prompt['pre_nlu']['prompt']
        
        messages = [{
            'role': 'system',
            'content': system
        }] 

        if self.eval_mode:
            messages.append({
                'role': 'system',
                'content': f"History: {self.history.get_history()}"
            })
        else:
            messages.append({
                'role': 'system',
                'content': "What can I do for you today?"
            })

        messages.append({
            'role': 'user',
            'content': user_input
        })

        response = ollama.chat(model=self.model, messages=messages)

        output =  response['message']['content']

        return output

