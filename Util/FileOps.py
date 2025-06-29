from Util import globals
import os
import base64
import json

from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel

from Util.GeneratorOps import generate_code
from Util.CryptoOps import decrypt_data,encrypt_data,generate_fernet_key_from_password
from Util.OtherOps import get_os_type,get_dev_id,email_confirmation
console = Console()


def load_data_fileV2():
    from Util.TerminalOps import prompt_options
    if globals.tempData=="": # if empty actually decrypt and load
        config=globals.tmpConfig
        if config.get("dataPath")!=None:
            currentPlatform=get_os_type()
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
                    #-----Get Master Password and decryption lv2 -------------------------------------------    
                    if globals.TemporaryKeyHolder=="":
                        console.print(Panel(f"{path}",padding=(0,0),style="bold white on green"),justify="center")
                        masterPWD2=Prompt.ask("[bold yellow]\tMaster Password ", password=True)
                        masterKey=generate_fernet_key_from_password(masterPWD2)
                        globals.TemporaryKeyHolder=masterKey
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
                            return globals.tempData
                        else:
                            quit()
                    dData["credentials"]=decryptedCred
                    #----Seting Data to memory-------------------------------------------------------------
                    globals.tempData=dData.copy()
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
                    config["dataPath"]=globals.tmpTBKpath
                    try:
                        with open(globals.tmpConfigPath, 'w') as f: # use write file fn
                            json.dump(config, f, indent=4)
                    except Exception as e:
                        print(e)
                    
                    confirmationEmail=Prompt.ask(f"[yello bold ] \t Insert Confirmation email ")
                    masterPWD=Prompt.ask(f"Insert Master Password")
                    masterPWD2=Prompt.ask(f"confirm Master Password")
                    if masterPWD!=masterPWD2:
                        return "done"
                    masterKey=generate_fernet_key_from_password(masterPWD2)
                    globals.TemporaryKeyHolder=masterKey
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
                    globals.tempData=template.copy()
                    # print("my tempData ", tempData)
                    credentials=[]
                    encryptedCred=encrypt_data(credentials,masterKey)
                    encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
                    template["credentials"]=encryptedCredStr
                    encryptedData=encrypt_data(template)
                    TBKPath=globals.tmpTBKpath
                    writeFile(encryptedData,TBKPath,"bin")
                    return globals.tempData
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
                config["dataPath"]=globals.tmpTBKpath
                try:
                    with open(globals.tmpConfigPath, 'w') as f: # use write file fn
                        json.dump(config, f, indent=4)
                except Exception as e:
                    print(e)
                
                confirmationEmail=Prompt.ask(f"[yello bold ] \t Insert Confirmation email ")
                masterPWD=Prompt.ask(f"Insert Master Password")
                masterPWD2=Prompt.ask(f"confirm Master Password")
                if masterPWD!=masterPWD2:
                    return "done"
                masterKey=generate_fernet_key_from_password(masterPWD2)
                globals.TemporaryKeyHolder=masterKey
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
                globals.tempData=template.copy()
                # print("my tempData ", tempData)
                credentials=[]
                encryptedCred=encrypt_data(credentials,masterKey)
                encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
                template["credentials"]=encryptedCredStr
                encryptedData=encrypt_data(template)
                TBKPath=globals.tmpTBKpath
                writeFile(encryptedData,TBKPath,"bin")
                return globals.tempData
            elif choise.lower()=="n":
                quit()
            elif choise.lower()=="x" or choise.lower()=="exit":
                quit()

    else:   # returns temp data id it is already loaded, but this should not be needed
        return globals.tempData
        # other code should just use global data to minimize repetetive decryption and loading

def reload_data_file():
    from Util.TerminalOps import prompt_options
    config=globals.tmpConfig
    if config.get("dataPath")!=None:
        path=config.get("dataPath")
        if path!=globals.tmpTBKpath:
            path=globals.tmpTBKpath
        if os.path.exists(path):
            try:
                try:
                    with open(globals.tmpConfigPath, 'w') as f: # use write file fn
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
                globals.tempData=dData.copy()
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
                config["dataPath"]=globals.tmpTBKpath
                try:
                    with open(globals.tmpConfigPath, 'w') as f: # use write file fn
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
                globals.tempData=template.copy()
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

    dataFile=globals.tempData

    config=globals.tmpConfig
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
    globals.tempData=dataFile.copy()
    encryptedCred=encrypt_data(dataFile.get("credentials"),globals.TemporaryKeyHolder)
    encryptedCredStr=base64.b64encode(encryptedCred).decode('utf-8')
    dataFile["credentials"]=encryptedCredStr
    eData=encrypt_data(dataFile)
    writeFile(eData,path,"bin")
    return "done"
    
def load_config(): # DONE
    currentPlatform=get_os_type()
    if currentPlatform=="Windows":
        app_name = "TBK"
        config_file = "config.json"
        appdata = os.getenv("APPDATA")
        # appdataPath=os.path.join(appdata, app_name)
        globals.tmpConfigPath=os.path.join(appdata, app_name, config_file)
    else:
        globals.tmpConfigPath="./TBKfiles/config.json"
    TBKfilesPath="./TBKfiles/"
    if not os.path.exists(TBKfilesPath):
        os.makedirs(os.path.dirname(TBKfilesPath), exist_ok=True)
    if os.path.exists(globals.tmpConfigPath):
        try:
            with open(globals.tmpConfigPath, 'r') as f:
                data = json.load(f)
            globals.tmpConfig=data
            return data
        except json.JSONDecodeError:
            print(f"Warning: File '{globals.tmpConfigPath}' is not valid JSON. Creating a new file with default data.")
            with open(globals.tmpConfigPath, 'w') as f:
                json.dump({}, f, indent=4)
            globals.tmpConfig={}
            return {}
    else:
        print(f"File '{globals.tmpConfigPath}' not found. Creating it with default data.")
        if not os.path.exists(globals.tmpConfigPath):
            os.makedirs(os.path.dirname(globals.tmpConfigPath), exist_ok=True)
        with open(globals.tmpConfigPath, 'w') as f:
            json.dump({}, f, indent=4)
        globals.tmpConfig={}
        return {}
    
def set_data_file(): # DONE
    path=Prompt.ask(f"Insert File Path ")
    pathType=path_type_identifier(path)
    TBKPath=evaluate_path(path,pathType)
    globals.tmpTBKpath=TBKPath
    if path.lower()=="x" or path.lower()=="exit":
        return "done"

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

def path_type_identifier(path):
    osType=get_os_type()
    print("TEST - os type",osType)
    print("TEST - path",path,path[0],path[0].lower()=="/",path[0].lower()=='/')
    if osType=="Windows":
        if not "\\" in path:
            pathType="unspecified"
        elif path[0].lower()=="c":
            pathType="absolut"
        elif path[0].lower()==".":
            pathType="relative"
        print("TEST - Windows type path type",pathType)
        return pathType
    if osType=="Linux":
        if not "\\" in path:
            pathType="unspecified"
        elif path[0].lower()=="/" or path[0].lower()=="\\":
            pathType="absolut"
        elif path[0].lower()==".":
            pathType="relative"
        print("TEST - linux type path type",pathType)
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
