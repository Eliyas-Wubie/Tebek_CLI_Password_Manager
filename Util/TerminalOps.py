from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.prompt import Prompt

from Util.CredentialOps import update_cred, view_password_history, del_cred
console = Console()

def display_intro(): # DONE
    console.print(Panel("Hello and Welcome to Tebek Password Manager. This a local only, Key Based Password Managment tool with High level encryption. you can \n Insert 'X' or 'exit' to leave a menu", title="[bold green on red] Welcome ", style="white on blue"),justify="center")

def prompt_options(options,title="OPTIONS",mode="main",more=""): # DONE
    if mode=="main":
        console.rule(f"[bold green on black] {title.upper()} ", style="bold green")
        optionsList=[]
        console.print("\t<Options>\t<Descriptions>")
        console.rule("", style="blue")
        for option in options:     # iterate and display them
            console.print(f"[bold]\t  <{list(option.keys())[0].upper()}>............[bold green]{list(option.values())[0].capitalize()} ", style="blue",no_wrap=True)
            optionsList.append(list(option.keys())[0].upper())
        allignedMore=Align.center(more)
        console.print(allignedMore)
        console.rule("'X' or 'exit' to leave")
        # provide an input
        choice=Prompt.ask("[bold yellow]\tInsert Option ")
        # return the selected item/dictionalry and validate
        if choice.upper() in optionsList: # valid choice selected
            return choice
        elif choice.upper()=="EXIT" or choice.upper()=="X":      # exit selected
            quit()
        else:                             # invalid input warning and RE-PROMPT
            console.print("[bold red]\t\t<< Alert >>[/bold red] [italic] Invalid input, Please select again")
            value=prompt_options(options)
            return value
    elif mode=="simple":
        console.rule(f"[bold]{title.upper()}", style="bold blue")
        optionsList=[]
        # console.print("\t\t<Options>---------<Descriptions>           Insert exit/Exit to leave the current prompt")
        # console.rule("", style="blue")
        for option in options:     # iterate and display them
            console.print(f"[bold]\t<{list(option.keys())[0].upper()}> --- [bold green]{list(option.values())[0].capitalize()} ", style="blue",no_wrap=True,end="")
            optionsList.append(list(option.keys())[0].upper())
        console.print("")
        console.rule("'X' or 'exit' to leave")
        # provide an input
        choice=Prompt.ask("[bold yellow]\t\tInsert Option ")
        # return the selected item/dictionalry and validate
        if choice.upper() in optionsList: # valid choice selected
            return choice
        elif choice.upper()=="EXIT" or choice.upper()=="X":      # exit selected
            return "EXIT"
        else:                             # invalid input warning and RE-PROMPT
            console.print("[bold red]\t\t<< Alert >>[/bold red] [italic] Invalid input, Please select again")
            value=prompt_options(options,title,mode)
            return value

