from components import NLU

class Chat():

    def __init__(self, config):

        self.RUNNING = True
        self.config = config

        self.nlu = NLU(self.config)

    def run_chat(self):

        while(self.RUNNING):

            user_input = input("User: ")
            if user_input.lower() == "exit":
                self.RUNNING = False
                print("Exiting chat application.")
                break
                
            meaning = self.nlu.query_model(model_name=self.config['model'], system_prompt=self.config['nlu_prompt_path'], user_input=user_input)

            print(f"System: {meaning}")

