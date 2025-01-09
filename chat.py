from components import (
    PreNLU,
    NLU,
    DM,
    NLG
)



class Chat():

    def __init__(self, config):

        self.RUNNING = True

        self.model = config['model']
        self.pre_nlu_prompt_path = config['pre_nlu_prompt_path']
        self.nlu_prompt_path = config['nlu_prompt_path']
        self.dm_prompt_path = config['dm_prompt_path']
        self.nlg_prompt_path = config['nlg_prompt_path']

        self.pre_nlu = PreNLU(self.model, self.pre_nlu_prompt_path)
        self.nlu = NLU(self.model, self.nlu_prompt_path)
        self.dm = DM(self.model, self.dm_prompt_path)
        self.nlg = NLG(self.model, self.nlg_prompt_path)

    def run_chat(self):

        while(self.RUNNING):

            user_input = input("User: ")
            if user_input.lower() == "exit":
                self.RUNNING = False
                print("Exiting chat application.")
                break
            
            user_input_pre_nlu = self.pre_nlu.query_model(user_input=user_input)

            print(f"System pre_nlu: {user_input_pre_nlu}")

            meaning = self.nlu.query_model(user_input=user_input_pre_nlu)

            print(f"System nlu: {meaning}")

            nba = self.dm.query_model(nlu_input=meaning)

            print(f"System nba: {nba}")

            response = self.nlg.query_model(nba_input=nba)

            print(f"System nlg: {response}")