def display_collections(data,title="DATA",mode="search"):
    console.rule(title)
    if mode=="search":
        console.print(f"{"<SN>":<{4}} \t {"< KEYWORDS >":<{20}} \t {"<USERNAME>":<{25}} \t {"<Password>":<{10}}")
        for i in range(len(data)):
            activePassword="No Active Password"
            for pwd in data[i].get("passwords"):
                if pwd.get("current"):
                    activePassword=pwd.get("password")
            keywords="/".join(data[i].get("keywords"))
            keywords=keywords[:20-3]+"..."
            sn="<"+str(i)+">"
            console.print(f"{sn:<{4}} \t {keywords:<{20}} \t {data[i].get("username"):<{25}} \t {activePassword:<{10}}")
        resultCount=len(data)
        info=f"[green on blue] Found CREDENTIALS [bold #ff00ff on #000000] > {resultCount} < "
        allignedInfo=Align.center(info)
        console.print(allignedInfo)
        console.rule(f"'X' or 'exit' to leave")
        choise=Prompt.ask(f"[bold yellow]\tInsert Serial Number for Detail and Action ")
        if choise.isdigit():
            if -1<int(choise)<len(data):
                resp=display_collections(data[int(choise)],"SINGLE","search_single")
                if resp=="deleted":
                    print("showing after deleting")
                    del data[int(choise)]
                    display_collections(data,title,mode)
                else:
                    display_collections(data,title,mode)
            else:
                console.print(f"[red] Invalid Input")
                display_collections(data,title,mode)
        elif choise.upper()=="EXIT"  or choise.upper()=="X":
            return "exit"
        else:
            console.print(f"[red] Invalid Input")
            display_collections(data,title,mode)
        return "exit"
    if mode=="search_single":
        console.rule(f"Keywords")
        for item in data.get("keywords"):
            console.print(f"\t{item}",end="")
        console.print("")
        console.rule(f"",style="blue")
        console.print(f"\t[bold blue]Username ", data.get("username"))
        activePassword="No Active Password"
        for pwd in data.get("passwords"):
            if pwd.get("current"):
                activePassword=pwd.get("password")
        console.print(f"\t[bold blue]Password ", activePassword)
        options=[
            {"U":"Update"},
            {"V":"View Previous Passowrds"},
            {"D":"Delete Credential"}
        ]
        choise=prompt_options(options,"OPTIONS","simple")
        choise=choise.upper()
        actionMap={
            "U":update_cred,
            "V":view_password_history,
            "D":del_cred
        }
        if choise.upper()=="EXIT" or choise.upper()=="X":
            # print("exiting single view")
            return "done"
        else:
            executor=actionMap[choise]
            resp=executor(data)
            if resp=="deleted":
                return "deleted"
            elif resp=="history":
                display_collections(data,title,mode)
            elif isinstance(resp, dict):
                display_collections(resp,title,mode)
            elif resp=="done":
                display_collections(data,title,mode)
            return "done"
        return "done"
    if mode=="notif":
        console.print(f"{"<SN>":<{4}} \t {"< KEYWORDS >":<{20}} \t {"<USERNAME>":<{25}} \t {"<Expire Date>":<{10}}")
        for i in range(len(data)):
            activePassword="No Active Password"
            for pwd in data[i].get("cred").get("passwords"):
                if pwd.get("current"):
                    activePassword=pwd.get("password")
            keywords="/".join(data[i].get("cred").get("keywords"))
            keywords=keywords[:20-3]+"..."
            sn="<"+str(i)+">"
            console.print(f"{sn:<{4}} \t {keywords:<{20}} \t {data[i].get("cred").get("username"):<{25}} \t {data[i].get("expireDate"):<{10}}")
        console.rule(f"'X' or 'exit' to leave")
        choise=Prompt.ask(f"[bold yellow]\tInsert Serial Number for Detail and Action ")
        if choise.upper()=="EXIT" or choise.upper()=="X":
            return "done"
        else:
            resp=display_collections(data[int(choise)],"SINGLE","search_notif")
            while resp=="continue":
                resp=display_collections(data[int(choise)],"SINGLE","search_notif")
    if mode=="search_notif":
        console.rule(f"Keywords")
        for item in data.get("cred").get("keywords"):
            console.print(f"\t{item}",end="")
        console.print("")
        console.rule(f"",style="blue")
        console.print(f"\t[bold blue]Username ", data.get("cred").get("username"))
        activePassword="No Active Password"
        for pwd in data.get("cred").get("passwords"):
            if pwd.get("current"):
                activePassword=pwd.get("password")
        console.print(f"\t[bold blue]Password ", activePassword)
        options=[
            {"U":"Update"},
            {"V":"View Previous Passowrds"},
            {"D":"Delete Credential"}
        ]
        choise=prompt_options(options,"OPTIONS","simple")
        choise=choise.upper()
        actionMap={
            "U":update_cred,
            "V":view_password_history,
            "D":del_cred
        }
        if choise.upper()=="EXIT" or choise.upper()=="X":
            # print("exiting single view")
            return "done"
        else:
            executor=actionMap[choise.upper()]
            resp=executor(data.get("cred"))
            return "continue"
    