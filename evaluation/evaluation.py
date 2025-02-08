import argparse
import json
from tqdm import tqdm
from collections import defaultdict
from components import PreNLU, NLU

class EvalNLU:
    def __init__(self, config):
        self.model = config['model']
        self.prompts_path = config['prompts_path']
        self.error_log_path = config['error_log_path']

        self.pre_nlu = PreNLU(self.model, self.prompts_path, useHistory=False)
        self.nlu = NLU(self.model, self.prompts_path, useHistory=False)

    def eval_NLU(self, dataset_path):
        # Load dataset
        with open(dataset_path, "r") as file:
            dataset = json.load(file)

        print(len(dataset))

        total_intent_counts = defaultdict(int)
        correct_intent_counts = defaultdict(int)
        total_slots = 0
        correct_slots = 0
        total_segments = 0
        correct_intents = 0


        with open(self.error_log_path, "w") as error_log:

            progress_bar = tqdm(dataset, desc="Evaluating NLU", unit="sample", 
                                dynamic_ncols=True)
            for example in progress_bar:
                user_input = example["input"]
                expected_outputs = example["output"]

                # Get model predictions
                output_pre_nlu = self.pre_nlu(user_input, system_response=" ")
                predicted_outputs = self.nlu(output_pre_nlu, user_input, system_response=" ")

                # Ensure both expected and predicted outputs are lists
                if not isinstance(expected_outputs, list):
                    expected_outputs = [expected_outputs]
                if not isinstance(predicted_outputs, list):
                    predicted_outputs = [predicted_outputs]

                total_segments += len(expected_outputs)

                for expected in expected_outputs:
                    total_intent_counts[expected["intent"]] += 1

                    # Find the predicted output that matches the expected output
                    predicted = next((output for output in predicted_outputs if output["intent"] == expected["intent"]), None)
                    if predicted is None:
                        error_log.write(json.dumps({
                            "input": user_input,
                            "expected_intent": expected["intent"],
                            "predicted_intent": "None",
                            "expected_slots": expected.get("slots", {}),
                            "predicted_slots": {}
                        }) + "\n")
                        error_log.flush()  
                        continue
                    
                    if expected["intent"] == predicted["intent"]:
                        correct_intent_counts[expected["intent"]] += 1
                    else:
                        error_log.write(json.dumps({
                            "input": user_input,
                            "expected_intent": expected["intent"],
                            "predicted_intent": predicted["intent"],
                            "expected_slots": expected.get("slots", {}),
                            "predicted_slots": predicted.get("slots", {})
                        }) + "\n")
                        error_log.flush()  


                    # Compare slot predictions
                    expected_slots = expected.get("slots", {})
                    predicted_slots = predicted.get("slots", {})

                    for slot_name, expected_value in expected_slots.items():
                        total_slots += 1  
                        predicted_value = predicted_slots.get(slot_name)

                        if isinstance(expected_value, str) and isinstance(predicted_value, str):
                            expected_value = expected_value.lower()
                            predicted_value = predicted_value.lower()

                        if predicted_value == expected_value:
                            correct_slots += 1
                        else:
                            error_log.write(json.dumps({
                                "input": user_input,
                                "expected_intent": expected["intent"],
                                "predicted_intent": predicted["intent"],
                                "expected_slots": expected.get("slots", {}),
                                "predicted_slots": predicted.get("slots", {})
                            }) + "\n")
                            error_log.flush()  

                # Update progress bar with accuracy
                overall_intent_accuracy = sum(correct_intent_counts.values()) / sum(total_intent_counts.values()) * 100 if sum(total_intent_counts.values()) else 0
                slot_accuracy = (correct_slots / total_slots) * 100 if total_slots else 0
                progress_bar.set_postfix({"Intent Acc": f"{overall_intent_accuracy:.2f}%", "Slot Acc": f"{slot_accuracy:.2f}%"})

        # Print final results
        print("\nNLU Evaluation Results:")
        print(f"Overall Intent Accuracy: {overall_intent_accuracy:.2f}%")
        print(f"Overall Slot Accuracy: {slot_accuracy:.2f}%")


def parse_args():
    parser = argparse.ArgumentParser(description="NLU Evaluation Configuration")

    parser.add_argument("--model", type=str, required=False, default="llama3",
                        help="Specify the model to use for chat.")
    parser.add_argument("--prompts", type=str, required=False, default="prompts/prompts.yaml",
                        help="Specify the path to prompts.")
    parser.add_argument("--dataset", type=str, required=False, default="evaluation/data/dataset_eval_nlu.json",
                        help="Specify the path to the evaluation dataset JSON file.")
    parser.add_argument("--error_log", type=str, required=False, default="evaluation/errors.log",
                        help="Specify the path to save incorrect predictions.")
    
    args = parser.parse_args()

    config = {
        "model": args.model,
        "prompts_path": args.prompts,
        "error_log_path": args.error_log
    }

    return config, args.dataset

if __name__ == "__main__":
    config, dataset_path = parse_args()
    evaluator = EvalNLU(config)
    evaluator.eval_NLU(dataset_path)


    #23
