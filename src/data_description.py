# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 13:53:58 2019

@author: Duvernay
"""
from kivy.app import App
from glob import glob

class Class:
    """
    Represent a class.
    """
    def __init__(self, name, key, batch):
        self.name = name
        self.key = key
        self.batch = batch
        self.layout = None


class Box:
    """
    Represent a box and all its features.
    """
    def __init__(self, coordinates, confidence, token, label="None", BIO_prefix="O"):
        self.left = coordinates[0]
        self.top = coordinates[1]
        self.right = coordinates[2]
        self.bottom = coordinates[3]
        self.confidence = confidence
        self.token = token
        self.label = label
        self.BIO_prefix = BIO_prefix
        
    def update_coord(self, coordinates):
        self.left = coordinates[0]
        self.top = coordinates[1]
        self.right = coordinates[2]
        self.bottom = coordinates[3]
    
    def __str__(self):
        return "left = " + str(self.left) + "\n" + \
                "top = " + str(self.top) + "\n" + \
                "right = " + str(self.right) + "\n" + \
                "bottom = " + str(self.bottom) + "\n" + \
                "confidence = " + str(self.confidence) + "\n" + \
                "token = " + str(self.token) + "\n" + \
                "label = " + str(self.label)
                


class Page:
    """
    Represente a document page (for instance for multi-frame TIFF)
    """
    def __init__(self, image_path):
        """
        Document page information.
        """
        self.image_path = image_path
        self.res_X = None
        self.res_Y = None
        self.pg_size_X = None
        self.pg_size_Y = None
        self.button_boxes = {}
    
    def fill_info(self, res_X, res_Y, pg_size_X, pg_size_Y):
        self.res_X = res_X
        self.res_Y = res_Y
        self.pg_size_X = pg_size_X
        self.pg_size_Y = pg_size_Y
        
    def __str__(self):
        """
        Display page information, used for debugging.
        """
        buffer = "res_X = " + str(self.res_X) + "\n"
        buffer += "res_Y = " + str(self.res_Y) + "\n"
        buffer += "pg_size_X = " + str(self.pg_size_X) + "\n"
        buffer += "pg_size_Y = " + str(self.pg_size_Y) + "\n"
        return buffer



                

class CurrentFile:
    """
    Gather relevant files corresponding to the current file.
    """
    def __init__(self, image_path, output_directory, _class=None):
        
        # Information about the document (based on OCR work)
        self.xmlns = "None"
        self.filesize = "None"
        self.engine = "None"
        self.recognition_info = "None"
        self.page_conf_level = "None"
        self.page_proc_time = "None"
        self.pdf = "None"
        self.nbPages = "None"
        self.res_X = "None"
        self.res_Y = "None"
        self.pg_size_X = "None"
        self.pg_size_Y = "None"
        self.BIO_labelling = False
        self._class = _class
        

        # Dictionnary  for accessing label occurrences in the current document from label names
        self.label_color = {}
        self.label_occurrence = {}
        self.label_occurrence["None"] = 0
        
        # Put the first page on the page list
        self.pages = [Page(image_path)]
        # Index of the current displayed page
        self.index_current_page = 0

        # The image path used to find related files
        self.image_path = image_path
        
        self.document_name = ".".join(image_path.split(".")[:-1])
            
        # Consequently guess the ID 
        self.ID = self.document_name.split("\\")[-1]
        
        # Search for a JSON file that matches in the output directory
        if glob(output_directory + "\\" + self.ID + ".json"):
            self.JSON_path = glob(output_directory + "\\" + self.ID + ".json")[0]
        else:
            self.JSON_path = None        
            
        App.get_running_app().root._popup.content.pb.value += 100/App.get_running_app().root.length
        
                
    def __str__(self):
        """
        Display current document information, used for debugging.
        """
        buffer = ""
        for index_page, page in enumerate(self.pages):
            buffer += "numero de page : " + str(index_page) + "\n"
            buffer += page.__str__()
        buffer += "image_path = " + self.image_path + "\n"
        buffer += "document_name = " + self.document_name + "\n"
        if self.JSON_path:
            buffer += "JSON_path = " + self.JSON_path + "\n"
        return buffer


