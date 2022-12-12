import os
import subprocess
import json
import sys
import time
from simple_term_menu import TerminalMenu
from getpass import getpass

WORKING_DIR = os.path.dirname(os.path.dirname(__file__))

##Logical buttons are options on a menu screen list,
##  but have the special case that 
class LogicalButton:
    def __init__(self, curr_result):
        self.curr_result = curr_result
        return

"""give logical button objects this object as an attribute ONLY IF 
    - it is going to be a main menu option AND
    - it is going to update the main config"""
class ConfigButton(LogicalButton):
    def __init__(self, curr_result, identity):
        self.identity = identity
        super().__init__(curr_result)
        return
"""
    Note to future developers,
    the overall format for adding a logical button is like this:

    class (class name)(Logical_Button):
        def __init__(self,
                curr_result,                #refer to class LogicalButton                                              
                [optional parameters]       #any other parameters self.run will need 
                ):
            
            STEP 1) set self.option as the string that will be displayed to the user
            
            STEP 2) set any other self.vars that self.run() will need
            
            return
        
        def run(self):
            (the desired code to be executed)
            return self.curr_result

    Example:
    class Cancel(LogicalButton):
        def __init__(self):
            self.option = "Press to Cancel"
            return
        
        def run(self):
            return self.curr_result
            
"""
class Cancel(LogicalButton):
    def __init__(self, curr_result):
        self.option = "Cancel Selection"
        super().__init__(curr_result)
        return
    
    def run(self):
        return self.curr_result

class Shell(LogicalButton):
    def __init__(self, curr_result):
        self.option = "Enter Simulated Shell"
        super().__init__(curr_result)
        return
    
    def run(self):
        print("FYI: This is a simulated shell")
        print("FYI: You are still inside the installer program")
        print("FYI: Use the 'exit' command to go back to the installer program")
        print("FYI: Use the interrupt key to exit the intaller program")
        print("Recommended: Use 'read-only' commands. Unintended behavior may result otherwise")
        while True:
            command = input("sim-sh $ ")
            if command == "exit":
                return self.curr_result
            subprocess.run(command, shell=True)

class Install(LogicalButton):
    def __init__(self, curr_result, 
            ready=False, needed=[], config=None):
        super().__init__(curr_result)
        self.start_install = False
        self._ready = ready
        
        if ready:
            self.option = "Start Install"
        else:
            self.option = "Needed before install:" + str(needed)
        return
    
    def run(self):
        if self._ready:
            self.start_install = True
        return self.curr_result


"""
    Note to future developers,
    the overall format for adding a config button is like this:

    class (class name)(ConfigButton):
        def __init__(self,
                curr_result,                #refer to class LogicalButton
                identity,                   #the config dict's key                                              
                [optional parameters]       #any other parameters self.run will need 
                ):
            
            super().__init__()
            **set any other self.vars that self.run() will need**
            **do NOT add a self.option attribute**
            return
        
        def run(self):
            (the desired code to be executed)
            **make sure to set self.curr_result to what you wish the config'd value relative to the config identity**
            return

    Example:
    class Hostname(ConfigButton):
        def __init__(self, curr_result, identity):
            super().__init__(curr_result, identity)
            return
        
        def run(self):
            hostname = input("Hostname:")
            self.curr_result = hostname
            return
            
"""
class Hostname(ConfigButton):
    def __init__(self, curr_result, identity):
        super().__init__(curr_result, identity)
        return
    
    def run(self):
        print("New System Hostname")
        hostname = input("Enter Hostname:")
        self.curr_result = hostname
        return

