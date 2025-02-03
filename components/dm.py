import yaml
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
            "n_session",
            "min_rating"
        ]
        fields_save_exercise = [
            "title",
            "description",
            "type",
            "body_part",
            "equipment",
            "level",
            "duration",
            "rating"

        ]
        
        if intent == "get_exercise":
            self.slots = {field: None for field in fields_get_exercise}
        elif intent == "get_information":
            self.slots = {field: None for field in fields_get_information}
        elif intent == "get_plan":
            self.slots = {field: None for field in fields_get_plan}
        elif intent == "save_exercise":
            self.slots = {field: None for field in fields_save_exercise}
        
        self.logger = logging.getLogger(__name__)

    
    def get_string(self):
        
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
    
    def get_intent(self):
        return self.intent

class DM():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.state = []
        self.history = History()
        self.dataset = MegaGymDataset()
        self.logger = logging.getLogger(__name__)
        with open(self.prompt_path, "r") as file:
            self.system_prompt = yaml.safe_load(file)

    def __call__(self, nlu_input: list) -> str:

        self.state = self.update_state(nlu_input)

        state_str = self.get_state_string()

        self.logger.debug(f"State updated: {state_str}")
        
        nba = self.query_model(state_str)

        self.logger.debug(f"DM decision: {nba}")

        if "confirmation" in nba:
            nba = self.confirmation(nba)

        return nba
    

    def confirmation(self, nba_confirm: str) -> str:

        data_confirm = {}
        
        intent_confirm = nba_confirm[nba_confirm.find("(") + 1 : nba_confirm.find(")")]

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
        else:
            self.logger.error(f"Intent {intent_confirm} not found")
            return "Error"

        return f"action: {nba_confirm} \n\n data from database:\n{data_selected}"


    def get_state_string(self):
        # trasform state to string
        state_str = ""

        for state in self.state:
            state_str += state.get_string() + "\n"

        return state_str


    def update_state(self, nlu_input: list):

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
    
