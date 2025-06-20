from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from rich.align import Align

import resend
import string
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from cryptography.fernet import Fernet
import base64
import json

from Util.IDgen import load_last_ids,save_last_ids,generate_id
from datetime import datetime, timedelta
import secrets
import random
import platform
import subprocess
import uuid
import os, json, re

console = Console()
TemporaryKeyHolder=""
tempData=""
tmpConfig=""
tmpTBKpath=""

def generate_credential_id(): #DONE
    today = datetime.now().date().isoformat()
    last_ids = tempData.get("lastId")        
    # today = datetime.now().date().isoformat()

    # Get the last number for today; if not found, start from 0
    last_number = last_ids.get(today, -1)
    print("last number is", last_number)
    # Generate a new ID
    new_id, new_last_number = generate_id(last_number)

    # Update the last number for today
    last_ids[today] = new_last_number

    # Save back to JSON
    tempData["lastId"]=last_ids
    return new_id

def generate_new_password(length=17,mode="restricted"): #DONE
    # get random number
    # ASCII Table 32–126 
    # 48–57	0–9	Digits
    # 65–90	A–Z	Uppercase letters
    # 97–122	a–z	Lowercase letters
    password=""
    invalidCharList=["\\","\"","'","`"," "]
    invalidIntList=[92,32,39,124,32]
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
            invalidCharList.extend(optionalInvalidCharList)
            if char in invalidCharList or salted_random_number in invalidIntList:
                i=i-1
            else:
                password+=char
        i+=1
    if len(password)==length:    
        return password
    else:
        console.print(f"[bold red]the length of password generated is not",length,"password: ", password)

def generate_code(length=8):
    print("generating code")
    characters = string.ascii_letters + string.digits  # a-zA-Z0-9
    return ''.join(random.choices(characters, k=length))

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

# def load_data_file(): # DONE
#     print("using depreciated function",__file__, __name__,__spec__)
#     global TemporaryKeyHolder
#     global tmpConfig
#     config=tmpConfig
#     if config.get("dataPath")!=None:
#         path=config.get("dataPath")
#         if os.path.exists(path):
#             try:
#                 encrypted=readFile(path,"bin")
#                 # decrypt the datafile with the static key
#                 dData=decrypt_data(encrypted)
#                 pltform=get_os_type()
#                 devID=get_dev_id(pltform)
#                 dataEmail=dData.get('email')
#                 # print(devID,dData.get('deviceID') )
#                 if devID!=dData.get('deviceID'):
#                     # confirmation
#                     code=generate_code()
#                     email_confirmation(code, dataEmail)
#                     Confirm=Prompt.ask(f"Insert Confirmatuion code")
#                     if code!=Confirm:
#                         console.print(f"[bold red] confirmation mismatch, Exiting program!!")
#                         quit()
#                     else:
#                         dData['deviceID']=devID
#                         eData=encrypt_data(dData)
#                         writeFile(eData,path,"bin")
#                         print("data owner changed")
#                         pass
#                     # compare code
                    

#                 if TemporaryKeyHolder=="":
#                     masterPWD2=Prompt.ask("[bold yellow]\tMaster Password ", password=True)
#                     masterKey=generate_fernet_key_from_password(masterPWD2)
#                     TemporaryKeyHolder=masterKey
#                 original_bytes = base64.b64decode(dData.get("credentials"))
#                 try:
#                     decryptedCred=decrypt_data(original_bytes,TemporaryKeyHolder)
#                 except Exception as e:
#                     console.print(f"invalid Master Password : Exiting Program")
#                     quit()
#                 dData["credentials"]=decryptedCred
#                 # confirmation logic, we should get recpt email from the data, check device id similarity
                    
#                     # get device id
#                     # compare device ids
#                     # if identical continue else confirm and update the device id on the data file
                
#                 return dData
#             except json.JSONDecodeError:
#                 print(f"Warning: File '{path}' is not valid JSON. Creating a new file with default data.")
#         else:
#             console.print(f"The File dose not Exist, Would you like to start from an empty file?")
#             options=[
#                 {
#                     "Y": "yes",
#                 },
#                 {
#                     "N":"no"
#                 }
#             ]
#             choise=prompt_options(options,"CREATE NEW FILE","simple")
            
