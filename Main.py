from all import display_intro, prompt_options, console, generate_credential_id,search_cred,add_cred,update_cred,show_notif, load_config, set_data_file

display_intro()
config=load_config()
if config=={}:
    console.print("The Data File is not specified")
    set_data_file()
myList=[
    {
        "N":"Notifications"
    },
    {
        "S":"Search Credential"
    }, 
    {
        "A":"Add Credential"
    },
    {
        "U":"Update  Credential"
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