# -*- coding: utf-8 -*-



class InvalidFile(Exception):
    
    def __init__(self, file, message):
        self.file = file
        self.message = message
        
    def __str__(self):
        return "[{}] -> {}".format(self.file, self.message)

class IncompatibleFiles(Exception):
    
    def __init__(self, file1, file2, message):
        self.file1 = file1
        self.file2 = file2
        self.message = message
        
    def __str__(self):
        return "[{}] [{}] -> {}".format(self.file1, self.file2, self.message)
