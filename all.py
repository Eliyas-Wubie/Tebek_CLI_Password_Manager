from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk.configuration import Configuration

from Util.IDgen import load_last_ids,save_last_ids,generate_id
from datetime import datetime, timedelta
import secrets
import random
import os, json, re
from cryptography.fernet import Fernet
console = Console()

# add system password lock logic, encrypt and store password in config, use salt(system built in data).
    # import socket
    # hostname = socket.gethostname()
    # print("Hostname:", hostname)

    # import uuid
    # mac_address = uuid.getnode()
    # mac_address_str = ':'.join(['{:02x}'.format((mac_address >> ele) & 0xff) for ele in range(40, -1, -8)])
    # print("MAC Address:", mac_address_str)

    # import subprocess
    # def get_linux_uuid():
    #     try:
    #         uuid = subprocess.check_output('cat /sys/class/dmi/id/product_uuid', shell=True).decode().strip()
    #         return uuid
    #     except Exception:
    #         return None
    # uuid_value = get_linux_uuid()
    # print("System UUID:", uuid_value)
# generate key from system specific info use the above info, salt and obfuscate
    # from cryptography.fernet import Fernet
    # import base64
    # import json

    # # Your key string (replace this with your actual key string)
    # key_str = "your-key-string-here"  # e.g., "VGVzdEtleVRleHRXb3JrU3RyaW5n"

    # # Convert the key string back to bytes
    # key_bytes = base64.urlsafe_b64decode(key_str.encode('utf-8'))

    # # Initialize Fernet with the key
    # f = Fernet(key_bytes)
    # json_data = json.dumps(data).encode('utf-8')
    # encrypted = f.encrypt(json_data)
# decrypt after reading
    # with open('encrypted_data.bin', 'rb') as f_in:
    #     encrypted_data = f_in.read()
    # decrypted_bytes = f.decrypt(encrypted_data)
    # decrypted_json = decrypted_bytes.decode('utf-8')
    # decrypted_data = json.loads(decrypted_json)
# encrypt before writing
    # # Save encrypted data to a file
    # with open('encrypted_data.bin', 'wb') as f_out:
    #     f_out.write(encrypted)
def Load_key():
    pass

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
    console.print(Panel("Hello and Welcome to Tebek Password Manager. This a local only, Key Based Password Managment tool with High level encryption. you can \n Insert 'X' or 'exit' to leave a menu", title="[bold green on red] Welcome ", style="white on blue"),justify="center")

def prompt_options(options,title="OPTIONS",mode="main"): # DONE
    if mode=="main":
        console.rule(f"[bold]{title.upper()}", style="bold green")
        optionsList=[]
        console.print("\t<Options>\t<Descriptions>           Insert exit/Exit to leave the current prompt")
        console.rule("", style="blue")
        for option in options:     # iterate and display them
            console.print(f"[bold]\t  <{list(option.keys())[0].upper()}>------------[bold green]{list(option.values())[0].capitalize()} ", style="blue",no_wrap=True)
            optionsList.append(list(option.keys())[0].upper())
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
        console.rule(f"'X' or 'exit' to leave")
        choise=Prompt.ask(f"[bold yellow]\tInsert Serial Number for Detail and Action ")
        if choise.isdigit():
            if -1<int(choise)<len(data):
                display_collections(data[int(choise)],"SINGLE","search_single")
            else:
                console.print(f"[red] Invalid Input")
                display_collections(data,title,mode)
        elif choise.upper()=="EXIT"  or choise.upper()=="X":
            return "done"
        else:
            console.print(f"[red] Invalid Input")
            display_collections(data,title,mode)
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
            if resp=="done":
                display_collections(data,title,mode)
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
    
def add_cred(): #DONE 
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
            "A":"Accept"
        },
        {
            "R":"change Domain and email"
        }
    ]
    choise=prompt_options(options,"CONFIRMATION","simple")
    # wait for confirmation
    if choise.upper()=="A": # save to database -> decide database structure
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
    elif choise.upper()=="R": # recursive call
        add_cred()
    elif choise.upper()=="EXIT":
        return "done"

def load_data_file(): # DONE
    config=load_config()
    if config.get("dataPath")!=None:
        path=config.get("dataPath")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                # Decrypt data
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
        for i in range(len(dataFile.get("credentials"))):
            print("matching ", dataFile.get("credentials")[i].get("id"), input.get("id"))
            if dataFile.get("credentials")[i].get("id")==input.get("id"):
                dataFile.get("credentials")[i]=input.get("updatedData")
    elif mode=="del cred":
        for i  in range(len(dataFile.get("credentials"))):
            if dataFile.get("credentials")[i].get("id")==input:
                print("deletteing....")
                del dataFile.get("credentials")[i]
                break
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

