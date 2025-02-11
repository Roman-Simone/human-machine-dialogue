import re
import yaml
import json
import ollama
import logging
from utils.history import History
from dataset.dataset import MegaGymDataset


class stateTracker():

    def __init__(self, intent):
        self.intent = intent
        
        fields_get_exercise = [
            "type",
            "body_part",
            "equipment",
            "level"
        ]
        fields_get_information = [
            "title",
            "body_part"
        ]
        fields_get_plan = [
            "level",
            "n_session"
        ]
        fields_save_exercise = [
            "title",
            "description",
            "type",
            "body_part",
            "equipment",
            "level",
            "duration"
        ]
        fields_add_favorite = [
            "title"
        ]
        fields_remove_favorite = [
            "title"
        ]
        fields_list_favorite = [
            "type",
            "body_part"
        ]
        fields_give_evaluation = [
            "rating",
            "comment"
        ]
        fields_out_of_context = []

        
        if intent == "get_exercise":
            self.slots = {field: None for field in fields_get_exercise}
        elif intent == "get_information":
            self.slots = {field: None for field in fields_get_information}
        elif intent == "get_plan":
            self.slots = {field: None for field in fields_get_plan}
        elif intent == "save_exercise":
            self.slots = {field: None for field in fields_save_exercise}
        elif intent == "add_favorite":
            self.slots = {field: None for field in fields_add_favorite}
        elif intent == "remove_favorite":
            self.slots = {field: None for field in fields_remove_favorite}
        elif intent == "list_favorite":
            self.slots = {field: None for field in fields_list_favorite}
        elif intent == "give_evaluation":
            self.slots = {field: None for field in fields_give_evaluation}
        else:
            self.slots = {field: None for field in fields_out_of_context}
        
        self.logger = logging.getLogger(__name__)


    def get_string(self) -> str:
        
        ret = "{"

        ret += f"Intent: {self.intent},\n"
        ret += "slots: {\n"
        for key, value in self.slots.items():
            ret += f"\t{key}: {value},\n"
        ret += "}}"

        return ret


    def update_state(self, nlu_response: list) -> str:

        for key, value in nlu_response.items():
            if value is None:
                continue
            elif isinstance(value, str):
                continue
            elif isinstance(value, dict):
                for slot_key, slot_value in value.items():
                    if slot_value is not None and slot_value != "null" and slot_key in self.slots.keys():
                        self.slots[slot_key] = slot_value
        
        return self.get_string()


    def get_intent(self) -> str:
        return self.intent

