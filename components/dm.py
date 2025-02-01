
import ollama
import logging
from utils.history import History
from abc import ABC, abstractmethod


# class StateManager(ABC):

#     @abstractmethod
#     def __init__(self):
#         pass

#     @abstractmethod
#     def update_state(self, nlu_response: dict):
#         pass

#     @abstractmethod
#     def get_string(self):
#         pass


class exerciseST():
    def __init__(self):
        self.intent = "get_exercise"
        fields = [
            "type",
            "body_part",
            "equipment",
            "level"
        ]
        self.slots = {field: None for field in fields}

        self.logger = logging.getLogger(__name__)

    
    def get_string(self):
        
        ret = ""

        ret += f"Intent: {self.intent},\n"
        ret += "slots: {\n"
        for key, value in self.slots.items():
            ret += f"\t{key}: {value},\n"
        ret += "}"

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


class workoutST():
    def __init__(self):
        self.intent = "get_workout"
        fields = [
            "type",
            "n_exercise",
            "equipment" ,
            "level"
        ]
        self.slots = {field: None for field in fields}

        self.logger = logging.getLogger(__name__)

    
    def get_string(self):
        
        ret = ""

        ret += f"Intent: {self.intent},\n"
        ret += "slots: {\n"
        for key, value in self.slots.items():
            ret += f"\t{key}: {value},\n"
        ret += "}"

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


class DM():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.state = []
        self.history = History()

    def __call__(self, nlu_input: list) -> str:

        self.state = self.update_state(nlu_input)

        # trasform state to string
        state_str = ""
        for state in self.state:
            if state.intent == "get_exercise":
                state_str += state.get_string()
            elif state.intent == "get_workout":
                state_str += state.get_string()
            else:
                state_str += "No state found"
        
        nba = self.query_model(state_str)

        return nba
    
    def update_state(self, nlu_input: list):

        flag_find = False
        for intent in nlu_input:
            for state in self.state:
                if state.intent == "get_exercise":
                    flag_find = True
                    state.update_state(intent)
                elif state.intent == "get_workout":
                    flag_find = True
                    state.update_state(intent)
        
        if not flag_find:
            for intent in nlu_input:
                if intent["intent"] == "get_exercise":
                    self.state.append(exerciseST())
                    self.state[-1].update_state(intent)
                elif intent["intent"] == "get_workout":
                    self.state.append(workoutST())
                    self.state[-1].update_state(intent)
        
        return self.state


    def query_model(self, nlu_input: str) -> str:

        system= open(self.prompt_path, 'r').read()
        
        messages = [{
            'role': 'system',
            'content': system
        }] #+ self.history.get_history()

        messages.append({
            'role': 'system',
            'content': nlu_input
        })

        self.history.add('user', nlu_input)

        response = ollama.chat(model=self.model, messages=messages)

        return response['message']['content']