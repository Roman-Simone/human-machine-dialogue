import json
import argparse
from tqdm import tqdm
from collections import defaultdict
from components import (
    PreNLU,
    NLU,
    DM
)

class Evaluation:
    '''
    Class to perform intrinsic evaluation of the NLU and DM components.
    '''

    def __init__(self, config):
        self.model = config['model']
        self.prompts_path = config['prompts_path']
        self.error_log_path_nlu = config['error_log_nlu']
        self.error_log_path_dm = config['error_log_dm']
        self.dataset_path_nlu = config['dataset_nlu']
        self.dataset_path_dm = config['dataset_dm']

        self.pre_nlu = PreNLU(self.model, self.prompts_path, eval_mode=False)
        self.nlu = NLU(self.model, self.prompts_path, eval_mode=False)
        self.DM = DM(self.model, self.prompts_path, eval_mode=True)

    def eval_NLU(self):
        '''
        Method to evaluate the NLU component. Take example from dataset and compare the expected output with the predicted output.
        Calculate the intent accuracy, slot accuracy, and intent-wise performance (precision, recall, f1-score).
        '''
        with open(self.dataset_path_nlu, "r") as file:
            dataset = json.load(file)

        total_intent_counts = defaultdict(int)
        correct_intent_counts = defaultdict(int)
        predicted_intent_counts = defaultdict(int)
        total_slots = 0
        correct_slots = 0
        total_segments = 0


        with open(self.error_log_path_nlu, "w") as error_log:

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
                        error_log.write("\n--- ERROR: MISSING PREDICTION ---\n")
                        error_log.write(f"Input: {user_input}\n")
                        error_log.write(f"Expected Intent: {expected['intent']}\n")
                        error_log.write(f"Expected Slots: {json.dumps(expected.get('slots', {}), indent=4)}\n")
                        error_log.write("\n------------------------------\n")
                        error_log.flush()  
                        continue
                    
                    predicted_intent_counts[predicted["intent"]] += 1

                    if expected["intent"] == predicted["intent"]:
                        correct_intent_counts[expected["intent"]] += 1
                    else:
                        error_log.write("\n--- ERROR: INTENT MISMATCH ---\n")
                        error_log.write(f"Input: {user_input}\n")
                        error_log.write(f"Expected Intent: {expected['intent']}\n")
                        error_log.write(f"Expected Slots: {json.dumps(expected.get('slots', {}), indent=4)}\n")
                        error_log.write(f"Predicted Intent: {predicted['intent']}\n")
                        error_log.write(f"Predicted Slots: {json.dumps(predicted.get('slots', {}), indent=4)}\n")
                        error_log.write("\n------------------------------\n")
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
                            error_log.write("\n--- ERROR: SLOT MISMATCH ---\n")
                            error_log.write(f"Input: {user_input}\n")
                            error_log.write(f"Expected Intent: {expected['intent']}\n")
                            error_log.write(f"Expected Slots: {json.dumps(expected.get('slots', {}), indent=4)}\n")
                            error_log.write(f"Predicted Intent: {predicted['intent']}\n")
                            error_log.write(f"Predicted Slots: {json.dumps(predicted.get('slots', {}), indent=4)}\n")
                            error_log.write("\n------------------------------\n")
                            error_log.flush()
          

                # Update progress bar with accuracy
                overall_intent_accuracy = sum(correct_intent_counts.values()) / sum(total_intent_counts.values()) * 100 if sum(total_intent_counts.values()) else 0
                slot_accuracy = (correct_slots / total_slots) * 100 if total_slots else 0

                progress_bar.set_postfix({"Intent Acc": f"{overall_intent_accuracy:.2f}%", "Slot Acc": f"{slot_accuracy:.2f}%"})

        # Compute final metrics per intent
        intent_metrics = {}
        for intent in total_intent_counts:
            tp = correct_intent_counts[intent]
            fp = predicted_intent_counts[intent] - tp
            fn = total_intent_counts[intent] - tp

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            intent_metrics[intent] = {
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
            
        # Print final results
        print("\nNLU Evaluation Results:")
        overall_intent_accuracy = sum(correct_intent_counts.values()) / sum(total_intent_counts.values()) * 100 if sum(total_intent_counts.values()) else 0
        slot_accuracy = (correct_slots / total_slots) * 100 if total_slots else 0
        print(f"Overall Intent Accuracy: {overall_intent_accuracy:.2f}%")
        print(f"Overall Slot Accuracy: {slot_accuracy:.2f}%")
        print("\nIntent-wise Performance:")
        for intent, metrics in intent_metrics.items():
            print(f"Intent: {intent}")
            print(f"  Precision: {metrics['precision']:.2f}")
            print(f"  Recall: {metrics['recall']:.2f}")
            print(f"  F1-score: {metrics['f1']:.2f}")
            print()


    def eval_DM(self):
        '''
        Method to evaluate the DM component. Take example from dataset and compare the expected output with the predicted output.
        Calculate the action accuracy, parameter accuracy, and action-wise performance (precision, recall, f1-score).
        '''
        with open(self.dataset_path_dm, "r") as file:
            dataset = json.load(file)

        total_actions = 0
        correct_actions = 0
        correct_parameters = 0
        total_parameters = 0
        predicted_actions = defaultdict(int)
        correct_predictions = defaultdict(int)
        total_expected_actions = defaultdict(int)

        with open(self.error_log_path_dm, "w") as error_log:

            progress_bar = tqdm(dataset, desc="Evaluating DM", unit="sample", dynamic_ncols=True)
            for sample in progress_bar:

                nlu_input = sample["input"]


                expected_output = sample["output"]

                # Get DM predictions
                dm_prediction = self.DM(nlu_input)

                total_actions += 1

                predicted_actions[dm_prediction["action"]] += 1
                total_expected_actions[expected_output["action"]] += 1

                if expected_output["action"] == dm_prediction["action"]:
                    correct_actions += 1
                    correct_predictions[expected_output["action"]] += 1
                else:
                    error_log.write("\n--- ERROR: DM MISMATCH ---\n")
                    error_log.write(f"NLU input: {json.dumps(nlu_input, indent=4)}\n")
                    error_log.write(f"Expected DM Output: {json.dumps(expected_output, indent=4)}\n")
                    error_log.write(f"Predicted DM Output: {json.dumps(dm_prediction, indent=4)}\n")
                    error_log.write("\n------------------------------\n")
                    error_log.flush()
                
                # Compare parameter predictions
                total_parameters+=1
                if dm_prediction["parameter"] in expected_output["parameter"]:
                    correct_parameters += 1
                else:
                    error_log.write("\n--- ERROR: PARAMETER MISMATCH ---\n")
                    error_log.write(f"NLU input: {json.dumps(nlu_input, indent=4)}\n")
                    error_log.write(f"Expected DM Output: {json.dumps(expected_output, indent=4)}\n")
                    error_log.write(f"Predicted DM Output: {json.dumps(dm_prediction, indent=4)}\n")
                    error_log.write("\n------------------------------\n")
                    error_log.flush()

                precision = sum(correct_predictions[action] / predicted_actions[action] if predicted_actions[action] > 0 else 0 for action in predicted_actions) / len(predicted_actions) if predicted_actions else 0
                recall = sum(correct_predictions[action] / total_expected_actions[action] if total_expected_actions[action] > 0 else 0 for action in total_expected_actions) / len(total_expected_actions) if total_expected_actions else 0
                f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                action_accuracy = (correct_actions / total_actions) * 100 if total_actions else 0
                parameter_accuracy = (correct_parameters / total_parameters) * 100 if total_parameters else 0

                progress_bar.set_postfix({
                    "Action Acc": f"{action_accuracy:.2f}%,", 
                    "Param Acc": f"{parameter_accuracy:.2f}%", 
                    "Precision": f"{precision:.2f}",
                    "Recall": f"{recall:.2f}",
                    "F1-score": f"{f1:.2f}"
                })

        print(f1)
        print(precision)
        print(recall)
        

        # Print final results
        print("\nDM Evaluation Results:")
        print(f"Overall Action Accuracy: {action_accuracy:.2f}%")


def parse_args():
    '''
    Function to parse command line arguments.
    '''
    parser = argparse.ArgumentParser(description="NLU Evaluation Configuration")

    parser.add_argument("--model", type=str, required=False, default="llama3",
                        help="Specify the model to use for chat.")
    parser.add_argument("--prompts", type=str, required=False, default="prompts/prompts.yaml",
                        help="Specify the path to prompts.")
    parser.add_argument("--dataset-nlu", type=str, required=False, default="evaluation/data/dataset_eval_nlu.json",
                        help="Specify the path to the evaluation dataset JSON file.")
    parser.add_argument("--dataset-dm", type=str, required=False, default="evaluation/data/dataset_eval_dm.json",
                        help="Specify the path to the evaluation dataset JSON file.")
    parser.add_argument("--error_log_nlu", type=str, required=False, default="evaluation/errors_nlu.log",
                        help="Specify the path to save incorrect predictions.")
    parser.add_argument("--error_log_dm", type=str, required=False, default="evaluation/errors_dm.log",
                        help="Specify the path to save incorrect predictions.")
    
    args = parser.parse_args()

    config = {
        "model": args.model,
        "prompts_path": args.prompts,
        "error_log_nlu": args.error_log_nlu,
        "error_log_dm": args.error_log_dm,
        "dataset_nlu": args.dataset_nlu,
        "dataset_dm": args.dataset_dm
    }

    return config

if __name__ == "__main__":
    config = parse_args()
    evaluator = Evaluation(config)
    evaluator.eval_NLU()
    evaluator.eval_DM()

    print()