class Dedicated_Drives(ConfigButton):
    def __init__(self, curr_result, identity):
        super().__init__(curr_result, identity)
        self.options, self.selections = self._parse_lsblk()
        self.prev_result = self.curr_result.copy()
        
        return
    
    def run(self):
        self.options_toggled = {}
        for options in self.options:
            self.options_toggled[options] = False

        while True:
            vis_options = self._update_vis_opt()
            
            cancel_button = Cancel(self.curr_result)
            vis_options.append(cancel_button.option)
            self.options.append(cancel_button.option)
            self.selections.append(cancel_button)

            boot_select = "Confirm and Select Boot Drive"
            vis_options.append(boot_select)
            self.options.append(boot_select)
            self.selections.append(boot_select)
            
            menu = TerminalMenu(vis_options, title="Select Drives Dedicated to the New System")
            menu_selection_index = menu.show()

            selection = self.selections[menu_selection_index]
            option = self.options[menu_selection_index]

            if isinstance(selection, Cancel):
                self.curr_result = self.prev_result.copy()
                break
            elif selection == boot_select:
                boot_options = []
                boot_selections = []

                self.options.pop()
                self.options.pop()
                self.selections.pop()
                self.selections.pop()

                for options in self.options:
                    if self.options_toggled[options] == True:                        
                        boot_options.append(options)
                        boot_selection_index = self.options.index(options)
                        boot_selections.append(self.selections.__getitem__(boot_selection_index))
                self.curr_result = self._display_boot_menu(boot_options, boot_selections)
                break
            else:
                self.options.pop()
                self.options.pop()
                self.selections.pop()
                self.selections.pop()
                self._toggle(option)
        return

    def _parse_lsblk(self):
        options = []
        selections = []

        with open(WORKING_DIR + "/json/lsblk.json", "r") as lsblk_file:
            loaded_lsblk = json.loads(lsblk_file.read())
        block_devices = loaded_lsblk["blockdevices"]

        for devices in block_devices:
            
            device_tags = devices["name"][0:2]
            accept_tags = [
                "sd",
                "hd",
                "nv"
            ]
            if device_tags not in accept_tags:
                continue
            
            device_parts = 0
            if "children" in devices.keys():
                parts = len(devices["children"])
            
            option = "NAME:" + devices["name"] + ", SIZE:" + devices["size"] + ", PARTS:" + str(device_parts)
            options.append(option)
            
            selection = devices["name"]
            selections.append(selection)

        return options, selections

    def _update_vis_opt(self):
        vis_options = []
        for options in self.options:
            if self.options_toggled[options]:
                vis_options.append("> " + options)
            else:
                vis_options.append(options)
        return vis_options

    def _display_boot_menu(self, options, selections):
        cancel_button = Cancel(self.prev_result)
        options.append(cancel_button.option)
        selections.append(cancel_button)
        
        menu = TerminalMenu(options, title="Select Device to Contain /boot")
        menu_selection_index = menu.show()
        selection = selections[menu_selection_index]

        if isinstance(selection, Cancel):
            return self.prev_result.copy()
        
        options.pop()
        selections.pop()

        output = {}
        for items in selections:
            output[items] = False
            if items == selection:
                output[items] = True
        
        return output

    def _toggle(self, option):
        if self.options_toggled[option]:
            self.options_toggled[option] = False
        else:
            self.options_toggled[option] = True

class Password(ConfigButton):
    def __init__(self, curr_result, identity):
        super().__init__(curr_result, identity)
        return
    
    def run(self):
        while True:
            print("New System Root Password")
            first_input = getpass("Password:")
            second_input = getpass("Confirm Password:")
            if first_input == second_input:
                self.curr_result = first_input
                break
            subprocess.run("clear")
            print("Password Incorrect, try again")
            time.sleep(1)
            subprocess.run("clear")
        return

class Packages(ConfigButton):
    def __init__(self, curr_result, identity):
        super().__init__(curr_result, identity)
        return
    
    def run(self):
        print("New System Optional Packages")
        print("(Space seperated list)")
        input_list = input("Packages:")
        string = ""
        output_list = []

        #while loop parses the string to the curr_opt_needed list
        while True:
            if len(input_list) == 0:
                self.curr_result = output_list
                break
            if input_list[0] == " ":
                input_list = input_list[1:]
            else:
                string += input_list[0]
                input_list = input_list[1:]
                if len(input_list) == 0 or input_list[0] == " ":
                    output_list.append(string)
                    string = ""
        
        #we test to see what packages dont exist, remove them from the list, and notify the user
        failed_packs = self._test_packages_exist()
        if len(failed_packs) == 0:
            return
        if len(failed_packs) != 0:
            for failures in failed_packs:
                pop_index = self.curr_result.index(failures)
                self.curr_result.pop(pop_index)
            print("WARNING: following packages not found in repo and were removed:")
            for failures in failed_packs:
                print(failures)
            dummy_var = input("Press \"Enter\" to continue")

    def _test_packages_exist(self):
        failed_packs = []
        for packages in self.curr_result:
            command = "pacman -Ss ^" + packages + "$"
            test = subprocess.getstatusoutput(command)[0]
            if test != 0:
                failed_packs.append(packages)
        return failed_packs

