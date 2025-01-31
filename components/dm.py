import json
import ollama
# import logging
from utils.history import History


# logger = logging.getLogger(__name__)

class StateManager():

    def __init__(self, nlu_response: dict):
        # self.intent = "get_exercise"
        # fields = [
        #     "type",
        #     "body_part",
        #     "equipment",
        #     "level"
        # ]
        # self.state = {field: None for field in fields}
        self.intent = None
        for key, value in nlu_response.items():
            if value is None:
                continue
            elif isinstance(value, str):
                self.intent = value
            elif isinstance(value, dict):
                self.slots = value

    def update_state(self, nlu_response: dict):
        for key, value in nlu_response.items():
            if value is None:
                continue
            elif isinstance(value, str):
                continue
            elif isinstance(value, dict):
                for slot_key, slot_value in value.items():
                    if slot_value is not None and slot_value != "null" and slot_key in self.slots.keys():
                        self.slots[slot_key] = slot_value

    def __str__(self) -> str:
        return f"Intent: {self.intent}, Slots: {self.slots}"
    


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

    
    def get_string(self):
        
        ret = ""

        ret += f"Intent: {self.intent},\n"
        ret += "slots: {\n"
        for key, value in self.slots.items():
            ret += f"\t{key}: {value},\n"
        ret += "}"

        return ret


    
    def update_state(self, nlu_response: dict) -> str:

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
            "...",
        ]
        self.slots = {field: None for field in fields}

    
    def get_json(self):
        return {
            "intent": self.intent,
            "slots": self.slots
        }

    
    def update_state(self, nlu_response: dict):
        for key, value in nlu_response.items():
            if value is None:
                continue
            elif isinstance(value, str):
                continue
            elif isinstance(value, dict):
                for slot_key, slot_value in value.items():
                    if slot_value is not None and slot_value != "null" and slot_key in self.slots.keys():
                        self.slots[slot_key] = slot_value
        
        return self.get_json()





class DM():

    def __init__(self, model, prompt_path):
        
        self.model = model
        self.prompt_path = prompt_path
        self.exerciseST = exerciseST()
        self.history = History()

    def __call__(self, nlu_input = " "):

        if self.exerciseST.intent == "get_exercise":
            nlu_response = self.exerciseST.update_state(nlu_input)
        elif self.exerciseST.intent == "suggest_workout":
            nlu_response = self.exerciseST.update_state(nlu_input)
        else:
            raise ValueError("Invalid intent")

        nba = self.query_model(nlu_response)
        return nba
    
        
    def query_model(self, nlu_input: str):

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