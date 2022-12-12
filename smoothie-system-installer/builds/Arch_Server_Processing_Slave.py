"""
IF ADDING A NEW BUILDER OBJECT:
    RULES: 
    
    1.  The name of the object needs to be unique and descriptive
    
    2.  If selected by server_select.py, will call this object's build function 
            --  this funciton should be completely independent from the rest of the file
                --  a.k.a, treat the object.build as if it is its own file

    3.  If only a single install script is required
        1.  write the installer script in the object's funtion "install"
        2.  use relative imports to import these scripts in this file's
            object.build function for your object

    4.  If the build requires a seperate configurate step and install step,
        1.  write the configuration script in the repo foler "config"
        2.  write the installer script in the repo folder "install"
        3.  use relative imports to import these scripts in this file's
            object.build function for your object

    5.  The object needs to be added to the server_select.py file
            --  documentation is included as a comment in the server_select.py 
                program on how this needs to be done
"""

import config.arch_process_slave as ConfigCollector
import installer.arch_process_slave_install as Installer

class Arch_Server_Processing_Slave():
    def build(self):
        #Load the auto-install config menu and gather configuration options form user
        
        install_config = self._collect_config()

        while True:
            success_code = self._start_install(install_config)
            if success_code == 0:
                break
            elif success_code == 1:
                install_config = self._collect_config(install_config)
            else:
                sys.exit(1)
    
    def _collect_config(self, config=None):
        install_config_choose = ConfigCollector.collect_config(config)
        return install_config_choose.config
    
    def _start_install(self, config):
        output_code = Installer.install(config)
        return output_code