class Menu():
    def __init__(
            self, title="",                                             #Menu title
            options=[], selections=[],                                  #The displayed options and their corresponding selection
            identity=None, prev_result=None, needed_options=[],         #The type of menu (useful for the config), a backup of the last result, and the needed options for the install button
            cancel=False, shell=False, install=False,                   #Options for logical options to be appended at the bottom of the menu
            ):
        
        self.title = title
        self.options = options
        self.selections = selections
        self.identity = identity
        self.result = prev_result
        self.needed_options = needed_options
        self.start_install = False

        self._add_logical_buttons(cancel, shell, install)   #for each enabled, appends the options and selection list
        
        return
    
    def display(self):
        menu = TerminalMenu(self.options, title=self.title)
        menu_selection_index = menu.show()
        selection = self.selections[menu_selection_index]

        self._test_select_type(selection) #self.result is updated (if not just a logical button)
    
    def _add_logical_buttons(self, cancel, shell, install):
        """
        Notes to future development,
        - DO NOT ADD "ConfigButton" LOGICAL BUTTONS HERE!
        - The overall format for adding a option is like this:

            if object should be added:
                (1) create desired instance of your button, a.k.a instance_object
                (2) append self.options with instance_object.option
                (3) append self.selections with instance_object
        
            Example:
            if cancel:
                cancel_button = Cancel()
                self.options.append(cancel_button.option)
                self.selections.append(cancel_button)
        """
        if cancel:
            cancel_button = Cancel(self.result)
            self.options.append(cancel_button.option)
            self.selections.append(cancel_button)
        
        if shell:
            shell_button = Shell(self.result)
            self.options.append(shell_button.option)
            self.selections.append(shell_button)
        
        if install:

            if len(self.needed_options) == 0:
                install_button = Install(self.result, ready=True)
            else:
                install_button = Install(self.result, needed=self.needed_options)
            self.options.append(install_button.option)
            self.selections.append(install_button)

    def _test_select_type(self, selection):
        if isinstance(selection, Menu):
            selection.display()
            self.result[selection.identity] = selection.result          #result value is made!
            return

        elif isinstance(selection, ConfigButton):
            selection.run()
            self.result[selection.identity] = selection.curr_result
        
        elif isinstance(selection, LogicalButton):
            self.result = selection.run()
            if isinstance(selection, Install):
                self.start_install = selection.start_install
            return                                  #result value is only updated is selection has the attribute "ConfigButton"

        elif type(selection) == list or str or dict:
            self.result = selection                 #result value is made!
            return
        
        else:
            print("ERROR: Selection type not found")
            sys.exit(1)

