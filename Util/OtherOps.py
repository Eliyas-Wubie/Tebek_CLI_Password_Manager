import os
import subprocess
import uuid
import platform
import resend

from rich.prompt import Prompt
from rich.console import Console

console = Console()

def get_dev_id(pltform,mode="sn"):
    if pltform=="Linux":
        if mode=="sn":
            try:
                result = subprocess.run(
                    ["sudo", "dmidecode", "-s", "system-serial-number"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError:
                data=get_dev_id(os,"mac")
                return data
                # return "Permission denied or dmidecode not available"
        elif mode=="mac":
            return hex(uuid.getnode())
    elif pltform=="Windows":
        if mode=="sn":
            result = subprocess.run(
            ["wmic", "bios", "get", "serialnumber"],
            capture_output=True,
            text=True,
            check=True
            )
            lines = result.stdout.strip().splitlines()
            for item in lines:
                if item!=None and item!='' and not 'Seri' in item:                    
                    return item
        elif mode=="mac":
            return hex(uuid.getnode())
    else:
        if mode=="sn":
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.splitlines():
                if "Serial Number" in line:
                    return line.split(":")[1].strip()
                else:
                    data=get_dev_id(os,"mac")
                    return data
        elif mode=="mac":
            return hex(uuid.getnode())

def get_os_type():
    os_name = platform.system()
    return os_name

def email_confirmation(confirmation_code, dataEmail):
    resendKey=Prompt.ask(f"Please insert Resend api key to use confirmation")
    resend.api_key = resendKey

    # Send email
    res = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": dataEmail,
        "subject": "file ownership confirmation",
        "html": f"<strong>This is your code {confirmation_code}</strong>"
    })
    console.print(f"[blue bold] Email sent to {dataEmail}")
    return "done"
