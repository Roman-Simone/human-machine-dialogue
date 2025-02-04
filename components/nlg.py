import re
import yaml
import ollama
import logging
from utils.history import History

class NLG():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.history = History()
        self.logger = logging.getLogger(__name__)
        with open(self.prompt_path, "r") as file:
            self.system_prompt_yaml = yaml.safe_load(file)
    

    def __call__(self, nba_input: dict) -> str:
        
        response = ""

        if type(nba_input) != dict:
            self.logger.error("Input must be a dictionary")
            return "error"
        
        nba = nba_input['nba']
        data = nba_input['data']

        action, argument = self.extract_action_argument(nba)

        if action == "request_info":
            system_prompt = self.system_prompt_yaml["nlg"]["prompt_request_info"]
            response = self.query_model(nba, system_prompt)
        elif action == "confirmation":
            if argument == "get_exercise":
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_get_exercise"]
            elif argument == "get_information":
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_get_information"]
            elif argument == "get_plan":
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_get_plan"]
            elif argument == "save_exercise":
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_save_exercise"]
            else:
                self.logger.error("Invalid argument for confirmation action")
                return "error"
        
            response = self.query_model(nba, system_prompt, data)


        return response


    def extract_action_argument(self, nba: str) -> tuple:

        match = re.match(r"(request_info|confirmation)\((.*?)\)", nba)
        
        if match:
            return match.groups()  # Returns (action, argument)
        
        return None, None  # Default case if no match is found


    def query_model(self, nba_input: str, system: str, data=" ")-> str:

        messages = [{
            'role': 'system',
            'content': system
        }] 

        # messages.append({
        #     'role': 'user',
        #     'content': f"History User: {self.history.get_history()}"
        # })
        if data != " ":
            messages.append({
                'role': 'user',
                'content': "user data: \n" + data
            })

        messages.append({
            'role': 'user',
            'content': nba_input
        })

        self.history.add('user', nba_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']
