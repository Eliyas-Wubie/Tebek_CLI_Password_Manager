from all import display_intro, prompt_options, console

# Desplay welcome prompt
display_intro()
myList=[{
    "x":"select xkahjkasdhfjkfhjkfhjksdhfjkasdfhjkfhjk"
}, {
        "y":"select y"
}]
choice=prompt_options(myList)
console.print(f"you have selected---- {choice} ")