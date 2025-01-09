import csv
import ollama
import random

PATH_DATASET = "dataset/megaGymDataset/megaGymDataset.csv"
prompt_path = "dataset/complete_dataset_prompt.txt"
MODEL = "llama3"

def query_model(user_input: str):
        
    system= open(prompt_path, 'r').read()
    
    messages = [{
        'role': 'system',
        'content': system
    }] #+ self.history.get_history()

    messages.append({
        'role': 'user',
        'content': user_input
    })

    # self.history.add('user', user_input)

    response = ollama.chat(model=MODEL, messages=messages)

    return response['message']['content']


if __name__ == "__main__":
    # Read the file into memory
    with open(PATH_DATASET, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)  # Read all rows into memory

    # Iterate over rows and modify if needed
    for row in rows:

        if row[7] == "":
            random_number = random.randint(1, 10)
            row[7] = str(random_number)  # Replace the empty cell with the random number
            print(random_number)
        
        if row[2] == "":

            input_string = (
                f"Provide the description of the exercise with the following information:\n"
                f"Name -> {row[1]},\n"
                f"Type -> {row[3]},\n"
                f"Body part -> {row[4]},\n"
                f"Equipment -> {row[5]},\n"
                f"Level -> {row[6]}"
            )
            print(f"input --> {input_string}")
            print()
            output = query_model(input_string)
            print("output --> " + output)
            print()
            row[2] = output

    # Write the updated rows back to the file
    with open(PATH_DATASET, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print("Processing complete. Updated rows have been written back to the file.")
