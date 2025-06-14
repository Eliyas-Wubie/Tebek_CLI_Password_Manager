from all import display_intro, prompt_options, console, generate_credential_id,search_cred,add_cred,update_cred,show_notif, load_config, set_data_file, readFile, checkFile, load_data_file, view_data, change_email, change_path, load_data_fileV2
# TemporaryKeyHolder=""
display_intro()
while True:
    isConfigAvailable=checkFile("./config.json")
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
                        "V":"View Data"
                    },
                    {
                        "E": "Change Email"
                    },
                    {
                        "P": "Change Data File Path"
                    }
                    ]
                while True:
                    choice=prompt_options(myList,f"MAIN MENU","main",f"[blue on green] TOTAL CREDENTIALS STORED [bold #ff00ff on #000000] > {credentialCount} < ")
                    
                    MainMenuOptions={
                        "N":show_notif,
                        "S":search_cred,
                        "A":add_cred,
                        "V":view_data,
                        "E":change_email,
                        "P":change_path
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