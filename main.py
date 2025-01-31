import sys
import logging
import argparse
from chat import Chat
from colorama import Fore, Style, init

# Initialize colorama for colored logging
init(autoreset=True)

# Custom log formatter with colors
class CustomFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, "")
        log_msg = super().format(record)
        return f"{log_color}{log_msg}{Style.RESET_ALL}"

def parse_args():
    parser = argparse.ArgumentParser(description="Chat Application Configuration")

    parser.add_argument("--model", type=str, required=False, default="llama3",
                        help="Specify the model to use for chat.")
    parser.add_argument("--prompt_pre_nlu", type=str, required=False, default="prompts/pre_nlu_prompt.txt",
                        help="Specify the path to the pre NLU prompt.")
    parser.add_argument("--prompt_nlu", type=str, required=False, default="prompts/nlu_prompt.txt",
                        help="Specify the path to the NLU prompt.")
    parser.add_argument("--prompt_dm", type=str, required=False, default="prompts/dm_prompt.txt",
                        help="Specify the path to the DM prompt.")
    parser.add_argument("--prompt_nlg", type=str, required=False, default="prompts/nlg_prompt.txt",
                        help="Specify the path to the NLG prompt.")
    parser.add_argument("--enable_logging", type=bool, default=True,
                        help="Enable logging output. If not specified, logging will be disabled.")
    
    args = parser.parse_args()

    config = {
        "model": args.model,
        "pre_nlu_prompt_path": args.prompt_pre_nlu,
        "nlu_prompt_path": args.prompt_nlu,
        "dm_prompt_path": args.prompt_dm,
        "nlg_prompt_path": args.prompt_nlg,
        "enable_logging": args.enable_logging
    }

    return config

def configure_logging(enable_logging):
    """Set up logging with optional color output."""
    logger = logging.getLogger()
    logger.handlers.clear()  # Clear previous handlers
    logging.getLogger("httpx").setLevel(logging.CRITICAL)
    logging.getLogger("httpcore").setLevel(logging.CRITICAL)
    logging.getLogger("http").setLevel(logging.CRITICAL)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomFormatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    if enable_logging:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)  # Suppress all logs below CRITICAL
    
    logger.addHandler(handler)

    logger.info("Logging is enabled." if enable_logging else "Logging is disabled.")
    print()


def main():
    config = parse_args()
    configure_logging(config["enable_logging"])

    chat = Chat(config)
    chat.run_chat()

if __name__ == "__main__":
    main()