class collect_config(): #function to be called by another program
    def __init__(self, loaded_config=None):
        if loaded_config != None and self.is_valid_config(loaded_config):
            self.config = loaded_config
        else:
            #self.config.keys() are the identities
            self.config = {
                "keyboard_layout" : "",
                "timezone" : "",
                "dedicated_drives" : {},
                "hostname" : "",
                "root_password" : "",
                "kernel" : "",
                "optional_packages" : []
            }
        
        self.options_needed = self._update_opt_needed()
        
        KEYBOARD_LAYOUTS = self._keyboard_layouts()
        TIMEZONES = list(self._timezones())
        KERNELS = list(self._kernels())

        while True: #this is structured like a do-while loop
            main_menu_options = [
                "Keyboard Layout:   " + self.config["keyboard_layout"],
                "Timezone:          " + self.config["timezone"],
                "Dedicated Drives:  " + str(self.config["dedicated_drives"]),
                "Hostname:          " + str(self.config["hostname"]),
                "Root Password:     " + self._password_indic(),
                "Kernel:            " + self.config["kernel"],
                "Optional Packages: " + str(self.config["optional_packages"])
            ]
            main_menu_selections = [
                Menu(title="Keyboard Layouts", 
                        options=KEYBOARD_LAYOUTS.copy(), selections=KEYBOARD_LAYOUTS.copy(),
                            identity="keyboard_layout", prev_result=self.config["keyboard_layout"],
                                cancel=True, shell=True),
                Menu(title="Timezones", 
                        options=TIMEZONES.copy(), selections=TIMEZONES.copy(),
                            identity="timezone", prev_result=self.config["timezone"],
                                cancel=True, shell=True),
                Dedicated_Drives(self.config["dedicated_drives"], "dedicated_drives"),
                Hostname(self.config, "hostname"),
                Password(self.config["root_password"], "root_password"),
                Menu(title="Kernel",
                        options=KERNELS.copy(), selections=KERNELS.copy(),
                            identity="kernel", prev_result=self.config["kernel"],
                                cancel=True, shell=True),
                Packages(self.config["optional_packages"], "optional_packages")
            ]
            main_menu = Menu(title="Smoothie Processing Slave Install Configuration",
                        options=main_menu_options, selections=main_menu_selections,
                            prev_result=self.config, needed_options=self.options_needed,
                                shell=True, install=True)
            
            main_menu.display()
            self.config = main_menu.result
            self.options_needed = self._update_opt_needed(curr_opt_needed=self.options_needed)
            if main_menu.start_install:
                break
        return

    def _update_opt_needed(self, curr_opt_needed=None): ##Only call this function if self.config is a valid config
        if curr_opt_needed == None:
            curr_opt_needed = [
                "Keyboard Layout",
                "Timezone",
                "Dedicated Drives",
                "Hostname",
                "Root Password",
                "Kernel"
            ]
            curr_opt_needed = self._update_opt_needed(curr_opt_needed=curr_opt_needed)
        else:
            curr_opt_needed = self._curr_opt_toggle(curr_opt_needed, self.config["keyboard_layout"], "", "Keyboard Layout")
            curr_opt_needed = self._curr_opt_toggle(curr_opt_needed, self.config["timezone"], "", "Timezone")
            curr_opt_needed = self._curr_opt_toggle(curr_opt_needed, self.config["dedicated_drives"], {}, "Dedicated Drives")
            curr_opt_needed = self._curr_opt_toggle(curr_opt_needed, self.config["hostname"], "", "Hostname")
            curr_opt_needed = self._curr_opt_toggle(curr_opt_needed, self.config["root_password"], "", "Root Password")
            curr_opt_needed = self._curr_opt_toggle(curr_opt_needed, self.config["kernel"], "", "Kernel")
        return curr_opt_needed
    
    def _curr_opt_toggle(self, curr_opt_needed, opt_made, default_opt, opt_needed_prompt):
        if opt_made == default_opt and opt_needed_prompt not in curr_opt_needed:
            curr_opt_needed.append(opt_needed_prompt)
        elif opt_made != default_opt and opt_needed_prompt in curr_opt_needed:
            curr_opt_needed.remove(opt_needed_prompt)
        return curr_opt_needed
    
    def _keyboard_layouts(self):
        with open(WORKING_DIR + "/json/keyboard_layouts.json", "r") as keyboard_layouts_json:
            keyboard_layout_options = json.load(keyboard_layouts_json)
            return keyboard_layout_options
    
    def _timezones(self):
        with open(WORKING_DIR + "/json/timezones.json", "r") as timezones_json:
            timezones = json.load(timezones_json)
            return timezones

    def _password_indic(self):
        if len(self.config["root_password"]) > 0:
            return "****"
        else:
            return ""

    def _kernels(self):
        return ["linux"]

    def is_valid_config(self, config):
        try:
            if bool(
                str == type(config["keyboard_layout"]) and
                str == type(config["timezone"]) and
                dict == type(config["dedicated_drives"]) and
                str == type(config["hostname"]) and
                str == type(config["root_password"]) and
                str == type(config["kernel"]) and
                list == type(config["optional_packages"])
                ):
                return True
        except:
                print("Config file formatted incorrectly")
                print("Using default config...")
                return False