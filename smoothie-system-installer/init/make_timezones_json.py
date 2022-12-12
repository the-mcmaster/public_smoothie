import os
import json

#working dir is always the main repo directory
#aka if the directory of this file is its parent,
#then the working dir is the grandparent in this case
WORKING_DIR = os.path.dirname(os.path.dirname(__file__))


def main():
    print("Creating timezones file...")
    with open(WORKING_DIR + "/tmp/timezones.txt", "r") as messy_timezones:
        clean_timezones = listify(messy_timezones.read())
    
    json_output = json.dumps(clean_timezones, indent=4)
    
    with open(WORKING_DIR + "/json/timezones.json", "w") as timezones_file:
        timezones_file.write(json_output)

    return

def listify(messy_input):
    output = []
    string_stack = ""
    while len(messy_input) > 0:
        if messy_input[0] != " ":
            string_stack += messy_input[0]
        else:
            if len(string_stack) > 0:
                output.append(string_stack)
                string_stack = ""
        messy_input = messy_input[1:]
    return output

if __name__ == "__main__":
    main()