from Util import globals
import re

from rich.prompt import Prompt
from rich.console import Console
from datetime import datetime, timedelta

from Util.FileOps import save_data_file,console
from Util.GeneratorOps import generate_new_password,generate_credential_id

def add_cred(): #DONE 
    from Util.TerminalOps import prompt_options,display_collections
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

def search_cred(s=None,SN=None): # DONE
    from Util.TerminalOps import prompt_options,display_collections

    data=globals.tempData
    creds=data.get("credentials")
    if s==None:
        query=Prompt.ask(f"[bold yellow]\tInsert Keyword/Domain (* for all) ")
    else:
        query=s
    if query.lower()=="x" or query.lower()=="exit":
        return "done"
    elif query.lower()=="*":
        resp=display_collections(creds,SN=SN)
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
        display_collections(result,SN=SN)    

def find_cred():
    pass

def update_cred(data,mode="terminalUI"): # DONE
    from Util.TerminalOps import prompt_options,display_collections
    if mode=="terminalUI":
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
    elif mode=="argument"
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
    from Util.TerminalOps import prompt_options,display_collections

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
    from Util.TerminalOps import prompt_options,display_collections

    # expired notification
    dataFile=globals.tempData
    config=globals.tmpConfig # MAY FIND ISSUE HERE
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