class DM():

    def __init__(self, model, prompt_path, eval_mode=False):
        
        self.model = model
        self.prompt_path = prompt_path
        self.state = []
        self.history = History()
        self.dataset = MegaGymDataset()
        self.logger = logging.getLogger(__name__)
        self.eval_mode = eval_mode

        with open(self.prompt_path, "r") as file:
            self.system_prompt = yaml.safe_load(file)


    def __call__(self, nlu_input: list) -> list:

        idx_to_remove = []

        if self.eval_mode:
            self.state = []

        if nlu_input[0] == "terminate_system":
            return "terminate_system"

        self.state = self.update_state(nlu_input)

        actions_ret = []

        for state in self.state:
            self.logger.debug(f"State: {state.get_string()}")

            flag_repeat = True
            states_str = self.get_states_string()

            self.logger.debug(f"\nStates updated:\n {states_str}")

            state_str = self.get_state_string(state)
            
            while(flag_repeat):

                nba_llama = self.query_model(state_str)

                try:
                    nba_llama_clean = self.clean_json_string(nba_llama)
                    nba_json = json.loads(nba_llama_clean)
                    if not self.eval_mode:
                        flag_repeat = self.check_nba(nba_json, state)
                    else:
                        flag_repeat = False
                
                except:
                    self.logger.error("Error parsing NBA response")

            self.logger.debug(f"DM decision: {nba_json}")

            data = ""
            if nba_json["action"] == "confirmation" and not self.eval_mode:
                data = self.confirmation(nba_json)
                if data or True:
                    self.logger.debug("Intent completed and eliminated from state")
                    for idx, element in enumerate(self.state):
                        if element.get_intent() == state.intent:
                            idx_to_remove.append(idx)
                # else:
                #     nba_json = {
                #         "action": "check_info",
                #         "parameter": nba_json["parameter"],
                #     }
                #     data = state.get_string()
            
            if nba_json["action"] == "request_info":
                data = f"intent: {state.intent}"
            
            response = {
                "action": nba_json["action"],
                "parameter": nba_json["parameter"],
                "data": data
            }

            actions_ret.append(response)

        if self.eval_mode:
            return actions_ret[0]
        
        state_back = []

        for idx, element in enumerate(self.state):
            if idx not in idx_to_remove:
                state_back.append(element)
        
        self.state = []

        for element in state_back:
            self.state.append(element)

        return actions_ret


    def clean_json_string(self, input_str: str) -> str:
        # Extract content between the first '[' and the last ']'
        match = re.search(r'\{}.*\}', input_str, re.DOTALL)
        return match.group(0) if match else input_str


    def confirmation(self, nba_confirm: dict) -> str:

        data_confirm = {}
        
        intent_confirm = nba_confirm["parameter"]

        find_flag = False
        for element in self.state:
            if element.get_intent() == intent_confirm:
                data_confirm = element
                find_flag = True
                break
        
        if not find_flag:
            self.logger.error(f"Intent {intent_confirm} not found in state")
            return "Error"
        
        if intent_confirm == "get_exercise":
            data_selected = self.dataset.filter_by_intent(data_confirm.slots)
        elif intent_confirm == "get_information":
            data_selected = self.dataset.filter_by_intent(data_confirm.slots)
        elif intent_confirm == "get_plan":
            data_selected = self.dataset.get_schedule(data_confirm.slots)
        elif intent_confirm == "save_exercise":
            data_selected = self.dataset.save_exercise(data_confirm.slots)
            data_selected = f"{data_confirm.slots}"
        elif intent_confirm == "add_favorite":
            response = self.dataset.add_favorite(data_confirm.slots)
            if not response.empty:
                data_selected = f"{data_confirm.slots}"
            else:
                data_selected = False
        elif intent_confirm == "remove_favorite":
            response = self.dataset.remove_favorite(data_confirm.slots)
            if response:
                data_selected = f"{data_confirm.slots}"
            else:
                data_selected = False
        elif intent_confirm == "list_favorite":
            data_selected = self.dataset.list_favorite(data_confirm.slots)
        elif intent_confirm == "give_evaluation":
            data_selected = self.give_evaluation(data_confirm.slots)
        elif intent_confirm == "out_of_context":
            data_selected = "Intent out_of_context"
        else:
            self.logger.error(f"Intent {intent_confirm} not found")
            return "Error"

        return data_selected


    def give_evaluation(self, slots: dict) -> bool:
        
        rating = slots["rating"]
        comment = slots["comment"]

        # save in a file the evaluation
        with open("dataset/data/evaluation.txt", "a") as file:
            file.write(f"Rating: {rating}\n")
            file.write(f"Comment: {comment}\n\n")

        return "Evaluation saved"


    def check_nba(self, nba: dict, nlu: dict) -> bool:

        action = nba['action']
        parameter = nba['parameter']
        
        if parameter == "None" or parameter == "null" or parameter == "" or parameter == "none":
            return True
        
        if not (action == "request_info" or action == "confirmation"):
            return True

        empty_flag = True
        for elem in nlu.slots.values():
            if elem is None:
                empty_flag = False
        
        if empty_flag and action != "confirmation":
            return True
        if not empty_flag and action != "request_info":
            return True
        
        if action == "get-exercise" or action == "get-information" or action == "get-plan" or action == "save-exercise" or action == "add-favorite" or action == "remove-favorite" or action == "list-favorite" or action == "give-evaluation" or action == "out-of-context":
            return True

        return False


    def get_states_string(self) -> str:
        # trasform state to string
        state_str = ""

        for state in self.state:
            state_str += state.get_string() + "\n"

        return state_str


    def get_state_string(self, state) -> str:
        
        state_str = ""

        state_str += state.get_string() + "\n"

        return state_str


    def update_state(self, nlu_input: list) -> list:

        for intent in nlu_input:
            
            flag_find = False

            for state in self.state:
                if state.intent == intent["intent"]:
                    flag_find = True
                    state.update_state(intent)
                    break
        
            if not flag_find:
                if intent["intent"] == "get_exercise":
                    self.state.append(stateTracker("get_exercise"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "get_information":
                    self.state.append(stateTracker("get_information"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "get_plan":
                    self.state.append(stateTracker("get_plan"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "save_exercise":
                    self.state.append(stateTracker("save_exercise"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "add_favorite":
                    self.state.append(stateTracker("add_favorite"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "remove_favorite":
                    self.state.append(stateTracker("remove_favorite"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "list_favorite":
                    self.state.append(stateTracker("list_favorite"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "give_evaluation":
                    self.state.append(stateTracker("give_evaluation"))
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "out_of_context":
                    self.state.append(stateTracker("out_of_context"))
                    self.state[-1].update_state(intent)
                else:
                    self.logger.error(f"Intent {intent['intent']} not found")
        
        return self.state


    def query_model(self, nlu_input: str) -> str:

        system = self.system_prompt["dm"]["prompt"]
        
        messages = [{
            'role': 'system',
            'content': system
        }]

        messages.append({
            'role': 'user',
            'content': nlu_input
        })

        self.history.add('user', nlu_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']