#             if choise.lower()=="y":
#                 confirmationEmail=Prompt.ask(f"[yello bold ] \t Insert Confirmation email ")
#                 masterPWD=Prompt.ask(f"Insert Master Password")
#                 masterPWD2=Prompt.ask(f"confirm Master Password")
#                 if masterPWD!=masterPWD2:
#                     return "done"
#                 masterKey=generate_fernet_key_from_password(masterPWD2)
#                 TemporaryKeyHolder=masterKey
#                 pltform=get_os_type()
#                 deviceID=get_dev_id(pltform)
#                 template={
#                 "systemConstants":{
#                 "ChrBlackList":[],
#                 "OptionalChrBlackList":[],
#                 "defaultPasswordLength":17,
#                 },
#                 "email":confirmationEmail,
#                 "deviceID":deviceID,
#                 "credentials":[]
#             }
#                 credentials=[]
#                 encryptedCred=encrypt_data(credentials,masterKey)
#                 encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
#                 template["credentials"]=encryptedCredStr
#                 # encrypt here
#                 encryptedData=encrypt_data(template)
#                 # write file
#                 writeFile(encryptedData,path,"bin")
#                 # json.dump(template, f, indent=4)
#                 return "done"
#             elif choise=="2":
#                 pass

def load_data_fileV2():
    global tempData
    global TemporaryKeyHolder
    global tmpConfig
    global tmpTBKpath
    if tempData=="": # if empty actually decrypt and load
        config=tmpConfig
        if config.get("dataPath")!=None:
            path=config.get("dataPath")
            if os.path.exists(path):
                try:
                    #-----Getting encrypted data and doing decryption lv1-----------------------------------
                    encrypted=readFile(path,"bin") 
                    dData=decrypt_data(encrypted)
                    #-----Device Check and email confirmation ----------------------------------------------
                    pltform=get_os_type()
                    devID=get_dev_id(pltform)
                    dataEmail=dData.get('email')
                    if devID!=dData.get('deviceID'): #EMAIL CONFIRMATION
                        code=generate_code()
                        email_confirmation(code, dataEmail)
                        Confirm=Prompt.ask(f"Insert Confirmatuion code")
                        if code!=Confirm:
                            console.print(f"[bold red] confirmation mismatch, Exiting program!!")
                            quit()
                        else:
                            dData['deviceID']=devID
                            eData=encrypt_data(dData)
                            writeFile(eData,path,"bin")
                            print("data owner changed")
                            pass
                    #-----Get Master Password and decryption lv2 -------------------------------------------    
                    if TemporaryKeyHolder=="":
                        console.print(Panel(f"{path}",padding=(0,0),style="bold white on green"),justify="center")
                        masterPWD2=Prompt.ask("[bold yellow]\tMaster Password ", password=True)
                        masterKey=generate_fernet_key_from_password(masterPWD2)
                        TemporaryKeyHolder=masterKey
                    original_bytes = base64.b64decode(dData.get("credentials"))
                    try:
                        decryptedCred=decrypt_data(original_bytes,masterKey)
                    except Exception as e:
                        console.print(f"invalid Master Password")
                        console.print(f"Would you like to Enter a different path")
                        options=[
                            {
                                "Y": "yes",
                            },
                            {
                                "N":"no"
                            }
                        ]
                        choise=prompt_options(options,"CREATE NEW FILE","simple")
                        if choise.lower()=="y":
                            set_data_file()
                            reload_data_file()
                            return tempData
                        else:
                            quit()
                    dData["credentials"]=decryptedCred
                    #----Seting Data to memory-------------------------------------------------------------
                    tempData=dData.copy()
                    return dData
                except json.JSONDecodeError:
                    print(f"Warning: File '{path}' is not valid JSON. Creating a new file with default data.")
            else:
                console.print(f"The File dose not Exist, Would you like to start from an empty file?")
                options=[
                    {
                        "Y": "yes",
                    },
                    {
                        "N":"no"
                    }
                ]
                choise=prompt_options(options,"CREATE NEW FILE","simple")
                
                if choise.lower()=="y":
                    #-----Initial Data file setup--------------------------------------------------------
                    filepath="./TBKfiles/config.json"
                    config["dataPath"]=tmpTBKpath
                    try:
                        with open(filepath, 'w') as f: # use write file fn
                            json.dump(config, f, indent=4)
                    except Exception as e:
                        print(e)
                    
                    confirmationEmail=Prompt.ask(f"[yello bold ] \t Insert Confirmation email ")
                    masterPWD=Prompt.ask(f"Insert Master Password")
                    masterPWD2=Prompt.ask(f"confirm Master Password")
                    if masterPWD!=masterPWD2:
                        return "done"
                    masterKey=generate_fernet_key_from_password(masterPWD2)
                    TemporaryKeyHolder=masterKey
                    pltform=get_os_type()
                    deviceID=get_dev_id(pltform)
                    template={
                        "systemConstants":{
                        "ChrBlackList":[],
                        "OptionalChrBlackList":[],
                        "defaultPasswordLength":17,
                        },
                        
                        "lastId":{},
                        "email":confirmationEmail,
                        "deviceID":deviceID,
                        "credentials":[]
                        }
                    # print("my template ", template)
                    tempData=template.copy()
                    # print("my tempData ", tempData)
                    credentials=[]
                    encryptedCred=encrypt_data(credentials,masterKey)
                    encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
                    template["credentials"]=encryptedCredStr
                    encryptedData=encrypt_data(template)
                    TBKPath=tmpTBKpath
                    writeFile(encryptedData,TBKPath,"bin")
                    return "done"
                elif choise.lower()=="n":
                    return "done"
        else:
            #--- Handling Edge case, where the configuration with data path exists but the file dose not
            console.print(f"The File dose not Exist, Would you like to start from an empty file?")
            options=[
                    {
                        "Y": "yes",
                    },
                    {
                        "N":"no"
                    }
                ]
            choise=prompt_options(options,"CREATE NEW FILE","simple")
            if choise.lower()=="y":
                filepath="./TBKfiles/config.json"
                config["dataPath"]=tmpTBKpath
                try:
                    with open(filepath, 'w') as f: # use write file fn
                        json.dump(config, f, indent=4)
                except Exception as e:
                    print(e)
                
                confirmationEmail=Prompt.ask(f"[yello bold ] \t Insert Confirmation email ")
                masterPWD=Prompt.ask(f"Insert Master Password")
                masterPWD2=Prompt.ask(f"confirm Master Password")
                if masterPWD!=masterPWD2:
                    return "done"
                masterKey=generate_fernet_key_from_password(masterPWD2)
                TemporaryKeyHolder=masterKey
                pltform=get_os_type()
                deviceID=get_dev_id(pltform)
                template={
                    "systemConstants":{
                    "ChrBlackList":[],
                    "OptionalChrBlackList":[],
                    "defaultPasswordLength":17,
                    },
                    
                    "lastId":{},
                    "email":confirmationEmail,
                    "deviceID":deviceID,
                    "credentials":[]
                    }
                # print("my template ", template)
                tempData=template.copy()
                # print("my tempData ", tempData)
                credentials=[]
                encryptedCred=encrypt_data(credentials,masterKey)
                encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
                template["credentials"]=encryptedCredStr
                encryptedData=encrypt_data(template)
                TBKPath=tmpTBKpath
                writeFile(encryptedData,TBKPath,"bin")
                return "done"
            elif choise.lower()=="n":
                quit()
            elif choise.lower()=="x" or choise.lower()=="exit":
                quit()

    else:   # returns temp data id it is already loaded, but this should not be needed
        return tempData
        # other code should just use global data to minimize repetetive decryption and loading

