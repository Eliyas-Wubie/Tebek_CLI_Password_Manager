
from Util import globals
from rich.prompt import Prompt

from Util.TerminalOps import prompt_options
from Util.CryptoOps import generate_fernet_key_from_password
from Util.FileOps import save_data_file,set_data_file,reload_data_file,console


def view_data():
    data=globals.tempData
    print(data)

def change_email():
    console.print(f"[yellow on blue] current Email : [yellow on black]{globals.tempData.get("email")}")

    newEmail=Prompt.ask(f"\t\t[yellow bold]Insert New Email")
    console.print(f"\t\t [blue on green] NEW EMAIL [bold #ff00ff on #000000]>{newEmail}<", justify="center")
    options=[
                {
                    "Y": "yes",
                },
                {
                    "N":"no"
                }
            ]
    choise=prompt_options(options,"Confirm New Email","simple")
    if choise.lower()=="y":
        save_data_file(newEmail,"change email")
        console.print(f"[bold purple] Email Updated !", justify="center")
    else:
        return "done"

def change_path():
    config=globals.tmpConfig
    console.print(f"[yellow on blue] Data Path : [yellow on black]{config.get("dataPath")}")
    set_data_file()
    reload_data_file()
    console.print(f"[bold purple] Data path Updated !", justify="center")

def change_master():
    oldPwd=Prompt.ask(f"\t\t\t [bold yellow] Insert Previous Password")
    masterKey=generate_fernet_key_from_password(oldPwd)
    if masterKey!=globals.TemporaryKeyHolder:
        console.print(f"[red]Invalid Password",justify="center")
        return "done"
    else:
        newPwd=Prompt.ask(f"\t\t\t [bold yellow] Insert New Password")
        newPwd2=Prompt.ask(f"\t\t\t [bold yellow] Insert New Password again")
        if newPwd!=newPwd2:
            console.print(f"[red]Passwords do not match",justify="center")
            return "done"
        else:
            newMasterKey=generate_fernet_key_from_password(newPwd2)
            globals.TemporaryKeyHolder=newMasterKey
            save_data_file(None,"master_change")
            console.print(f"[bold purple] Master password Updated !", justify="center")

def configurations():
    while True:
        options=[
        {
            "V":"View Data"
        },
        {
            "E": "Change Email"
        },
        {
            "P": "Change Data File Path"
        },
        {
            "M":"Change Master Password"
        },
    ]
        choice=prompt_options(options,f"CONFUGURATION MENU","simple")
        MainMenuOptions={
                            "V":view_data,
                            "E":change_email,
                            "P":change_path,
                            "M":change_master
                        }
        if choice.lower()=="x" or choice.lower()=="exit":
            return "done"
        executer=MainMenuOptions.get(choice.upper())
        executer()