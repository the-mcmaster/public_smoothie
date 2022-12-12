from builds.Arch_Server_Processing_Slave import Arch_Server_Processing_Slave

class Builds_Lib():
    def __init__(self):
        self.library = {
            "Arch Server Processing Slave" : Arch_Server_Processing_Slave()
        }
    
    def options(self):
        return list(self.library.keys())
    
    def selections(self):
        return list(self.library.values())