def reload_data_file():
    global tempData
    global tmpConfig
    global tmpTBKpath
    config=tmpConfig
    if config.get("dataPath")!=None:
        path=config.get("dataPath")
        if path!=tmpTBKpath:
            path=tmpTBKpath
        if os.path.exists(path):
            try:
                filepath="./TBKfiles/config.json"
                config["dataPath"]=tmpTBKpath
                try:
                    with open(filepath, 'w') as f: # use write file fn
                        json.dump(config, f, indent=4)
                except Exception as e:
                    print(e)
                #-----Getting encrypted data and doing decryption lv1-----------------------------------
                encrypted=readFile(path,"bin") 
                dData=decrypt_data(encrypted)
                #-----Device Check and email confirmation ----------------------------------------------
                pltform=get_os_type()
                devID=get_dev_id(pltform)
                dataEmail=dData.get('email')
                if devID!=dData.get('deviceID'): #EMAIL CONFIRMATION
                    code=generate_code()
                    email_confirmation(code, dataEmail)
                    Confirm=Prompt.ask(f"Insert Confirmatuion code")
                    if code!=Confirm:
                        console.print(f"[bold red] confirmation mismatch, Exiting program!!")
                        quit()
                    else:
                        dData['deviceID']=devID
                        eData=encrypt_data(dData)
                        writeFile(eData,path,"bin")
                        print("data owner changed")
                        pass
                #-----Get Master Password and decryption lv2 -------------------------------------------    
                masterPWD2=Prompt.ask("[bold yellow]\tMaster Password ", password=True)
                masterKey=generate_fernet_key_from_password(masterPWD2)
                original_bytes = base64.b64decode(dData.get("credentials"))
                try:
                    decryptedCred=decrypt_data(original_bytes,masterKey)
                except Exception as e:
                    console.print(f"invalid Master Password : Exiting Program {e}")
                    quit()
                dData["credentials"]=decryptedCred
                #----Seting Data to memory-------------------------------------------------------------
                tempData=dData.copy()
            except json.JSONDecodeError:
                print(f"Warning: File '{path}' is not valid JSON. Creating a new file with default data.")
        else:
            console.print(f"The File dose not Exist, Would you like to start from an empty file?")
            options=[
                {
                    "Y": "yes",
                },
                {
                    "N":"no"
                }
            ]
            choise=prompt_options(options,"CREATE NEW FILE","simple")
            
            if choise.lower()=="y":
                #-----Initial Data file setup--------------------------------------------------------
                
                filepath="./TBKfiles/config.json"
                config["dataPath"]=tmpTBKpath
                try:
                    with open(filepath, 'w') as f: # use write file fn
                        json.dump(config, f, indent=4)
                except Exception as e:
                    print(e)
                confirmationEmail=Prompt.ask(f"[yello bold ] \t Insert Confirmation email ")
                masterPWD=Prompt.ask(f"Insert Master Password")
                masterPWD2=Prompt.ask(f"confirm Master Password")
                if masterPWD!=masterPWD2:
                    return "done"
                masterKey=generate_fernet_key_from_password(masterPWD2)
                pltform=get_os_type()
                deviceID=get_dev_id(pltform)
                template={
                    "systemConstants":{
                    "ChrBlackList":[],
                    "OptionalChrBlackList":[],
                    "defaultPasswordLength":17,
                    },
                    "lastId":{},
                    "email":confirmationEmail,
                    "deviceID":deviceID,
                    "credentials":[]
                    }
                # print("my template ", template)
                tempData=template.copy()
                # print("my tempData ", tempData)
                credentials=[]
                encryptedCred=encrypt_data(credentials,masterKey)
                encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
                template["credentials"]=encryptedCredStr
                encryptedData=encrypt_data(template)
                writeFile(encryptedData,path,"bin")
                return "done"
            elif choise.lower()=="n":
                return "done"

        # other code should just use global data to minimize repetetive decryption and loading

