from components import (
    NLU,
    DM,
    NLG
)



class Chat():

    def __init__(self, config):

        self.RUNNING = True

        self.model = config['model']
        self.nlu_prompt_path = config['nlu_prompt_path']
        self.dm_prompt_path = config['dm_prompt_path']
        self.nlg_prompt_path = config['nlg_prompt_path']

        self.nlu = NLU(self.model)
        self.dm = DM(self.config)
        self.nlg = NLG(self.config)

    def run_chat(self):

        while(self.RUNNING):

            user_input = input("User: ")
            if user_input.lower() == "exit":
                self.RUNNING = False
                print("Exiting chat application.")
                break
                
            meaning = self.nlu.query_model(model_name=self.config['model'], system_prompt=self.config['nlu_prompt_path'], user_input=user_input)

            print(f"System: {meaning}")

