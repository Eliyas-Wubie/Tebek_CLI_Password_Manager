# from all import display_intro, prompt_options, console, generate_credential_id,search_cred,add_cred,update_cred,show_notif, load_config, set_data_file, readFile, checkFile, view_data, change_email, change_path, load_data_fileV2,configurations
################# NEW------------------------------------
import argparse
import sys
import os

from Util.TerminalOps import display_intro,prompt_options
from Util.CredentialOps import search_cred,add_cred,show_notif, find_cred,update_cred,view_password_history
from Util.FileOps import load_config,set_data_file,checkFile,load_data_fileV2
from Util.ConfigrationOps import configurations
from Util.OtherOps import get_os_type


AP=argparse.ArgumentParser(description="single letter argument")

AP.add_argument("-a",nargs=3, metavar=('domain', 'username', 'password'),default=['-','-','-'],dest="a",help="Add Credential [Domain Username Password]")
# args.a will be an array containing the incerted series of items
AP.add_argument("-f",nargs=1, metavar=('id'),default=['-'],dest="f",help="Find Credential [Id]")
AP.add_argument("-sd",nargs=1, metavar=('domain'),default=['-'],dest="sd",help="Search Credential using domain")
AP.add_argument("-su",nargs=1, metavar=('username'),default=['-'],dest="su",help="Search Credential using username")
AP.add_argument("-s",nargs=1, metavar=('domain or username'),default=['-'],dest="s",help="Search Credential")
AP.add_argument("-u",nargs=4, metavar=('id','domain', 'username', 'password'),default=['-','-','-','-'],dest="u",help="Update Credential")
AP.add_argument("-vh",nargs=1, metavar=('id'),default=['-'],dest="vh",help="View Credential Password History")

args=AP.parse_args()

if len(sys.argv) == 1:
    display_intro()
    while True:
        currentPlatform=get_os_type()
        if currentPlatform=="Windows":
            app_name = "TBK"
            config_file = "config.json"
            appdata = os.getenv("APPDATA")
            appdataPath=os.path.join(appdata, app_name)
            configpath=os.path.join(appdata, app_name, config_file)
        else:
            configpath="./TBKfiles/config.json"
        isConfigAvailable=checkFile(configpath)
        if isConfigAvailable:
            config=load_config()
            print("config",config)
            dataPath=config.get("dataPath")
            if dataPath!=None:
                isDataFileAvailable=checkFile(dataPath)
                if isDataFileAvailable:
                    # data=load_data_file()
                    data=load_data_fileV2()
                    credentialCount=len(data.get("credentials"))
                    count=show_notif("count")
                    myList=[
                        {
                            "N":f"Notifications (*{count})"
                        },
                        {
                            "S":"Search Credential"
                        },
                        {
                            "A":"Add Credential"
                        },
                        {
                            "C":"Configurations"
                        }
                        ]
                    while True:
                        choice=prompt_options(myList,f"MAIN MENU","main",f"[blue on green] TOTAL CREDENTIALS STORED [bold #ff00ff on #000000] > {credentialCount} < ")
                        
                        MainMenuOptions={
                            "N":show_notif,
                            "S":search_cred,
                            "A":add_cred,
                            "C":configurations,
                        }
                        executer=MainMenuOptions.get(choice.upper())
                        executer()
                else:
                    print("calling set data file from main IsDatafileavailanle is false")
                    set_data_file()
                    load_data_fileV2()
                    dataPath=config.get("dataPath")
                    isDataFileAvailable=checkFile(dataPath)
                    if not isDataFileAvailable:
                        quit()
            else:
                print("calling set data file from main dataPath is none")
                set_data_file()
                load_data_fileV2()
                dataPath=config.get("dataPath")
                isDataFileAvailable=checkFile(dataPath)
                if not isDataFileAvailable:
                    quit()
        else:
            print("Config file not found")
            load_config()
else:
    isConfigAvailable=checkFile("./TBKfiles/config.json")
    if isConfigAvailable:
        config=load_config()
        dataPath=config.get("dataPath")
        if dataPath!=None:
            isDataFileAvailable=checkFile(dataPath)
            if isDataFileAvailable:
                data=load_data_fileV2()
                credentialCount=len(data.get("credentials"))
                if args.a!=['-','-','-']: #handled -tesed
                    add_cred(args.a)
                elif args.f!=['-']: #handled - tested
                    find_cred(args.f)
                elif args.sd!=["-"]: #handled - tasted
                    search_cred(args.sd,["keywords"])
                elif args.su!=["-"]: #handled - tasted
                    search_cred(args.su,["username"])
                elif args.s!=["-"]: #handled - tasted
                    search_cred(args.s,["username","keywords"])
                elif args.u!=['-','-','-','-']: #handled - tasted
                    update_cred(arg=args.u)
                elif args.vh!=['-']:
                    view_password_history(arg=args.u)
                else:
                    quit()                
            else:
                set_data_file()
                load_data_fileV2()
                dataPath=config.get("dataPath")
                isDataFileAvailable=checkFile(dataPath)
                if not isDataFileAvailable:
                    quit()
        else:
            set_data_file()
            load_data_fileV2()
            dataPath=config.get("dataPath")
            isDataFileAvailable=checkFile(dataPath)
            if not isDataFileAvailable:
                quit()
    else:
        print("Config file not found")
        load_config()