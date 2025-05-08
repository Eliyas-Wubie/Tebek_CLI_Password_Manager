from all import display_intro, prompt_options, console, generate_credential_id,search_cred,add_cred,update_cred,show_notif, load_config, set_data_file

display_intro()
config=load_config()
if config=={}:
    console.print("The Data File is not specified")
    set_data_file()
myList=[
    {
        "0":"Notifications"
    },
    {
        "1":"Search A Credential"
    }, 
    {
        "2":"Add a New Credential"
    },
    {
        "3":"Update a Credential"
    }
    ]
while True:
    choice=prompt_options(myList,"MAIN MENU")
    MainMenuOptions={
        "0":show_notif,
        "1":search_cred,
        "2":add_cred,
        "3":update_cred
    }
    if choice.lower()=="exit":
        break
    executer=MainMenuOptions.get(choice)
    executer()