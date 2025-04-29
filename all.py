from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
console = Console()

def generate_credential_id():
    pass
def generate_new_password():
    pass
def add_new_credentials():
    pass
def update_credentials():
    pass
def remove_credential():
    pass
def display_intro():
    console.print(Panel("Hello and Welcome to Tebek Password Manager. This a local only, Key Based Password Managment tool with High level encryption", title="[bold green on red] Welcome ", style="white on blue"),justify="center")

def prompt_options(options):
    console.rule("[bold]OPTIONS", style="bold green")
    optionsList=[]
    console.print("\t\t<Options>---------<Descriptions>")
    console.rule("", style="blue")
    for option in options:     # iterate and display them
        console.print(f"[bold]\t\t  <{list(option.keys())[0].upper()}>------[bold green]{list(option.values())[0].capitalize()} ", style="blue",no_wrap=True)
        optionsList.append(list(option.keys())[0].upper())
    console.rule("END")
    # provide an input
    choice=Prompt.ask("[bold yellow]\t\tIncert Option ")
    # return the selected item/dictionalry and validate
    if choice.upper() in optionsList: # valid choice selected
        return choice
    elif choice.upper()=="EXIT":      # exit selected
        return "EXIT"
    else:                             # invalid input warning and RE-PROMPT
        console.print("[bold red]\t\t<< Alert >>[/bold red] [italic] Invalid input, Please select again")
        value=prompt_options(options)
        return value

    
    
def load_data_file():
    pass
def set_data_file():
    pass
def set_config():
    pass
def get_domain_credential():
    pass

