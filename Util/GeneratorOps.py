from Util import globals
import secrets
import random
import string
from datetime import datetime
from rich.console import Console
from Util.IDgen import generate_id

console = Console()

def generate_credential_id(): #DONE
    today = datetime.now().date().isoformat()
    last_ids = globals.tempData.get("lastId")        
    # today = datetime.now().date().isoformat()

    # Get the last number for today; if not found, start from 0
    last_number = last_ids.get(today, -1)
    print("last number is", last_number)
    # Generate a new ID
    new_id, new_last_number = generate_id(last_number)

    # Update the last number for today
    last_ids[today] = new_last_number

    # Save back to JSON
    globals.tempData["lastId"]=last_ids
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