def save_data_file(input,mode="add cred"): # DONE
    # print("accessing temporary key holder from", __file__)
    global tempData
    global tmpConfig
    dataFile=tempData

    config=tmpConfig
    path=config.get("dataPath")
    if mode=="add cred":
        dataFile.get("credentials").append(input)
    elif mode=="update cred":
        for i in range(len(dataFile.get("credentials"))):
            # print("matching ", dataFile.get("credentials")[i].get("id"), input.get("id"))
            if dataFile.get("credentials")[i].get("id")==input.get("id"):
                dataFile.get("credentials")[i]=input.get("updatedData")
    elif mode=="del cred":
        for i  in range(len(dataFile.get("credentials"))):
            if dataFile.get("credentials")[i].get("id")==input:
                # print("deletteing....")
                del dataFile.get("credentials")[i]
                break
    elif mode=="change email":
        dataFile["email"]=input
    elif mode=="master_change":
        pass
    tempData=dataFile.copy()
    encryptedCred=encrypt_data(dataFile.get("credentials"),TemporaryKeyHolder)
    encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
    dataFile["credentials"]=encryptedCredStr
    eData=encrypt_data(dataFile)
    writeFile(eData,path,"bin")
    return "done"
    
def load_config(): # DONE
    global tmpConfig
    global tmpConfig
    filepath="./TBKfiles/config.json"
    TBKfilesPath="./TBKfiles/"
    if not os.path.exists(TBKfilesPath):
    # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(TBKfilesPath), exist_ok=True)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            tmpConfig=data
            return data
        except json.JSONDecodeError:
            print(f"Warning: File '{filepath}' is not valid JSON. Creating a new file with default data.")
            with open(filepath, 'w') as f:
                json.dump({}, f, indent=4)
            tmpConfig={}
            return {}
    else:
        print(f"File '{filepath}' not found. Creating it with default data.")
        with open(filepath, 'w') as f:
            json.dump({}, f, indent=4)
        tmpConfig={}
        return {}
    
