from Util import globals
import re
import pyperclip

from rich.prompt import Prompt
from datetime import datetime, timedelta

from Util.FileOps import save_data_file,console
from Util.GeneratorOps import generate_new_password,generate_credential_id

def add_cred(arg=None): #DONE 
    from Util.TerminalOps import prompt_options
    if arg==None:
        userName=Prompt.ask("[bold yellow]\t\tInsert Username ") # insert username
        if userName.lower()=="exit" or userName.lower()=="x":
            return "done"
        keywords=Prompt.ask("[bold yellow]\t\tInsert Domains/keywords ") # insert domains/keyword
        if keywords.lower()=="exit" or keywords.lower()=="x":
            return "done"
        keywords=keywords.replace(" ","")
        keywordsList=keywords.split(",")
        PasswordOption=Prompt.ask("[bold yellow]\t\tGenerate or Input password(G\\I)?")
        if PasswordOption.lower()=='g':
            password=generate_new_password()
        elif PasswordOption.lower()=='i':
            password=Prompt.ask("[bold yellow]\t\tInsert Password ") 
            if password.lower()=="exit" or password.lower()=="x":
                return "done"
        elif PasswordOption.lower()=="exit" or PasswordOption.lower()=="x":
            return "done"
        else:
            console.print(f"[bold red] Invalid option")
            return "done"
        # generate and display password
        # display domain, username, password
        
    else:
        keywords=arg[0]
        keywordsList=keywords.split(",")
        
        userName=arg[1]
        if arg[2].lower()=="_" or arg[2].lower()=="-":
            password=generate_new_password()
        else:
            password=arg[2]
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
        quit()
    
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
            "R":"Re-do"
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

def search_cred(arg=None, typ=["keywords","username"]): # DONE
    from Util.TerminalOps import display_collections

    data=globals.tempData
    creds=data.get("credentials")
    if arg==None:
        query=Prompt.ask(f"[bold yellow]\tInsert Keyword/Domain (* for all) ")
        if query.lower()=="x" or query.lower()=="exit":
            return "done"
        elif query.lower()=="*":
            resp=display_collections(creds)
            if resp=="exit":
                return "done"
    else:
        query=arg[0]
    if query!="*":
        query=f".*{query.lower()}.*"

        result=[]
        for cred in creds:
            if "keywords" in typ:    
                for keyword in cred.get("keywords"):
                    check = re.search(query,keyword.lower())
                    # print("domain check",check)
                    if check:
                        result.append(cred)
                        break
            if "username" in typ:
                # print(cred.get("username").lower())
                check = re.search(query,cred.get("username").lower())
                # print("username check",check)
                
                if check and not cred in result:
                    result.append(cred)
                    
        if result==[]:
            console.print(f"[yellow] No data available")
            return "done"
        else:
            if arg==None:
                display_collections(result,arg=True)
            else:
                display_collections(result,arg=False)    
    else:
        resp=display_collections(creds,arg=True)
        if resp=="exit":
            return "done"

def find_cred(arg): #DONE
    from Util.TerminalOps import display_collections
    if arg[0].isdigit() or re.search(f"CR-.*",f"{arg[0].upper()}"):
        if arg[0].isdigit():
            number=int(arg[0])
            if number < 0 or number > 9999:
                console.print(f"[bold red]Number must be between 0 and 9999.")
            formatted_number = f"{number:04d}"
            ID=f"CR-{formatted_number}"
        else:
            ID=arg[0].upper()
    else:
        console.print(f"[bold red] Format is not ID")
    data=globals.tempData
    creds=data.get("credentials")
    result=""
    for cred in creds:
        if cred.get("id")==ID:
            result=cred
            break
    if result=="":
        # output console
        console.rule("credential")
        console.print(f"[bold red]Credential Not Found", justify="center")
        pass
    else:
        # output console
        display_collections(result,mode="search_single",arg=True)
        pass

def update_cred(data=None,arg=None): # DONE
    from Util.TerminalOps import prompt_options
    if arg==None:
        userName=Prompt.ask("[bold yellow]\t\tInsert Username ") # insert username
        if userName.lower()=="exit" or userName.lower()=="x":
            return "done"
        keywords=Prompt.ask("[bold yellow]\t\tInsert Domains/keywords ") # insert domains/keyword
        if keywords.lower()=="exit" or keywords.lower()=="x":
            return "done"
        createNewPassword=Prompt.ask("[bold yellow]\t\tKeep,Generate, or Input password(K\\G\\I)?") # insert domains/keyword
        while createNewPassword.lower()!="k" and createNewPassword.lower()!="g" and createNewPassword.lower()!="i" and createNewPassword.lower()!="x" and createNewPassword.lower()!="exit" and createNewPassword!="":
            console.print(f"[bold red]invalid input {createNewPassword}", justify="center")
            createNewPassword=Prompt.ask("[bold yellow]\t\tKeep,Generate, or Input password(K\\G\\I)?") # insert domains/keyword
        if createNewPassword.lower()=="x" or createNewPassword.lower()=="exit":
            return "done"
        if createNewPassword.lower()=="":
            createNewPassword="k"
        
        keywords=keywords.replace(" ","")
        keywordsList=keywords.split(",")
    
        # generate and display password
        if createNewPassword.lower()=="g":
            password=generate_new_password()
        elif createNewPassword.lower()=="k":
            for pwd in data.get("passwords"):
                if pwd.get("current")==True:
                    password=pwd.get("password")
                    break
                else:
                    password=data.get("passwords")[-1]
        elif createNewPassword.lower()=="i":
            password=password=Prompt.ask("[bold yellow]\t\tInsert Password ")
            if keywords.lower()=="exit" or keywords.lower()=="x":
                return "done"
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
                "R":"Re-Do"
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
        elif choise.lower()=="r": # recursive call
            update_cred(data)
        elif choise=="x" or choise=="X": # exit
            return "done"
    else:
        #data[0]=id
        #data[1]=domain
        #data[2]=username
        #data[3]=password
        data=arg
        expire=datetime.now()+timedelta(30)# delta should be read from config
        credFound=False
        for item in globals.tempData.get("credentials"):
            if item.get("id")==data[0]:
                credFound=True
                if data[1]!='-' and data[1]!='_':
                    rawKeywords=data[1]
                    newKeywords=rawKeywords.split(",")
                    item["keywords"]=newKeywords
                if data[2]!='-' and data[2]!='_':
                    item['username']=data[2]
                if data[3]!='-' and data[3]!='_':
                    for pwd in item.get("passwords"):
                        if pwd.get("current")==True:
                            currentPwd=pwd.get("password")
                        pwd["current"]=False
                    if data[3].lower()=="keep":
                        newPassword=currentPwd
                    elif data[3].lower()=="regen":
                        newPassword=generate_new_password()
                    else:
                        newPassword=data[3]
                    item.get("passwords").append(
                    {
                            "password":newPassword,
                            "startDate":datetime.now().isoformat(),
                            "expireDate":expire.isoformat(),
                            "current":True
                    }
                    )
                sendData=item
        if not credFound:
            console.print(f"[bold red] CredentialID {data[0]} Not found", justify="center")
            quit()
        send={
                "id":data[0],
                "updatedData":sendData
            }    
        save_data_file(send,"update cred")
        console.print(f"[bold purple] Credential Updated !", justify="center")
        console.print(f"[bold Yellow on green] Password:{newPassword}", justify="center")
        quit()
        return sendData

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
