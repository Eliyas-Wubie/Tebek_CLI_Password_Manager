from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from Util.IDgen import load_last_ids,save_last_ids,generate_id
from datetime import datetime, timedelta
import secrets
import random
import os, json, re
console = Console()

def generate_credential_id(): #DONE
    last_ids = load_last_ids()
    today = datetime.now().date().isoformat()

    # Get the last number for today; if not found, start from 0
    last_number = last_ids.get(today, -1)

    # Generate a new ID
    new_id, new_last_number = generate_id(last_number)

    # Update the last number for today
    last_ids[today] = new_last_number

    # Save back to JSON
    save_last_ids(last_ids)
    return new_id

def generate_new_password(length=17,mode="unrestricted"): #DONE
    # get random number
    # ASCII Table 32–126 
    # 48–57	0–9	Digits
    # 65–90	A–Z	Uppercase letters
    # 97–122	a–z	Lowercase letters
    password=""
    invalidCharList=["\\","\"","'","`"," "]
    invalidIntList=[92,32,39,124],32
    optionalInvalidCharList=["$","#","&",":",";","=",")","(","]","[","}","{",">","<",".",",","?","!","~"]
    i=0
    while i<length:
        salt = secrets.token_bytes(16)
        seed = int.from_bytes(salt, 'big')
        rng = random.Random(seed)
        salted_random_number = rng.randint(32, 126)
        char=chr(salted_random_number)
        if mode=="unrestricted":
            if char in invalidCharList or salted_random_number in invalidIntList:
                i=i-1 
            else:
                password+=char
        else:
            invalidList=invalidCharList.extend(optionalInvalidCharList)
            if char in invalidList or salted_random_number in invalidIntList:
                i=i-1
            else:
                password+=char
        i+=1
    if len(password)==length:    
        return password
    else:
        console.print(f"[bold red]the length of password generated is not",length,"password: ", password)
    
def display_intro(): # DONE
    console.print(Panel("Hello and Welcome to Tebek Password Manager. This a local only, Key Based Password Managment tool with High level encryption", title="[bold green on red] Welcome ", style="white on blue"),justify="center")

def prompt_options(options,title="OPTIONS",mode="main"): # DONE
    if mode=="main":
        console.rule(f"[bold]{title.upper()}", style="bold green")
        optionsList=[]
        console.print("\t<Options>---------<Descriptions>           Insert exit/Exit to leave the current prompt")
        console.rule("", style="blue")
        for option in options:     # iterate and display them
            console.print(f"[bold]\t  <{list(option.keys())[0].upper()}>------[bold green]{list(option.values())[0].capitalize()} ", style="blue",no_wrap=True)
            optionsList.append(list(option.keys())[0].upper())
        console.rule("END")
        # provide an input
        choice=Prompt.ask("[bold yellow]\tInsert Option ")
        # return the selected item/dictionalry and validate
        if choice.upper() in optionsList: # valid choice selected
            return choice
        elif choice.upper()=="EXIT":      # exit selected
            return "EXIT"
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
        console.rule("END")
        # provide an input
        choice=Prompt.ask("[bold yellow]\t\tInsert Option ")
        # return the selected item/dictionalry and validate
        if choice.upper() in optionsList: # valid choice selected
            return choice
        elif choice.upper()=="EXIT":      # exit selected
            return "EXIT"
        else:                             # invalid input warning and RE-PROMPT
            console.print("[bold red]\t\t<< Alert >>[/bold red] [italic] Invalid input, Please select again")
            value=prompt_options(options)
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
        choise=Prompt.ask(f"[bold yellow]\tInsert Serial Number for Detail and Action ")
        display_collections(data[int(choise)],"SINGLE","search_single")
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
            {"1":"Update"},
            {"2":"View Previous Passowrds"},
            {"3":"Delete Credential"}
        ]
        choise=prompt_options(options,"OPTIONS","simple")
        actionMap={
            "1":update_cred,
            "2":view_password_history,
            "3":del_cred
        }
    # console.rule(title)

def add_cred(): #DONE 
    # console.print(f"====>  Adding cred ........")
    # console.print(f"")
    userName=Prompt.ask("[bold yellow]\t\tInsert Username ") # insert username
    keywords=Prompt.ask("[bold yellow]\t\tInsert Domains/keywords ") # insert domains/keyword
    keywords=keywords.replace(" ","")
    keywordsList=keywords.split(",")
    
    # generate and display password
    password=generate_new_password()
    # display domain, username, password
    console.rule(f"Keywords")
    for item in keywordsList:
        console.print(f"\t{item}",end="")
    console.print("")
    console.rule(f"",style="blue")
    console.print(f"\t[bold blue]Username ", userName)
    console.print(f"\t[bold blue]Password ", password)
    # show options 
    options=[
        {
            "1":"Accept"
        },
        {
            "2":"change Domain and email"
        },
        {
            "x":"discard and exit"
        }
    ]
    choise=prompt_options(options,"CONFIRMATION","simple")
    # wait for confirmation
    if choise=="1": # save to database -> decide database structure
        expire=datetime.now()+timedelta(30)# delta should be read from config
        template={
            "id":generate_credential_id(),
            "keywords":keywordsList,
            "username":userName,
            "createdAt":datetime.now().isoformat(),
            "updatedAt":"",
            "passwords":[
                {
                    "password":password,
                    "startDate":datetime.now().isoformat(),
                    "expireDate":expire.isoformat(),
                    "current":True
                }
                ]
        }
        save_data_file(template,"add cred")
        console.print(f"[bold purple] New Credential Saved !", justify="center")
    elif choise=="2": # recursive call
        add_cred()
    elif choise=="x" or choise=="X": # exit
        return "done"