def set_data_file(): # DONE
    global tmpConfig
    global tmpTBKpath
    path=Prompt.ask(f"Insert File Path ")
    pathType=path_type_identifier(path)
    TBKPath=evaluate_path(path,pathType)
    tmpTBKpath=TBKPath
    if path.lower()=="x" or path.lower()=="exit":
        return "done"


def search_cred(): # DONE
    global tempData
    data=tempData
    creds=data.get("credentials")
    query=Prompt.ask(f"[bold yellow]\tInsert Keyword/Domain (* for all) ")
    if query.lower()=="x" or query.lower()=="exit":
        return "done"
    elif query.lower()=="*":
        resp=display_collections(creds)
        if resp=="exit":
            return "done"
    query=f".*{query}.*"

    result=[]
    for cred in creds:    
        for keyword in cred.get("keywords"):
            check = re.search(query,keyword)
            if check:
                result.append(cred)
                break
    if result==[]:
        console.print(f"[yellow] No data available")
        return "done"
    else:
        display_collections(result)    

def update_cred(data): # DONE
    userName=Prompt.ask("[bold yellow]\t\tInsert Username ") # insert username
    keywords=Prompt.ask("[bold yellow]\t\tInsert Domains/keywords ") # insert domains/keyword
    createNewPassword=Prompt.ask("[bold yellow]\t\tGenerate New Password(Y/N) ") # insert domains/keyword
    while createNewPassword.lower()!="y" and createNewPassword.lower()!="n" and createNewPassword.lower()!="x" and createNewPassword.lower()!="exit" and createNewPassword!="":
        print(createNewPassword)
        createNewPassword=Prompt.ask("[bold yellow]\t\tGenerate New Password(Y/N)") # insert domains/keyword
    if createNewPassword.lower()=="x" or createNewPassword.lower()=="exit":
        return "done"
    if createNewPassword=="":
        createNewPassword="n"
    keywords=keywords.replace(" ","")
    keywordsList=keywords.split(",")
    
    # generate and display password
    if createNewPassword=="y":
        password=generate_new_password()
    elif createNewPassword=="n":
        for pwd in data.get("passwords"):
            if pwd.get("current")==True:
                password=pwd.get("password")
            else:
                password=data.get("passwords")[-1]
    if userName=="":
        userName=data.get("username")
    if keywords=="":
        keywordsList=data.get("keywords")
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
            "C":"change Domain and email"
        },
        {
            "x":"discard and exit"
        }
    ]
    
    choise=prompt_options(options,"CONFIRMATION","simple")
    if choise.lower()=="a": # adjust this loigic to append
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
        return data
    elif choise.lower()=="c": # recursive call
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
    if confirmation.upper()=="EXIT":
        return "done"
    elif confirmation.lower()=="y":
        id=data.get("id")
        save_data_file(id,"del cred")
        return "deleted"
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
    return "history"

def show_notif(mode="main"): # DONE - count
    # expired notification
    global tempData
    global tmpConfig
    dataFile=tempData
    config=tmpConfig
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

def email_confirmation(confirmation_code, dataEmail):
    print("sending confirmation email")
    resendKey=Prompt.ask(f"Please insert Resend api key to use confirmation")
    resend.api_key = resendKey

    # Send email
    res = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": dataEmail,
        "subject": "file ownership confirmation",
        "html": f"<strong>This is your code {confirmation_code}</strong>"
    })
    console.print(f"[blue bold] Email sent to {dataEmail}")
    return "done"

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
        with open(path, 'rb') as f_in:
            data = f_in.read()
        return data
    else:
        print("file type unspecified")

def writeFile(data,path, fileType="json"):
    if fileType=="json":
        try:
            with open(path, 'w') as f:
                json.dump(data,f,indent=4)
            return "done"
        except Exception as e:
            print(f"Warning: error writing json. {e} ")
    elif fileType=="txt":
        try:
            with open(path, 'w') as f:
                f.write(data)
            return "done"
        except:
            print(f"Warning: error writing txt.")
    elif fileType=="bin":
        try:
            with open(path, 'wb') as f:
                f.write(data)
            return "done"
        except Exception as e:
            print(f"Warning: error writing bin.{e}")
    else:
        print("file type unspecified")

