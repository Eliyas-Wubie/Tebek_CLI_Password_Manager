import platform

os_name = platform.system()

if os_name == "Windows":
    print("Running on Windows")
elif os_name == "Linux":
    print("Running on Linux")
elif os_name == "Darwin":
    print("Running on macOS")
else:
    print(f"Unknown OS: {os_name}")
