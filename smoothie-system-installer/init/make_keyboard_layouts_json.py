import os
import json

#working dir is always the main repo directory
#aka if the directory of this file is its parent,
#then the working dir is the grandparent in this case
WORKING_DIR = os.path.dirname(os.path.dirname(__file__))

def main():
    print("Creating keyboard layouts file...")
    with open(WORKING_DIR + "/tmp/keyboard_layouts.txt", "r") as messy_keyboard_layouts:
        clean_keyboard_layouts = listify(messy_keyboard_layouts.read())
    
    json_output = json.dumps(clean_keyboard_layouts, indent=4)

    with open(WORKING_DIR + "/json/keyboard_layouts.json", "w") as keyboard_layouts_json:
        keyboard_layouts_json.write(json_output)
    
    return

def listify(messy_input):
    output = []
    string_stack = ""
    while True:
        if messy_input[0] != " " and messy_input != "\n":
            string_stack += messy_input[0]
        elif len(string_stack) > 0 and messy_input[0] != "\n":
            output.append(string_stack)
            string_stack = ""
        messy_input = messy_input[1:]
        
        if len(messy_input) == 0 and len(string_stack) > 0:
            output.append(string_stack)
            string_stack = ""
            break
        elif len(messy_input) == 0 and len(string_stack) == 0:
            break
    return output

if __name__ == "__main__":
    main()