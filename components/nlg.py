import yaml
import ollama
import logging

class NLG():
    '''
    Class for Natural Language Generation (NLG) task. 
    '''

    def __init__(self, model, prompt_path):
        '''
        NLG class constructor.
        '''
        self.model = model
        self.prompt_path = prompt_path
        self.logger = logging.getLogger(__name__)
        with open(self.prompt_path, "r") as file:
            self.system_prompt_yaml = yaml.safe_load(file)


    def __call__(self, nba_inputs: list) -> str:
        '''
        Take the NBA inputs and return the system response. 
        
        Args:
            nba_inputs (list): list of dictionaries with the NBA inputs 
            [
                {
                    "action": (str), -> action to be performed
                    "parameter": (str), -> parameter of the action
                    "data": (str) -> data from the database to be used in the action 
            
            '''

        responses = []
        
        for nba_input in nba_inputs:

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

            responses.append(response)
        
        if len(responses) == 1:
            return responses[0]
        else:
            system_prompt = self.system_prompt_yaml["nlg"]["prompt_merge_responses"]
            response_to_merge = ""
            for idx_response, response  in enumerate(responses):
                response_to_merge += f"response n_{idx_response}: \n{response}\n\n"
            
            response = self.query_model(response_to_merge, system_prompt)

            

        return response


    def query_model(self, nba_input: str, system: str, data=" ")-> str:
        '''
        Query the model with the nba_input and system response.

        Args:
            nba_input (str): NBA input
            system (str): system response
            data (str): data from the database to be used in the action

        return:
            str: model response
        '''

        messages = [{
            'role': 'system',
            'content': system
        }] 

        user_input = f"{nba_input} \ndata = {data}"

        messages.append({
            'role': 'user',
            'content': user_input
        })

        self.history.add('user', nba_input)

        response = ollama.chat(model=self.model, messages=messages)

        output =  response['message']['content']

        return output