def load_data_file(): # DONE
    config=load_config()
    if config.get("dataPath")!=None:
        path=config.get("dataPath")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                return data
            except json.JSONDecodeError:
                print(f"Warning: File '{path}' is not valid JSON. Creating a new file with default data.")
        else:
            console.print(f"The File dose not Exist, Would you like to start from an empty file?")
            options=[
                {
                    "1": "yes",
                },
                {
                    "2":"no"
                }
            ]
            choise=prompt_options(options,"CREATE NEW FILE","simple")
            
            template={
                "systemConstants":{
                "ChrBlackList":[],
                "OptionalChrBlackList":[],
                "defaultPasswordLength":17,
                },
                "credentials":[]
            }
            if choise=="1":
                with open(path, 'w') as f:
                    json.dump(template, f, indent=4)
                return template
            elif choise=="2":
                pass

def save_data_file(input,mode="add cred"): # DONE
    dataFile=load_data_file()
    config=load_config()
    path=config.get("dataPath")
    if mode=="add cred":
        dataFile.get("credentials").append(input)
    elif mode=="update cred":
        dataFile.get("credentials")[input.get("id")]=input.get("updatedData")
    elif mode=="del cred":
        pass
    with open(path, 'w') as f:
        json.dump(dataFile, f, indent=4)
        return "done"
    
def load_config(): # DONE
    filepath="./config.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            print(f"Warning: File '{filepath}' is not valid JSON. Creating a new file with default data.")
            with open(filepath, 'w') as f:
                json.dump({}, f, indent=4)
            return {}
    else:
        print(f"File '{filepath}' not found. Creating it with default data.")
        # Ensure the directory exists before creating the file
        # directory = os.path.dirname(filepath)
        # if directory and not os.path.exists(directory):
        #     os.makedirs(directory)
        with open(filepath, 'w') as f:
            json.dump({}, f, indent=4)
        return {}
    
def set_data_file(): # DONE
    filepath="./config.json"
    path=Prompt.ask(f"Insert File Path : ")
    # Copy to Known path for future use
    config=load_config()
    config["dataPath"]=path
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=4)
    # Create config file that specifies the path - this may be the better way

def search_cred(): # DONE
    data=load_data_file()
    query=Prompt.ask(f"[bold yellow]\tInsert Keyword/Domain ")
    query=f".*{query}.*"
    creds=data.get("credentials")
    result=[]
    for cred in creds:    
        for keyword in cred.get("keywords"):
            check = re.search(query,keyword)
            if check:
                result.append(cred)
                break
    
    display_collections(result)    

def update_cred(data): 
    userName=Prompt.ask("[bold yellow]\t\tInsert Username ") # insert username
    keywords=Prompt.ask("[bold yellow]\t\tInsert Domains/keywords ") # insert domains/keyword
    keywords=keywords.replace(" ","")
    keywordsList=keywords.split(",")
    
    # generate and display password
    password=generate_new_password()
    # display domain, username, password
    console.rule(f"Keywords")
    for item in keywordsList:
        console.print(f"\t{item}",end="")
    console.print("")
    console.rule(f"",style="blue")
    console.print(f"\t[bold blue]Username ", userName)
    console.print(f"\t[bold blue]Password ", password)
    # show options 
    options=[
        {
            "1":"Accept"
        },
        {
            "2":"change Domain and email"
        },
        {
            "x":"discard and exit"
        }
    ]
    choise=prompt_options(options,"CONFIRMATION","simple")
    if choise=="1": # adjust this loigic to append
        expire=datetime.now()+timedelta(30)# delta should be read from config 
        template={
            "id":generate_credential_id(),
            "keywords":keywordsList,
            "username":userName,
            "createdAt":datetime.now().isoformat(), # change here to make it the original
            "updatedAt":"", # change here to add the latest date
            "passwords":[ # append here and turn the previous false to true
                {
                    "password":password,
                    "startDate":datetime.now().isoformat(),
                    "expireDate":expire.isoformat(),
                    "current":True
                }
                ]
        }
        save_data_file(template,"add cred")
        console.print(f"[bold purple] New Credential Saved !", justify="center")
    elif choise=="2": # recursive call
        update_cred(data)
    elif choise=="x" or choise=="X": # exit
        return "done"

def del_cred():
    # confirm,
    # dlete,
    # save
    pass

def view_password_history():
    # acess, format, display all the password hostory, in time order, with active collored uniquely
    pass

def show_notif():
    pass

