import logging
from components import (
    PreNLU,
    NLU,
    DM,
    NLG
)

class Chat():

    def __init__(self, config):

        self.RUNNING = True
        self.logger = logging.getLogger(__name__)
        self.model = config['model']
        self.prompts_path = config['prompts_path']

        self.pre_nlu = PreNLU(self.model, self.prompts_path)
        self.nlu = NLU(self.model, self.prompts_path)
        self.dm = DM(self.model, self.prompts_path)
        self.nlg = NLG(self.model, self.prompts_path)

    def run_chat(self):

        while(self.RUNNING):

            user_input = input("User: ")
            if user_input.lower() == "exit":
                self.RUNNING = False
                self.logger.info("Exiting chat")
                break
            
            user_input_pre_nlu = self.pre_nlu(user_input)

            self.logger.info(f"User pre_nlu:\n {user_input_pre_nlu}\n\n")

            meaning = self.nlu(user_input_pre_nlu)

            self.logger.info(f"User nlu:\n {meaning}\n\n")

            nba = self.dm(meaning)

            self.logger.info(f"User nlu:\n {nba}\n\n")

            response = self.nlg(nba)

            print(f"System nlg: {response}")

