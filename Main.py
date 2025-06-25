# from all import display_intro, prompt_options, console, generate_credential_id,search_cred,add_cred,update_cred,show_notif, load_config, set_data_file, readFile, checkFile, view_data, change_email, change_path, load_data_fileV2,configurations
################# NEW------------------------------------
import argparse
import sys

from Util.TerminalOps import display_intro,prompt_options
from Util.CredentialOps import search_cred,add_cred,show_notif, find_cred
from Util.FileOps import load_config,set_data_file,checkFile,load_data_fileV2
from Util.ConfigrationOps import configurations


AP=argparse.ArgumentParser(description="single letter argument")

# AP.add_argument('-n', '--notif', action='store_true', dest='n',help='A number input')
# AP.add_argument('-s', '--search', type=str, dest='s',help='A number input')
# AP.add_argument('-a', '--add', type=str, dest='n', help='A number input')
# AP.add_argument('-c', '--config', type=str, dest='n', help='A number input')
# AP.add_argument('--SN', type=str, help='A number input')
##########################################################################

AP.add_argument("-a",nargs=3, metavar=('domain', 'username', 'password'),default=['','',''],dest="a",help="Add Credential")
# args.a will be an array containing the incerted series of items
AP.add_argument("-f",nargs=2, metavar=('domain', 'username'),default=['',''],dest="f",help="Find Credential")
# args.f will be an array containing the incerted series of items
AP.add_argument("-sd",nargs=1, metavar=('domain'),default=[''],dest="sd",help="Search Credential using domain")
# args.sd will be an array containing the incerted series of items
AP.add_argument("-su",nargs=1, metavar=('username'),default=[''],dest="su",help="Search Credential using username")
# args.su will be an array containing the incerted series of items
AP.add_argument("-s",nargs=1, metavar=('domain or username'),default=[''],dest="s",help="Search Credential")
# args.s will be an array containing the incerted series of items
AP.add_argument("-u",nargs=3, metavar=('id','domain', 'username', 'password'),default=['','','',''],dest="u",help="Update Credential")
# args.a will be an array containing the incerted series of items

args=AP.parse_args()

if len(sys.argv) == 1:
    display_intro()
    while True:
        isConfigAvailable=checkFile("./TBKfiles/config.json")
        if isConfigAvailable:
            config=load_config()
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
            print("there is no config file")
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
                #------------------Option One----------------------
                # if args.n:
                #     show_notif()
                # elif args.s:
                #     search_cred(args.s,args.SN)
                # elif args.a:
                #     add_cred()
                # elif args.c:
                #     configurations()
                #-------------Option Two----------------------------
                if args.a:
                    add_cred(args.a)
                elif args.f:
                    find_cred(args.f)
                elif args.sd:
                    search_cred(args.sd)
                elif args.su:
                    search_cred(args.su)
                elif args.s:
                    search_cred(args.s)
                elif args.u:
                    # update_cred(args.u)
                    pass
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
        print("there is no config file")
        load_config()