def checkFile(path):
    if os.path.exists(path):
        return True
    else:
        return False

def decrypt_data(eData,key=""):
    if key=="":
        f = get_encryption_object()
        decrypted_bytes = f.decrypt(eData)
        decrypted_json = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_json)
        return decrypted_data
    else:
        f = get_encryption_object(key)
        decrypted_bytes = f.decrypt(eData)
        decrypted_json = decrypted_bytes.decode('utf-8')
        decrypted_data = json.loads(decrypted_json)
        return decrypted_data

def encrypt_data(dData,key=""):
    if key=="":
        json_data = json.dumps(dData).encode('utf-8')
        f = get_encryption_object()
        encrypted = f.encrypt(json_data)
        return encrypted
    else:
        json_data = json.dumps(dData).encode('utf-8')
        f = get_encryption_object(key)
        encrypted = f.encrypt(json_data)
        return encrypted

def get_key(): 
    key = "I3SJTsjh3tzanQR67JBRhcHNmW55LbtZlR87-3CEVs8=" # static key
    return key

def get_encryption_object(key=""):
    if key=="":
        key_str=get_key()
        f = Fernet(key_str)
        return f
    else:
        key_str=key
        f = Fernet(key_str)
        return f

def get_dev_id(pltform,mode="sn"):
    if pltform=="Linux":
        if mode=="sn":
            try:
                result = subprocess.run(
                    ["sudo", "dmidecode", "-s", "system-serial-number"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError:
                data=get_dev_id(os,"mac")
                return data
                # return "Permission denied or dmidecode not available"
        elif mode=="mac":
            return hex(uuid.getnode())
    elif pltform=="Windows":
        if mode=="sn":
            result = subprocess.run(
            ["wmic", "bios", "get", "serialnumber"],
            capture_output=True,
            text=True,
            check=True
            )
            lines = result.stdout.strip().splitlines()
            for item in lines:
                if item!=None and item!='' and not 'Seri' in item:                    
                    return item
        elif mode=="mac":
            return hex(uuid.getnode())
    else:
        if mode=="sn":
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.splitlines():
                if "Serial Number" in line:
                    return line.split(":")[1].strip()
                else:
                    data=get_dev_id(os,"mac")
                    return data
        elif mode=="mac":
            return hex(uuid.getnode())

def get_os_type():
    os_name = platform.system()
    return os_name

def generate_fernet_key_from_password(password):
    STATIC_SALT = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F'

    # Derive key using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=STATIC_SALT,
        iterations=100_000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def view_data():
    global tempData
    data=tempData
    print(data)

def change_email():
    console.print(f"[yellow on blue] current Email : [yellow on black]{tempData.get("email")}")

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
    global tmpConfig
    config=tmpConfig
    console.print(f"[yellow on blue] Data Path : [yellow on black]{config.get("dataPath")}")
    set_data_file()
    reload_data_file()
    console.print(f"[bold purple] Data path Updated !", justify="center")

def change_master():
    global TemporaryKeyHolder
    oldPwd=Prompt.ask(f"\t\t\t [bold yellow] Insert Previous Password")
    masterKey=generate_fernet_key_from_password(oldPwd)
    if masterKey!=TemporaryKeyHolder:
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
            TemporaryKeyHolder=newMasterKey
            save_data_file(None,"master_change")
            console.print(f"[bold purple] Master password Updated !", justify="center")

def path_type_identifier(path):
    osType=get_os_type()
    if osType=="Windows":
        pass
    if osType=="Linux":
        pass

    if not "\\" in path:
        pathType="unspecified"
    elif path[0].lower()=="c":
        pathType="absolut"
    elif path[0].lower()=="/":
        pathType="absolut" 
    elif path[0].lower()==".":
        pathType="relative"
    return pathType

def evaluate_path(path,pathType):
    if pathType=="unspecified":
        TBKPath=f"./TBKfiles/{path}"
        TBKPath=os.path.abspath(os.path.join(os.getcwd(),TBKPath))
    if pathType=="relative":
        TBKPath=os.path.abspath(os.path.join(os.getcwd(),path))
    if pathType=="absolut":
        TBKPath=path
    
    return TBKPath

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