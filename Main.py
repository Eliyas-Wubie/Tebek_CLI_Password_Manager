from all import display_intro, prompt_options, console, generate_credential_id,search_cred,add_cred,update_cred,show_notif, load_config, set_data_file, readFile, checkFile, load_data_file

display_intro()
while True:
    isConfigAvailable=checkFile("./config.json")
    if isConfigAvailable:
        config=readFile("./config.json","json")
        dataPath=config.get("dataPath")
        if dataPath!=None:
            isDataFileAvailable=checkFile(dataPath)
            if isDataFileAvailable:
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
                    }
                    ]
                while True:
                    choice=prompt_options(myList,"MAIN MENU")
                    
                    MainMenuOptions={
                        "N":show_notif,
                        "S":search_cred,
                        "A":add_cred,
                        "U":update_cred
                    }
                    executer=MainMenuOptions.get(choice.upper())
                    executer()
            else:
                set_data_file()
                load_data_file()
        else:
            set_data_file()
            load_data_file()
    else:
        print("there is no config file")
        load_config()