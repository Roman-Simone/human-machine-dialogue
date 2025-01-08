import ollama

class NLU():
    def __init__(self, config):
        self.config = config


    def query_model(self, model_name: str, system_prompt:str, user_input: str):
        system= open(system_prompt, 'r').read()
        
        messages = [{
            'role': 'system',
            'content': system
        }]

        messages.append({
            'role': 'user',
            'content': user_input
        })

        response = ollama.chat(model=model_name, messages=messages)

        return response['message']['content']