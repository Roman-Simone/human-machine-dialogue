from chat import Chat
import argparse

def parse_args():

    parser = argparse.ArgumentParser(description="Chat Application Configuration")

    parser.add_argument(
        "--model",
        type=str,
        required=False,
        default="llama3",
        help="Specify the model to be used for the chat application."
    )
    parser.add_argument(
        "--prompt_nlu",
        type=str,
        required=False,
        default="prompts/nlu_prompt.txt",
        help="Specify the path to the NLU prompt."
    )
    parser.add_argument(
        "--prompt_dm",
        type=str,
        required=False,
        default="prompts/dm_prompt.txt",
        help="Specify the path to the DM prompt."
    )
    parser.add_argument(
        "--prompt_nlg",
        type=str,
        required=False,
        default="prompts/nlg_prompt.txt",
        help="Specify the path to the NLG prompt."
    )

    args = parser.parse_args()

    config = {
        "model": args.model,
        "nlu_prompt_path": args.prompt_nlu,
        "dm_prompt_path": args.prompt_dm,
        "nlg_prompt_path": args.prompt_nlg
    }

    return config

def main():

    config = parse_args()
    
    chat = Chat(config)
    chat.run_chat()


if __name__ == "__main__":
    
    main()