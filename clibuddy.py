import os
import subprocess
from groq import Groq
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama and load environment variables
init(autoreset=True)
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_command(description):
    """Get command from LLM"""
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a CLI assistant. Current directory: {os.getcwd()}. "
                "Provide ONLY the command, no explanations. "
                "For Windows Command Prompt. "
                "If paths have spaces, use double quotes."
            )
        },
        {
            "role": "user",
            "content": description
        }
    ]

    response = client.chat.completions.create(
        messages=messages,
        model="gemma2-9b-it",
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def is_safe(command):
    """Check if command is safe"""
    return not any(cmd in command.lower() for cmd in ['del', 'rm', 'format'])

def execute_command(command):
    """Execute the command with basic safety checks"""
    try:
        # Handle 'cd' commands differentlym so that script can continue to run
        if command.lower().startswith('cd '):
            path = command[3:].strip().strip('"')
            new_path = os.path.abspath(os.path.join(os.getcwd(), path))
            if os.path.isdir(new_path):
                os.chdir(new_path)
                print(Fore.GREEN + f"Changed directory to {os.getcwd()}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Directory not found: {new_path}" + Style.RESET_ALL)
        else:
            # Execute other commands
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            # Print output
            if result.stdout:
                print(Fore.GREEN + result.stdout + Style.RESET_ALL)
            if result.stderr:
                print(Fore.RED + result.stderr + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)

def run():
    while True:
        try:
            # Show current directory
            print(Fore.BLUE + f"Current: {os.getcwd()}" + Style.RESET_ALL)
            # Get user input
            desc = input(Fore.CYAN + "What do you want to do? (or 'exit'): " + Style.RESET_ALL)
            if desc.lower() == 'exit':
                break
            # Get and show command
            command = get_command(desc)
            print(Fore.YELLOW + f"Command: {command}" + Style.RESET_ALL)
            # If not safe, continue
            if not is_safe(command):
                print(Fore.RED + "Command is not safe. Aborting." + Style.RESET_ALL)
                continue
            # Confirm and execute
            if input("Execute? (y/n): ").lower() == 'y':
                execute_command(command)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}" + Style.RESET_ALL)
            break

if __name__ == "__main__":
    run()