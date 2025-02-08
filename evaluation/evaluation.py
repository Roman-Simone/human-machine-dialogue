import argparse
import json
from tqdm import tqdm
from components import PreNLU, NLU

class EvalNLU:
    def __init__(self, config):
        self.model = config['model']
        self.prompts_path = config['prompts_path']

        self.pre_nlu = PreNLU(self.model, self.prompts_path, useHistory=False)
        self.nlu = NLU(self.model, self.prompts_path, useHistory=False)

    def eval_NLU(self, dataset_path):
        # Load dataset
        with open(dataset_path, "r") as file:
            dataset = json.load(file)

        total_examples = len(dataset)
        correct_intents = 0
        total_intents = 0
        correct_slots = 0
        total_slots = 0

        # Iterate over dataset with tqdm progress bar
        for example in tqdm(dataset, desc="Evaluating NLU", unit="sample"):
            user_input = example["input"]
            expected_output = example["output"]

            # Get model predictions
            output_pre_nlu = self.pre_nlu(user_input, system_response=" ")
            predicted_output = self.nlu(output_pre_nlu, user_input, system_response=" ")

            predicted_output = predicted_output[0]

            # Compare intent prediction
            if predicted_output["intent"] == expected_output["intent"]:
                correct_intents += 1
            else:
                print()

            # Compare slot predictions
            expected_slots = expected_output.get("slots", {})
            predicted_slots = predicted_output.get("slots", {})

            for slot_name, expected_value in expected_slots.items():
                
                total_slots += 1  
                predicted_value = predicted_slots.get(slot_name)

                if type(expected_value) == str and type(predicted_value) == str:
                    expected_value = expected_value.lower()
                    predicted_value = predicted_value.lower()

                if predicted_value == expected_value:
                    correct_slots += 1
                else:
                    print()



            # Calculate accuracy metrics
            intent_accuracy = correct_intents / total_examples * 100
            slot_accuracy = (correct_slots / total_slots * 100) if total_slots > 0 else 0

            print("\nEvaluation Results:")
            print(f"Intent Accuracy: {intent_accuracy:.2f}%")
            print(f"Slot Accuracy: {slot_accuracy:.2f}%")

def parse_args():
    parser = argparse.ArgumentParser(description="NLU Evaluation Configuration")

    parser.add_argument("--model", type=str, required=False, default="llama3",
                        help="Specify the model to use for chat.")
    parser.add_argument("--prompts", type=str, required=False, default="prompts/prompts.yaml",
                        help="Specify the path to prompts.")
    parser.add_argument("--dataset", type=str, required=False, default="evaluation/data/dataset_eval_nlu.json",
                        help="Specify the path to the evaluation dataset JSON file.")
    
    args = parser.parse_args()

    config = {
        "model": args.model,
        "prompts_path": args.prompts
    }

    return config, args.dataset

if __name__ == "__main__":
    config, dataset_path = parse_args()
    evaluator = EvalNLU(config)
    evaluator.eval_NLU(dataset_path)
    print()