def update_cred(data): # DONE
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
        for pwd in data.get("passwords"):
            pwd["current"]=False
        data.get("passwords").append(
            {
                    "password":password,
                    "startDate":datetime.now().isoformat(),
                    "expireDate":expire.isoformat(),
                    "current":True
            }
        )
        data={
            "id":data.get("id"),
            "keywords":keywordsList,
            "username":userName,
            "createdAt":data.get("createdAt"),
            "updatedAt":datetime.now().isoformat(),
            "passwords":data.get("passwords")
        }
        send={
            "id":data.get("id"),
            "updatedData":data
        }
        save_data_file(send,"update cred")
        console.print(f"[bold purple] Credential Updated !", justify="center")
    elif choise=="2": # recursive call
        update_cred(data)
    elif choise=="x" or choise=="X": # exit
        return "done"
    return "done"

def del_cred(data): # DONE
    option=[
        {"Y": "Yes"},
        {"N": "No"}
    ]
    confirmation=prompt_options(option,"CONFIRMATION","simple")
    print("bla bla bla", confirmation)
    if confirmation.upper()=="EXIT":
        print("----- returining done")
        return "done"
    elif confirmation.lower()=="y":
        id=data.get("id")
        save_data_file(id,"del cred")
    elif confirmation.lower()=="n":
        return "done"
    else:
        console.print(f"[red] Invalid Input")
        del_cred(data)
    return "done"

def view_password_history(data): # DONE
    console.rule("Password History")
    console.print(f"{"<Password>":<{20}} \t {"< CreationTime >":<{25}} \t {"<ExpireDate>":<{25}}")
    for item in data.get("passwords"):
        console.print(f"{item.get("password"):<{20}} \t {item.get("startDate"):<{25}} \t {item.get("expireDate"):<{25}}")
    console.rule("")
    return "done"

def show_notif(mode="main"): # DONE - count
    # expired notification
    dataFile=load_data_file()
    config=load_config()
    path=config.get("dataPath")
    notif=[]
    count=0
    # iterate all credentials
    for i in range(len(dataFile.get("credentials"))):
        cred=dataFile.get("credentials")[i]
        passwordIndex=None
        for j in range(len(cred.get("passwords"))):
            pwd=cred.get("passwords")[j]
            if pwd.get("current"):
                currentPwd=pwd
                passwordIndex=j
                break
            else:
                continue
        now = datetime.now()
        expireTime = datetime.fromisoformat(currentPwd.get("expireDate"))
        if now>expireTime:
            template={
                "expireDate":currentPwd.get("expireDate"),
                "passIndex":passwordIndex,
                "cred":cred
            }
            count+=1
            notif.append(template)
        else:
            continue
    if mode=="count":
        return count
    else:
        display_collections(notif,"NOTIFICATION","notif")

def email_confirmation(confirmation_code):
    configuration = Configuration()
    configuration.api_key['api-key'] = 'your_brevo_api_key_here'

    api_client = sib_api_v3_sdk.ApiClient(configuration)
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

    email_content = f"""
    <html>
      <body>
        <p>Hello!</p>
        <p>Your confirmation code is <strong>{confirmation_code}</strong>.</p>
      </body>
    </html>
    """

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": "to_email"}],
        subject="Confirm Your Email Address",
        html_content=email_content,
        sender={"name": "Your App", "email": "your@email.com"}
    )

    try:
        response = api_instance.send_transac_email(email)
        print("Email sent! Message ID:", response['messageId'])
    except ApiException as e:
        print("Error sending email:", e)


    filepath="./config.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return True
        except json.JSONDecodeError:
            print(f"Warning: File '{filepath}' is not valid JSON. Creating a new file with default data.")
            return False
    else:
        print(f"File '{filepath}' not found. Creating config with default data.")
        return False
###################################### New Implementation

def readFile(path, fileType="json"):
    if fileType=="json":
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            print(f"Warning: File '{path}' is not valid JSON. Creating a new file with default data.")
    elif fileType=="txt":
        try:
            with open(path, 'r') as f:
                data = f.read()
            return data
        except:
            print(f"Warning: File '{path}' is not valid TXT. Creating a new file with default data.")
    elif fileType=="bin":
        pass
    else:
        print("file type unspecified")

def checkFile(path):
    if os.path.exists(path):
        return True
    else:
        return False

def decrypt_data(eData):
    decrypted_bytes = f.decrypt(eData)
    decrypted_json = decrypted_bytes.decode('utf-8')
    decrypted_data = json.loads(decrypted_json)
    return decrypted_bytes
def encrypt_data(dData):
    config=load_config()
    json_data = json.dumps(dData).encode('utf-8')
    encrypted = f.encrypt(json_data)
    # Save encrypted data to a file
    with open(f'{config.get("data_path")}', 'wb') as f_out:
        f_out.write(encrypted)
    pass
def get_key():
    pass
def get_encryption_object():
    pass
#REMAINING
    # Testing
    # logging
    # encryption
    # publishing

