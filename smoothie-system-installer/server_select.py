import os
import time
from simple_term_menu import TerminalMenu
from header import Builds_Lib

WORKING_DIR = os.path.dirname(__file__)

"""
IF ADDING A BUILD OBJECT TO THE SERVER SELECTOR:
    1.  make the name of the object discriptive to the build that will be done
    
    2.  append to the string list in the var named "options" in the 
        select_server() funciton
            --  this is what will be displayed nametag to the user for your installation
    
    3.  append to the object list in the var named "selections" in the 
        select_server() function
            --  add in an instance of your installation object
"""

def main():
    #user selects the desired build
    build_selected = select_install()
    
    #give the user 5 second countdown to interrupt the build process
    five_sec_countdown("Staring builder in ")

    #we install the build
    build_selected.build()
    return

def select_install():
    library = Builds_Lib()
    options = library.options()
    selections = library.selections()

    #show options and let user select desired system builder
    menu = TerminalMenu(options, title="Select System to Install")
    menu_selection_index = menu.show()
    chosen_build = selections[menu_selection_index]
    return chosen_build

def five_sec_countdown(prompt_string):
    write(prompt_string)
    
    count = 5
    while count > 0:
        write(str(count))
        time.sleep(0.25)
        write(".")
        time.sleep(0.25)
        write(".")
        time.sleep(0.25)
        write(".")
        time.sleep(0.25)
        count -= 1
    
    print("")

def write(string):
    print(string, end='', flush=True)

if __name__ == "__main__":
    main()