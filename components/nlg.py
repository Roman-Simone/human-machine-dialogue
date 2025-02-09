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
        
        nba = f"action: {nba_input['action']}, parameter: {nba_input['parameter']}"
        data = nba_input['data']

        action = nba_input['action']
        parameter = nba_input['parameter']

        if action == "request_info":
            self.logger.debug(f"Action request_info. Slot: {parameter}")
            system_prompt = self.system_prompt_yaml["nlg"]["prompt_request_info"]
            response = self.query_model(nba, system_prompt, data)

        elif action == "confirmation":
            if parameter == "get_exercise":
                self.logger.debug("Action confirmation. Intent: get_exercise")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_get_exercise"]
            elif parameter == "get_information":
                self.logger.debug("Action confirmation. Intent: get_information")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_get_information"]
            elif parameter == "get_plan":
                self.logger.debug("Action confirmation. Intent: get_plan")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_get_plan"]
            elif parameter == "save_exercise":
                self.logger.debug("Action confirmation. Intent: save_exercise")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_save_exercise"]
            elif parameter == "add_favorite":
                self.logger.debug("Action confirmation. Intent: add_favorite")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_add_favorite"]
            elif parameter == "remove_favorite":
                self.logger.debug("Action confirmation. Intent: remove_favorite")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_remove_favorite"]
            elif parameter == "list_favorite":
                self.logger.debug("Action confirmation. Intent: list_favorite")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_list_favorite"]
            elif parameter == "give_evaluation":
                self.logger.debug("Action confirmation. Intent: give_evaluation")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_give_evaluation"]
            elif parameter == "out_of_context":
                self.logger.debug("Action confirmation. Intent: out_of_context")
                system_prompt = self.system_prompt_yaml["nlg"]["prompt_confirmation_out_of_context"]
            else:
                self.logger.error("Invalid argument for confirmation action")
                return "error"
        
            response = self.query_model(nba, system_prompt, data)
        
        elif action == "check_info":
            self.logger.debug("Action check_info")
            system_prompt = self.system_prompt_yaml["nlg"]["prompt_check_info"]
            response = self.query_model(nba, system_prompt, data)


        return response


    def query_model(self, nba_input: str, system: str, data=" ")-> str:

        messages = [{
            'role': 'system',
            'content': system
        }] 

        # messages.append({
        #     'role': 'user',
        #     'content': f"History User: {self.history.get_history()}"
        # })

        user_input = f"{nba_input} \ndata = {data}"

        messages.append({
            'role': 'user',
            'content': user_input
        })

        # if data != " ":
        #     messages.append({
        #         'role': 'user',
        #         'content': "user data: \n" + data
        #     })

        self.history.add('user', nba_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']
