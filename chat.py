import logging
from components import (
    PreNLU,
    NLU,
    DM,
    NLG
)

import main

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

        print("""
        .-.   .-.     .--.  .-.   .-.  .--.  .----..-. .---. 
        | |   | |    / {} \ |  `.'  | / {} \ | {_  | |{_   _}
        | `--.| `--./  /\  \| |\ /| |/  /\  \| |   | |  | |  
        `----'`----'`-'  `-'`-' ` `-'`-'  `-'`-'   `-'  `-'  
        🔥 Welcome to LLAMAFIT! 🦙💪 

        Hey there, fitness warrior! I'm Llamafit, your AI-powered personal trainer.

        💥 What I can do for you:  
        ✅ Custom workout plans tailored to your fitness level  
        ✅ Exercise description  
        ✅ Keep your favorite exercises saved
        ✅ Save your exercise  
        
        """)

        system_response = "What can I do for you today?"
        print(f"{system_response}")


        while(self.RUNNING):

            user_input = input("User: ")
            if user_input.lower() == "exit":
                self.RUNNING = False
                self.logger.info("Exiting chat")
                break
            
            output_pre_nlu = self.pre_nlu(user_input, system_response)

            self.logger.info(f"User pre_nlu:\n {output_pre_nlu}\n\n")

            meaning = self.nlu(output_pre_nlu, user_input, system_response)

            self.logger.info(f"\nUser nlu:\n {meaning}\n\n")

            system_response = input("System: ")

            nba = self.dm(meaning)

            self.logger.info(f"User nlu:\n {nba}\n\n")

            # system_response = self.nlg(nba)

            # print(f"\nSystem: {system_response}\n")


if __name__ == "__main__":
    main.main()
