from kivy.app import App
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty, DictProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from glob import glob
from os.path import join
from PIL import Image as ImagePIL
import Zoom
import os
from kivy.graphics import Color, Rectangle
from kivy.config import Config
from kivy.uix.checkbox import CheckBox
import json
from kivy.graphics import Line, InstructionGroup
import ColorWheel2
import shutil
import traceback
from kivy.animation import Animation
import zipfile
import ast
from kivy.clock import Clock
import threading
from functools import partial
import win32api
from HelpDisplayer import HelpDisplayer
from Resizer import ResizableButton
from util import *
import LinePlayground
from popups import (MetadataPopup, ProjectPopup, ColorPopup, 
                    DelClassPopup, ErrorPopup, WarningPopup, DelLabelPopup, 
                    AddClassPopup, DefineHotKeyPopup, ArchivePopup, 
                    QuitPopup, GoToPopup)
import popups
from exceptions import InvalidFile, IncompatibleFiles
from cancellation import Canceller
from graphical_elements import ImageButton, Token, BIO_Label
import graphical_elements
from data_description import Class, Box, Page, CurrentFile
from LoadDialog import LoadDialog

Config.set('input', 'mouse', 'mouse,disable_multitouch,multitouch_on_demand')   # Avoid using multitouch (like it was running on a mobile phone)
Config.adddefaultsection('previously')                                          # Add the section used by the app to remember user choices of last sessions
Config.write()                                                                  # Write it in the .kivy.config.ini file

Window.maximize()   # Fullscreen



class AppManager(ScreenManager):
    """
    Manage the main part of the app
    """
    
    # References to several objects
    
    
    classification = BooleanProperty(None)                  # Reference to the boolean that indicates if user is classifying
    labelling = BooleanProperty(None)                       # Reference to the boolean that indicates if user is labelling
    
    
    current_filepath = StringProperty(None)               # Reference to the path of the document currently displayed
    current_filename = StringProperty("Document name")      # Reference to the document name of the document currently displayed
    current_document = None                                 # Document currently displayed
    page_num = ObjectProperty(None)                         # Reference to the Label that shows the page counter
    
    class_box = ObjectProperty(BoxLayout)                   # Reference to the BoxLayout containing all class icons
    
    my_zoom = ObjectProperty(None)                          # Reference to the Zoom object that display the document and the boxes. It allows to move the document, zoom in, zoom out...
    my_box = ObjectProperty(None)                           # Reference to the my_zoom parent, a FloatLayout object
    my_image = ObjectProperty(None)                         # Reference to the Image object present inside the Zoom object
    
    
    # Referenc to the various checkboxes
    checkbox_showboxes = ObjectProperty(None)                           
    checkbox_showbackground = ObjectProperty(None)
    checkbox_showtokens = ObjectProperty(None)
    checkbox_refocus = ObjectProperty(None)
    checkbox_boxinside = ObjectProperty(None)
    checkbox_switch = ObjectProperty(None)
    accordion_BIO = ObjectProperty(None)
    accordion_tool = ObjectProperty(None)
        
    box_beginning = ObjectProperty(None)
    
    button_change_everything = ObjectProperty(None)
    
    tool_buttons = ListProperty(None)
    label_box = ObjectProperty(None)                        # Reference to the box containing labels used in labelling
    
    save_icone = ObjectProperty(None)
    
    resizer = ObjectProperty(None)
    
    
    bio_box = ObjectProperty(None)
    
    object_list = ListProperty({})

    
    # Some attributs
    
    inside_textbox = False          # If user is writting a label name
    checkbox_list = []              # List of label checkboxes
    global_label_color = {}         # Dictionnary for accessing label colors from label names - This concerns the whole project
    cursor_tool = "Tag"             # The mode of labelling (when creating a rectangle)
    sudden_stop = True              # If user is suddenly leaving the application
    ratio = 1                       # Ratio of the image
    keyboard = {}                   # Access the computer key picture thanks to the ASCII code of the key
    class_directory = {}            # Access the name of the corresponding class thanks to the ASCII code of the key
    documents = []                  # All the paths of each document in the dataset


    in_Popup = DictProperty({'AddClassPopup': False,
                             'ArchivePopup': False,
                             'ColorPopup': False,
                             'DefineHotKeyPopup': False,
                             'DelClassPopup': False,
                             'DelLabelPopup': False,
                             'ErrorPopup': False,
                             'GoToPopup': False,
                             'MetadataPopup': False,
                             'ProjectPopup': False,
                             'QuitPopup': False,
                             'WarningPopup': False
                             })
    
    dataset = StringProperty("")                  # Path of the dataset
    output_directory = None         # Path of the output directory
    index_document = None           # Index of the document currently displayed
    previous_frame_button_disabled = True           # If user cannot switch to the previous frame of the multi frame TIFF
    next_frame_button_disabled = True           # Same for next frame
    actual_current_filepath = "None"# Temporary variable used to save document path
    old_current_filepath = "None"   # Temporary variable used to save document path
    tokens_to_buttons = {}          # Dictionnary for accessing buttons from tokens
    buttons_to_tokens = {}          # Dictionnary for accessing tokens from buttons
    tokens_already_loaded = False   # If tokens have already been loaded (optimize time during switching between documents)
    current_pressed_button = None   # The button currently pressed (used in my_zoom)
    
    during_undo = False
    temporary_dataset = False
    bio_tool = "O"
    resizer = None
    
    loadDial = None

    temp_tool_box = None
    standard_keys = {"prev": 273, "next": 274, "prev_frame": 276, "next_frame": 275, "prev_label": 256, "next_label": 257, \
                 "tag": 49, "create": 50, "encapsulate": 51, "merge": 52, "remove": 53, "modify": 54, "metadata": 9, \
                 "approval": 178, "project-metrics": 42, "help": 44}
    used_keys = DictProperty(ast.literal_eval(Config.getdefault('previously', 'shortcuts', standard_keys.__str__())))
    if used_keys.defaultvalue.keys() != standard_keys.keys():
        used_keys = standard_keys

    last_document_ID = None
    
    last_document_found = False
    is_approved = BooleanProperty(False)
    nb_approved = 0
    nb_documents = 0
    
    add_class_button = ObjectProperty(None)
    doc_name_to_class = {}
    archiving = False
    
    main_box = ObjectProperty(None)
    BIO_ID = StringProperty("")
    bio_letters = {}
    
    
    
    info_list = [
        ('left', "Create a new label either for the document currently displayed with 'Add local label' or \
for the whole dataset with 'Add general label'. You will ask to choose a name and a color. Next you \
can browse among labels and select which one you want to use for tagging."),
        ('left', "Check 'Show boxes' to load pontential OCR processing and have access \
to various tagging tools. \nThe 'Tool' board enables you to respectively tag, create, move/resize, \
encapsulate, merge and remove boxes. \nThe 'BIO labelling' board enables you to \
assign a prefix to the boxes either manually with 'B' 'I' or 'O' or automatically with 'Select chunk'. You can specify and \
id to distinguish between different chunks."), 
        ('left', "Recenter the document thanks to 'Focus' and check 'Automatically refocus' in order \
to recenter the next document when switching."),
        ('right', "Create a new class with 'Add class'. You will ask to choose a name and a hotkey. \
Then use the corresponding hotkey to classify the current document in the class of your choice. \n \
Check 'Switch document once classified' to automatically switch to the next document once you have used \
a class hotkey. \n'Archive documents' is used to effectively gather documents among class folders. You \
will ask to choose if you prefer to move or duplicate documents, it will close the app and archive your project."),
        ('right', "Approve or not a document when labelling is done."),
        ('right', "Name of the document currently displayed."),
        ('right', "A floppy will appear if you type Ctrl+S indicating your work has been saved."),
        ('right', "Navigate among documents."),
        ('right', "Display metrics about labelling and/or classification within your project."),
        ('right', "Open metadata board that allows to store any data for each document."),
        ('right', "Navigate among document frames."),
        ('right', "Display this Help."),
        ('left', "Display or not tokens (loaded from OCR file), the cursor, the document, and avoid creating box outside the document.")
    ]


    
    def __init__(self, **kwargs):
        """
        Initialise the app.
        """
        super(AppManager, self).__init__(**kwargs)
        
        Window.bind(on_key_down=self.key_action)        # Jump to key_action method if someone press et key

        
        # Jump to on_checkbox_active method when one of the checkboxes is activated
        self.checkbox_showboxes.bind(active=self.on_checkbox_active)
        self.checkbox_showbackground.bind(active=self.on_checkbox_active)
        self.checkbox_showtokens.bind(active=self.on_checkbox_active)
        
        self.accordion_BIO.bind(collapse=self.on_checkbox_active)
        
        # Create popups...
        self.popAdd = AddClassPopup()           # for adding class
        self.popKey = DefineHotKeyPopup()       # for defining the key (ASCII code of a keyboard touch) of the class
        self.popDelClass = DelClassPopup()      # in case of class deletion when there are already documents classed
        self.popDelLabel = DelLabelPopup()      # in case of label deletion when there are already boxes labelled
        self.popMetadata = MetadataPopup()
        self.popProject = ProjectPopup()
        self.popCol = ColorPopup()              # choose the color and the name of the new label
        self.popArchive = ArchivePopup()
        
        
        self.canceller = Canceller(self)
        self.helpDisplayer = HelpDisplayer(self.object_list, self.info_list, [self.my_box.parent])
        self.main_box.parent.add_widget(self.helpDisplayer)
        
    def move_to(self, mode, doc_name=""):
        if mode == 'user_choice':
            for index, doc in enumerate(self.documents):
                if doc.document_name == doc_name:
                    self.switch_document(-1, index)
                    return
            WarningPopup("No document found with this name.").open()
            
        if mode == 'unclassified':
            for index, doc in enumerate(self.documents):
                if doc.document_name not in self.doc_name_to_class:
                    self.switch_document(-1, index)
                    return
                
            WarningPopup("All documents are classified.").open()
            
        if mode == 'not_approved':
            for index, doc in enumerate(self.documents):
                if doc.JSON_path:
                    try:
                        with open(doc.JSON_path) as json_file:
                            data = json.load(json_file)
                        is_approved = data['info']['approved']
                    except FileNotFoundError:
                        pass
                    except KeyError as err:
                        raise InvalidFile(doc.JSON_path, "The '{}' section is missing.".format(err.args[0]))
                    if not is_approved:
                        self.switch_document(-1, index)
                        return
                    
            WarningPopup("All document are approved.").open()

        
    def doc_starter(self, path):
        """
        Display the corresponding start image according to what functionality was selected.
        """
        self.current_filepath = path
    
    

    def show_load(self):
        """
        Open the 'Load dataset' popup.
        """
        
        content = LoadDialog(load=self.pre_load, cancel=self.dismiss_popup)                     # Create the content of the popup
        content.potential_input_dataset = Config.getdefault('previously', 'input_dataset', "\\")
        content.potential_output_directory = Config.getdefault('previously', 'output_directory', "\\")
        Config.write()
        self._popup = Popup(title="Load dataset", content=content, size_hint=(0.9, 0.9), auto_dismiss=False)    # Create the popup
        self._popup.open()                                                                  # Open the popup


    def pre_load(self, input_path, output_path):
        
        self.extract_done = Clock.create_trigger(lambda dt: self.launch())  # Prepare the event to make the main thread execute the launch_rest function
        
        threading.Thread(target=partial(self.load, input_path, output_path)).start()

    def load(self, input_path, output_path):
        """
        Specify the dataset, close the 'Load dataset' popup (in case of 'Load')
        and start the rest.
        """
        Config.set('previously', 'input_dataset', input_path)
        Config.set('previously', 'output_directory', output_path)
        Config.write()
        if input_path.split(".")[-1] == 'zip':
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                input_path = output_path + '\\_temp_input_dataset'
                self._popup.content.button_box.opacity = 0
                self._popup.content.extraction_box.opacity = 1
                zip_ref.extractall(input_path)
                self._popup.content.extraction_box.opacity = 0
            self.temporary_dataset = True
        self.dataset = os.path.join(input_path)                 # Set the input dataset path
        self.output_directory = os.path.join(output_path)       # Set the output directory path

        self.length = len(glob(join(self.dataset, '*.jpg'))+
                          glob(join(self.dataset, '*.png'))+
                          glob(join(self.dataset, '*.tif'))+
                          glob(join(self.dataset, '*.tiff')))
        self.extract_done()

        

    def dismiss_popup(self):
        """
        Close the 'Load dataset' popup (in case of 'Cancel').
        """
        self._popup.dismiss()                   # Close the popup


    def update_resizer(self):
        if self.resizer.is_active and self.cursor_tool != "Move/Resize":   # If another tool is selected and resizer has been activated
            self.resizer.disable()                          # Disable it
        elif not self.resizer.is_active and self.cursor_tool == "Move/Resize":                              # If resizer has not been activated
            self.resizer.activate()                         # Do it
        
    
    def launch(self):
        """
        Once the dataset has been selected
        """

        if self.labelling:
            try:
                with open(self.output_directory + "\\_labels.json") as json_file:
                        data = json.load(json_file)
                self.last_document_ID = data['last-document']
            except FileNotFoundError:
                pass
            except KeyError as err:
                raise InvalidFile(self.output_directory + "\\_classes.json", "The '{}' section is missing.".format(err.args[0]))
        elif self.classification:
            try:
                with open(self.output_directory + "\\_classes.json") as json_file:
                        data = json.load(json_file)
                self.last_document_ID = data['last-document']
            except FileNotFoundError:
                pass
            except KeyError as err:
                raise InvalidFile(self.output_directory + "\\_classes.json", "The '{}' section is missing.".format(err.args[0]))
                
        if self.classification:
            self.load_classes()

        self._popup.content.pb.opacity = 1
        self._popup.content.button_box.opacity = 0
        
        self.loading_done = Clock.create_trigger(lambda dt: self.launch_rest())  # Prepare the event to make the main thread execute the launch_rest function
        
        threading.Thread(target=self.loading).start()  # Call another thread to load document
                                                       # This allows to update the progress bar
        
    def loading(self):
        """
        Documents loading by another thread
        """
        # Load all permitted files
        for index, filename in enumerate(glob(join(self.dataset, '*.jpg')) + \
                          glob(join(self.dataset, '*.png')) + \
                          glob(join(self.dataset, '*.tif')) + \
                          glob(join(self.dataset, '*.tiff'))):
            curr_file = CurrentFile(filename, self.output_directory)
            if curr_file.document_name in self.doc_name_to_class:
                document_class = self.doc_name_to_class[curr_file.document_name]
                if document_class:
                    for _class in list(self.class_directory.values()):
                        if _class.name == document_class:
                            curr_file._class = _class
                            break
            self.documents.append(curr_file)
            self.nb_documents += 1
            if self.last_document_ID and curr_file.ID == self.last_document_ID:
                self.index_document = index
                self.last_document_found = True
        self.loading_done() # Trigger event to make the main thread execute the launch_rest function


    def launch_rest(self):
        """
        Once documents have been loaded by the other thread
        """
        
        self._popup.dismiss()
        self.popGoTo = GoToPopup(self.classification, self.labelling)
        
        if not self.documents:                                              # If no document
            self.sudden_stop = False
            GuiApp.get_running_app().stop()                                 # Stop the app
            return
        
            
        if self.last_document_ID and not self.last_document_found:
            self.index_document = 0
            WarningPopup("Unable to load the last document that was processed the previous time.").open()
        elif not self.last_document_ID:
            self.index_document = 0
        
        self.current_document = self.documents[self.index_document]
        
        self.current_filename = self.current_document.document_name
        self.actual_current_filepath = self.current_document.pages[0].image_path 
        
        if self.current_document.image_path.split('.')[-1] == "tif" or self.current_document.image_path.split('.')[-1] == "tiff":
            
            TIFF_path = self.current_document.image_path
            im = ImagePIL.open(TIFF_path)
            temp_TIFF_path = self.output_directory + "\\_temp_" + TIFF_path.split("\\")[-1]
            im.save(temp_TIFF_path, compression=None)

            self.current_filepath = temp_TIFF_path
        else:
            self.current_filepath = self.current_document.pages[0].image_path                                # Select the next document
            
        
        if self.current_filepath.split('.')[-1] == "tif" or self.current_filepath.split('.')[-1] == "tiff":
            self.handle_multiframe_TIFF()
        if self.labelling:   
            self.global_load()
            self.load_boxes()
            self.popCol.colpic.wheel.init_disabled_arcs(list(self.current_document.label_color.values()))
        
        self.my_zoom.initial_pos = self.my_zoom.pos
        
        if self.classification:
            its_class = self.current_document._class        # Take the document class
            if its_class:                                   # If there is effectively a class
                self.show_class(its_class.key)              # Show the magenta rectangle
                        
    def clean_data_and_options(self, bio_option):
                
        if bio_option:                              # BIO
            self.accordion_tool.collapse = False

        if self.tokens_already_loaded:              # Tokens
            self.hide_tokens()
            self.clear_tokens()
        self.tokens_already_loaded = False
        
        self.hide_boxes()                           # Boxes
        
        self.canceller.reset()                      # Undo manager
        
        self.checkbox_showbackground.active = True  # Background
        
    def reset_data_and_options(self, bio_option):
        
        
        if self.checkbox_showboxes.active:      # Boxes
            self.display_boxes()
        
        
        if self.checkbox_showtokens.active:     # Tokens
            self.load_tokens()
            self.display_tokens()
            
        if bio_option:                          # BIO
            self.accordion_BIO.collapse = False
        
    def show_class(self, key):
        class_outline = InstructionGroup(group='class_outline')
        class_outline.add(Color(1, 0, 1, 1, mode='rgba'))
        layout = self.class_directory[key].layout
        class_outline.add(Line(width=0.3, rectangle=(layout.pos[0], layout.pos[1], layout.size[0], layout.size[1]))) 
        self.class_directory[key].layout.canvas.add(class_outline)
        
    def hide_class(self, key):
        class_outline = self.class_directory[key].layout.canvas.get_group('class_outline')[0]
        self.class_directory[key].layout.canvas.remove(class_outline)
    
    def classify(self, key):
        
            # Remove the document from its current class if it is already classified
            old_class = self.current_document._class        # Take the document class
            if old_class:                                   # If there is effectively a class
                self.class_directory[old_class.key].batch.remove(self.current_document.document_name) # Remove the document from its batch
                self.hide_class(old_class.key)                                                      # And hide the magenta rectangle
            # Classify the document
            self.class_directory[key].batch.append(self.current_document.document_name) # Add the document to the class batch
            self.current_document._class = self.class_directory[key]    # Update the class of the document
            self.doc_name_to_class[self.current_document.document_name] = self.class_directory[key].name

            # Show the class thanks to a magenta rectangle
            self.show_class(key)
            
    
    def switch_document(self, key, index=None):
        """
        Class the current document and display the next
        """        
        ## Save work
        its_class = None
        if self.classification:
            self.write_json_classification()
            its_class = self.current_document._class        # Take the document class
            if its_class:                                   # If there is effectively a class
                self.hide_class(its_class.key)              # Hide the magenta rectangle
        
        if self.labelling:
            self.write_json_labelling()                 # Write modifications to the JSON file
        
            ## Clear data and disable options
            bio_option = not self.accordion_BIO.collapse
            self.clean_data_and_options(bio_option)
        
            self.popMetadata.reinitiate()               # Metadata
        
        self.reinitiate_frame()                     # Multi-frame manager
        
        # Update : if user returns on this document, it will consider the JSON file
        self.documents[self.index_document] = CurrentFile(self.current_document.image_path, self.output_directory, its_class) #c pour mettre à jour si on a créé un JSON dans la même instance de l'algo
        
        
        # Switching
        if index is not None:
            self.index_document = index
            self.current_document = self.documents[self.index_document]
        elif key == self.used_keys["next"]:                                                              # Determine if user wants to go to the previous or next document
            self.index_document = (self.index_document+1)%self.nb_documents       # Update the index corresponding to the current document
            self.current_document = self.documents[self.index_document]             # Update the current document
        elif key == self.used_keys["prev"]:
            self.index_document = (self.index_document-1)%self.nb_documents
            self.current_document = self.documents[self.index_document]
                
        self.current_filename = self.current_document.document_name                     # Get the document name
        self.actual_current_filepath = self.current_document.pages[0].image_path        # Get the first page of the document
        
        if self.current_document.image_path.split('.')[-1] == "tif" or self.current_document.image_path.split('.')[-1] == "tiff":   # If TIFF, preprocessing is applied to avoid Popup warning
            # Save the TIFF without compression option in a temporary file
            TIFF_path = self.current_document.image_path
            im = ImagePIL.open(TIFF_path)
            temp_TIFF_path = self.output_directory + "\\_temp_" + TIFF_path.split("\\")[-1]
            im.save(temp_TIFF_path, compression=None)
            self.current_filepath = temp_TIFF_path  # The current path is now actually the path of the temporary TIFF
            self.handle_multiframe_TIFF() # And process multi-frame TIFF
            
        else:    
            self.current_filepath = self.current_document.image_path    # The current path is now simply the original image page
        
        
        ## Reset options
        
        if self.checkbox_refocus.active:    # Focus
            self.my_zoom.focus()
        
        if self.classification:
            its_class = self.current_document._class        # Take the document class
            if its_class:                                   # If there is effectively a class
                self.show_class(its_class.key)              # Show the magenta rectangle
        
        if self.labelling:
        
            # Reset labels
            self.load_boxes()

            
            self.popCol.colpic.wheel.init_disabled_arcs(list(self.current_document.label_color.values()))
            
            self.reset_data_and_options(bio_option)
            

    def undo(self):
        if self.labelling and self.dataset and self.checkbox_showboxes.active:
            self.canceller.undo()
    
    def save(self):
        self.save_icone.opacity = 1
        anim = Animation(opacity=0, duration=1.5)
        anim.start(self.save_icone)
        if self.labelling: self.write_json_labelling()
        if self.classification: self.write_json_classification()
        
    
    def key_action(self, *args):
        """
        When the user use the keyboard
        """
        key_input = list(args)[1]
        combination = list(args)[4]
        if self.dataset and not self.inside_textbox:                # If dataset has been selected and not using a text box
            
            # Ctrl combination
            if 'ctrl' in combination:         
                if key_input == 122:        # Undo (ctrl + z)
                    self.undo()
                elif key_input == 115:      # Save (ctrl + s)
                    self.save()
                    
            # Choose a keyboard shortcut
            elif self.in_Popup['DefineHotKeyPopup'] and not self.in_Popup['WarningPopup']:
                # Verify the key belongs to the authorized domain and is not already used
                if key_input not in ([k for k in range(48, 58)] +                               # The domain
                        [k for k in range(97, 123)] + [k for k in range(256, 271)] +
                        [k for k in range(273, 277)] + [9, 33, 36, 41, 42, 44, 58, 59, 61, 94, 178, 249]) or \
                        (key_input in list(self.class_directory.keys()) +                       # Used for a class
                        list(self.used_keys.values())):                                         # Used for carrying out and action
                    WarningPopup("Key not allowed.").open()
                else:
                    
                    # Add a class
                    if self.popKey.mode == 'add_class':
                        self.add_class(self.popAdd.class_name, key_input)
                        
                    # Choose shortcut for carrying out an action    
                    else:
                        caller_key = int(self.popKey.caller.source.split("\\")[-1][:-4])
                        
                        # For a class
                        if caller_key in list(self.class_directory.keys()):
                            key_class = self.class_directory[caller_key]
                            del self.class_directory[caller_key]
                            key_class.key = key_input
                            self.class_directory[key_input] = key_class
                            self.popKey.caller.source = ".\\keyboard_icones\\{}.png".format(key_input)
                            
                        # For an other action
                        else:
                            task = None
                            for item in self.used_keys.items():
                                if caller_key == item[1]:
                                    task = item[0]
                                    break
                            self.used_keys[task] = key_input
                            
                    self.popKey.dismiss()
            
            # Carry out an action
            elif not True in list(self.in_Popup.values()):                                  # If no Popup is open
                
                # Open Metadata Popup
                if key_input == self.used_keys["metadata"] and self.labelling:
                    self.popMetadata.open()
                    
                # Navigate between labels
                elif key_input in [self.used_keys["next_label"], self.used_keys["prev_label"]]:
                    # Find the current label index
                    active_index = 0
                    for index, child_box in enumerate(self.label_box.children):
                        if child_box.children[1].active:
                            active_index = index
                            break
                    # Disable it and active another label
                    if (key_input == self.used_keys["next_label"]) and active_index < len(self.label_box.children)-1:
                        self.label_box.children[active_index+1].children[1].active = True
                    elif (key_input == self.used_keys["prev_label"]) and active_index > 0:
                        self.label_box.children[active_index-1].children[1].active = True
               
                # Navigate between document pages
                elif key_input in [self.used_keys["prev_frame"], self.used_keys["next_frame"]]:
                    if key_input == self.used_keys["prev_frame"] and not self.previous_frame_button_disabled:
                        self.change_frame(-1)
                    elif key_input == self.used_keys["next_frame"] and not self.next_frame_button_disabled:
                        self.change_frame(1)
                
                # Use one of the label tools
                elif key_input in [item[1] for item in list(self.used_keys.items()) if item[0] in ["tag", "create", "encapsulate", "merge", "remove", "modify"]]  and self.checkbox_showboxes.active:
                    index = [item[1] for item in list(self.used_keys.items()) if item[0] in ["tag", "create", "encapsulate", "merge", "remove", "modify"]].index(key_input)
                    self.tool_buttons[index].trigger_action(duration=0)
                    
                # Approve a document
                elif key_input == self.used_keys["approval"]:
                    self.nb_approved -= self.is_approved		# Update number of approved documents using a boolean (1)
                    self.is_approved = 1 - self.is_approved
                    self.nb_approved += self.is_approved        # Update number of approved documents using a boolean (2)
                    self.write_json_labelling()                 # Save the change
                    
                # Display project metrics
                elif key_input == self.used_keys["project-metrics"]:
                    self.popProject.open(self)
                    
                # Proceed to the next document
                elif key_input in [self.used_keys["prev"], self.used_keys["next"]]:  
                    self.switch_document(key_input)
                    
                # Class a document
                elif key_input in list(self.class_directory.keys()):
                    self.classify(key_input)
                    if self.checkbox_switch.active:
                        self.switch_document(self.used_keys["next"])
                        
                # Display Help
                elif key_input == self.used_keys["help"]:
                    self.helpDisplayer.display_help()
            
    
    def update_class_box(self, layout):
        self.class_box.remove_widget(layout)
        self.update_class_box_done()
    
    def delete_class(self, remove_button):
        key = int(remove_button.key)
        class_to_delete = self.class_directory[key]
        if class_to_delete.batch:
            self.popDelClass.remove_button = remove_button
            self.popDelClass.open()
        else:
            self.class_box.remove_widget(remove_button.parent)
            del self.class_directory[key]
            its_class = self.current_document._class
            if its_class:
                self.hide_class(its_class.key)
                Clock.schedule_once(lambda dt: self.show_class(its_class.key))


            
    def unlist_files(self, remove_button):
        key = int(remove_button.key)
        class_to_delete = self.class_directory[key]

        for doc in self.documents:
            if doc._class and doc._class.name == class_to_delete.name:
                doc._class = None
                del self.doc_name_to_class[doc.document_name]
        class_to_delete.batch = []
        self.delete_class(remove_button)

        
    def add_class(self, new_class, key, batch=[]):
        """
        Effectively add the new class
        """

        self.class_directory[key] = Class(new_class, key, batch.copy())  

        # Create a new icon in the window
        layout = BoxLayout(orientation='horizontal', padding=5, spacing=5)                        # Create a BoxLayout for the new class
        
                                     # Store the new class
        label = Label(text=new_class, font_size = '20sp')                   # Create a label with the class name
        
        image = ImageButton(source=".\\keyboard_icones\\{}.png".format(key), on_press=self.popKey.open)                            # Create an Image with the key icon
        
        layout.add_widget(label)                                            # Add the label to the BoxLayout
        layout.add_widget(image)                                            # And the image
        
        remove_button = ImageButton(source='keyboard_icones\dustbin.png', on_press=self.delete_class, size_hint_x=0.1)
        remove_button.key = str(key)
        layout.add_widget(remove_button)
        
        self.class_directory[key].layout = layout
        
        self.class_box.add_widget(self.class_directory[key].layout)      
                             # Finally add the BoxLayout of the class into the parent BoxLayout for classels
        
        if self.current_document:
            its_class = self.current_document._class
            if its_class:
                self.hide_class(its_class.key)
                Clock.schedule_once(lambda dt: self.show_class(its_class.key))
        
  
    

    def handle_multiframe_TIFF(self):
        """
        Initialise what is necessary in case of multiframe TIFF
        """
        image = ImagePIL.open(self.actual_current_filepath)                # Open the image
        try:                                                        # Try if it is a multiframe TIFF
            image.seek(1)
        except EOFError:                                            # If not: do nothing
            return                                                  
        else:                                                       # Else: create a frames list
            error_flag = False                                      
            frame_number = 0
            while not error_flag:
                try:
                    image.seek(frame_number)
                except EOFError:
                    error_flag = True
                else:
                    
                    frame = image.copy()
                    frame_path = self.output_directory + "\\_temp_{}_".format(frame_number) + self.actual_current_filepath.split("\\")[-1]
                    frame.save(frame_path)
                    if frame_number:
                        self.current_document.pages.append(Page(frame_path))
                    else:
                        self.current_document.pages[0] = Page(frame_path)
                    frame_number += 1
            self.page_num.text = "page 1/{}".format(frame_number)
            self.next_frame_button_disabled = False
            


    def change_frame(self, direction):
        """
        Switch to the previous or next frame of the multi-frame TIFF 
        according to direction.
        """
        
        
        ## Clear data and disable options
        bio_option = not self.accordion_BIO.collapse
        self.clean_data_and_options(bio_option)
        
        
        ## Change document page
        
        self.current_document.index_current_page += direction   # Update the page index
        if self.current_document.index_current_page == (len(self.current_document.pages)-1)*(1+direction)/2:    # If no more previous (or next) page
            if direction == 1:                              # Disable the corresponding short_key
                self.next_frame_button_disabled = True
            else:
                self.previous_frame_button_disabled = True

        self.current_filepath = self.current_document.pages[self.current_document.index_current_page].image_path # Update the path
        self.page_num.text = "page {}/{}".format(self.current_document.index_current_page+1, len(self.current_document.pages)) # Update the page number
        if direction == 1:                                  # Allow to come back (or go forward)
                self.previous_frame_button_disabled = False
        else:
            self.next_frame_button_disabled = False           
        
        ## Reset options
        
        self.reset_data_and_options(bio_option)
    
    def reinitiate_frame(self):
        """
        Destroy what was built to handle the multiframe TIFF
        """
        if len(self.current_document.pages) > 1:
            for page in self.current_document.pages:
                os.remove(page.image_path)                                # Remove temp files
        if self.current_filepath.split('.')[-1] == "tif" or self.current_filepath.split('.')[-1] == "tiff":
            temp_TIFF_path = self.output_directory + "\\_temp_" + self.actual_current_filepath.split("\\")[-1]
            os.remove(temp_TIFF_path)
        self.next_frame_button_disabled = True
        self.previous_frame_button_disabled = True
        self.page_num.text = "page 1/1"
        
    def hide_boxes(self):
        """
        Disable boxes display
        """        
        dico = self.current_document.pages[self.current_document.index_current_page].button_boxes
        for button in dico:
            self.my_zoom.remove_widget(button)

    
    def display_boxes(self):
        """
        Display boxes
        """
        dico = self.current_document.pages[self.current_document.index_current_page].button_boxes
        for button in dico:
            self.my_zoom.add_widget(button)
                    
    
    def load_classes(self):
        """
        Load the classes internally
        """
        try:
            with open(self.output_directory + "\\_classes.json") as json_file:
                    data = json.load(json_file)
            for _class in data['documents_by_classes']:
                self.add_class(_class['name'], _class['key'], _class['batch'])
            for document_name in data['classes_by_documents']:
                self.doc_name_to_class[document_name] = data['classes_by_documents'][document_name]
        except Exception:
            print("first time : no _classes.json file yet")
    
    def remove(self, button, multiple=False):
        dico = self.current_document.pages[self.current_document.index_current_page].button_boxes
        if not multiple and not self.during_undo:
            self.canceller.update([], {button: dico[button]}, [], [], [])
        if self.tokens_already_loaded:
            del self.tokens_to_buttons[self.buttons_to_tokens[button]]
            self.my_box.remove_widget(self.buttons_to_tokens[button])
        self.my_zoom.remove_widget(button)
        self.current_document.label_occurrence[dico[button].label] -= 1
        del dico[button]
    
    
    def appear(self, button):
            """
            Make the button appear (used to see it when clicking on)
            """
            if not self.cursor_tool == "Move/Resize":
                button.background_color = (1, 1, 1, 0.5)
                self.current_pressed_button = button
            
    def tag(self, button, label_name=None, during_box_creation=False, multiple=False, bio_letter=None, during_untag=False):
        """
        Tag the box : update the corresponding Box object and change color box on the document
        """
        dico = self.current_document.pages[self.current_document.index_current_page].button_boxes
        if not self.accordion_BIO.collapse:
            if not multiple and not self.during_undo and not during_box_creation:
                self.canceller.update([], {}, [button], [], [dico[button].BIO_prefix])
            dico[button].BIO_prefix = self.bio_tool+self.BIO_ID if not bio_letter else bio_letter
            for (bio_letter, _button) in self.bio_letters.items():
                if _button == button:
                    bio_letter.text = dico[button].BIO_prefix
            
        elif during_untag or self.cursor_tool == "Tag" or (self.cursor_tool in ["Create", "Encapsulate", "Merge"] and during_box_creation) or self.during_undo:
            button.background_color = (1, 1, 1, 0)
            for checkbox in self.checkbox_list:
                if checkbox.active:
                    # Specify the right label
                    if not label_name:                      # Use the currently selected label
                        label_name = checkbox.text
                    if label_name == dico[button].label:    # Labelling twice is replacing by 'None'
                        label_name = "None"
                        
                    if not multiple and not self.during_undo and not during_box_creation:
                        self.canceller.update([], {}, [button], [dico[button].label], [])
                    
                    self.current_document.label_occurrence[dico[button].label] -= 1     # Remove the previous tag
                    dico[button].label = label_name                                     # Update the new tag
                    self.current_document.label_occurrence[label_name] += 1             # Add the new tag
                    
                    col = self.current_document.label_color[label_name]
                    button.canvas.get_group('outline')[0].children[0].rgba = col + [1]  # Update box outline
                    button.canvas.get_group('filling')[0].children[0].rgba = col + [0.3 if label_name != "None" else 0]  # Update box filling
                    
                    break
                
        elif self.cursor_tool == "Remove":
            self.remove(button)
        else:
            return
        
    
    def global_load(self):
        try:
            with open(self.output_directory + "\\_labels.json") as json_file:
                    data = json.load(json_file)
            for label in data['labels']:
                self.add_label([val/255 for val in label['color']], label['name'], "general")         
            for metainfo in data['metadata']:
                self.popMetadata.general_metadata.add(metainfo)
            self.nb_approved = data['nb-approved']
        except FileNotFoundError:
            print("first time : no _labels.json file yet")
            self.add_label([0, 0.5, 1], "None", "general")
        except KeyError as err:
            raise InvalidFile(self.output_directory + "\\_labels.json", "The '{}' section is missing.".format(err.args[0]))
                
    
    def load_boxes(self):
        """
        Load the boxes internally
        """
        
        previous_label_name = [checkbox.text for checkbox in self.checkbox_list if checkbox.active][0]
        self.label_box.clear_widgets()
        self.checkbox_list = []
        self.current_document.label_color = {}
        # Clear the color wheel according to the labels used in the new current document
        self.popCol.colpic.wheel.init_wheel(None)
        
        
        
        for label, color in self.global_label_color.items():
            self.add_label(color, label, "general")
#                
                
        def loading(coordinates, confidence, token, index_page, label, BIO_prefix="O"):
            """
            Effectively load boxes internally
            """
            
            dico = self.current_document.pages[index_page].button_boxes
            
            x_origin = self.my_box.width/2-self.my_image.norm_image_size[0]/2
            y_origin = self.my_box.height/2-self.my_image.norm_image_size[1]/2
            self.ratio = self.my_image.norm_image_size[0]/self.my_image.texture_size[0]
            button = ResizableButton(on_press=self.appear, on_release=self.tag,
                                 border=(0, 0, 0 ,0), 
                                 background_color=(1, 1, 1, 0),                          
                                 pos=(x_origin+self.ratio*(coordinates[0]), y_origin+self.ratio*(self.current_document.pages[index_page].pg_size_Y-coordinates[3])), 
                                 size_hint=(None, None), 
                                 size=(self.ratio*(coordinates[2]-coordinates[0]), self.ratio*(coordinates[3]-coordinates[1])))
            
            
            dico[button] = Box(coordinates, confidence, token, label, BIO_prefix)
            
            self.current_document.label_occurrence[label] += 1
            
            col = self.current_document.label_color[label]
            
            outline = InstructionGroup(group='outline')

            outline.add(Color(rgba=col + [1], mode='rgba'))
            outline.add(Line(width=0.3,rectangle=(button.pos[0], button.pos[1], button.size[0], button.size[1])))
            button.canvas.add(outline)

            filling = InstructionGroup(group='filling')        
            filling.add(Color(rgba=col + [0.3 if label != "None" else 0], mode='rgba'))
            filling.add(Rectangle(pos=button.pos, size=button.size))
            button.canvas.add(filling)
            
            
            
        if self.current_document.JSON_path:
            # Load from JSON file
            with open(self.current_document.JSON_path) as json_file:
                data = json.load(json_file)
                
                try:
                
                    self.current_document.filesize = data['info']['filesize']
                    self.current_document.engine = data['info']['engine']
                    self.current_document.recognition_info = data['info']['recognition-info']
                    self.current_document.page_conf_level = data['info']['page-conf-level']
                    self.current_document.pdf = data['info']['pdf']
                    self.current_document.nbPages = data['info']['nbPages']
                    self.current_document.res_X = data['info']['res-X']
                    self.current_document.res_Y = data['info']['res-Y']
                    self.current_document.pg_size_X = data['info']['pg-size-X']
                    self.current_document.pg_size_Y = data['info']['pg-size-Y']
                    self.current_document.BIO_labelling = data['info']['BIO_labelling']
                    self.is_approved = data['info']['approved']

                    for label in data['labels']:
                        if label['name'] != 'None':
                            color = [val/255 for val in label['color']]
                            if label['name'] not in self.global_label_color:
                                self.add_label(color, label['name'], "local")
                    
                    for metaname in data['metadata']:
                        metavalue = data['metadata'][metaname]
                        self.popMetadata.load_info(metaname, metavalue)
                    for metaname in self.popMetadata.general_metadata:
                        if metaname not in data['metadata']:
                            self.popMetadata.load_info(metaname, "")
                    
                    if len(data['info']['pages']) < len(self.current_document.pages):
                        raise IncompatibleFiles(self.current_document.image_path, 
                                                self.current_document.OCR_path, 
                                                "Image contains more pages than JSON description.")
                    elif len(data['info']['pages']) > len(self.current_document.pages):
                        WarningPopup("OCR description contains more pages than image.").open()
                    for index_page, page in enumerate(data['info']['pages']):
                        if index_page < len(self.current_document.pages):
                            self.current_document.pages[index_page].fill_info(page['res-X'], page['res-Y'], page['pg-size-X'], page['pg-size-Y'])
                    
                    for index_page, page in enumerate(data['boxes-by-page']):
                        if index_page < len(self.current_document.pages):
                            for box in page['boxes']:
                                coordinates = [box['left'], box['top'], box['right'], box['bottom']]
                                confidence = box['confidence']
                                token = box['token']
                                label = box['label']
                                if self.current_document.BIO_labelling:
                                    BIO_prefix = box['BIO-prefix']
                                    loading(coordinates, confidence, token, index_page, label, BIO_prefix)
                                else:
                                    loading(coordinates, confidence, token, index_page, label)
                            
                except KeyError as err:
                    raise InvalidFile(self.current_document.JSON_path, "The '{}' section is missing.".format(err.args[0]))
                
                json_file.close()
                        

        else:
            # No file to load boxes
            # Search for pg_size_X and pg_size_Y attributs
            self.is_approved = False
            try:
                for metainfo in self.popMetadata.general_metadata:
                    self.popMetadata.load_info(metainfo, "")
                im = ImagePIL.open(self.current_document.image_path)
                if self.current_filepath.split('.')[-1]== "tif" or self.current_filepath.split('.')[-1]== "tiff":
                
                    for index, page in enumerate(self.current_document.pages):
                        im.seek(index)
                        frame = im.copy()
                        self.current_document.pages[index].pg_size_X = frame.size[0]
                        self.current_document.pages[index].pg_size_Y = frame.size[1]
                        
                else:
                    self.current_document.pages[0].pg_size_X = im.size[0] 
                    self.current_document.pages[0].pg_size_Y = im.size[1]
            except Exception:
                raise InvalidFile(self.current_document.image_path, "Cannot read image size.")

        for checkbox in self.checkbox_list:
            if checkbox.text == previous_label_name: 
                checkbox.active = True
                break

        return
                    
    def clear_tokens(self):
        self.tokens_to_buttons = {}
        self.buttons_to_tokens = {}
    
    
    def load_tokens(self):
        dico = self.current_document.pages[self.current_document.index_current_page].button_boxes
        self.clear_tokens()
        for button in dico:
            new_pos = self.my_zoom.transform_to_parent((button.pos[0], button.pos[1]+button.size[1]))
            token = Token(new_pos, dico[button].token)
            self.tokens_to_buttons[token] = button
            self.buttons_to_tokens[button] = token
        self.tokens_already_loaded = True
        
    def new_button(self, new_button_LB, new_button_RT, label="None"):
        """
        Return a new button (and its outline) created from its bottom left and top right points.
        """
        button = ResizableButton(on_press=self.appear, on_release=self.tag, 
                             border=(0, 0, 0 ,0), 
                             background_color=(1, 1, 1, 0), 
                             pos=(new_button_LB),
                             size_hint=(None, None), 
                             size=(new_button_RT[0]-new_button_LB[0], new_button_RT[1]-new_button_LB[1]))       
        
        
        col = self.current_document.label_color[label]
        
        self.current_document.label_occurrence[label] += 1
        
        outline = InstructionGroup(group='outline')
        outline.add(Color(rgba=col + [1], mode='rgba'))
        outline.add(Line(width=0.3,rectangle=(button.pos[0], button.pos[1], button.size[0], button.size[1]))) 
        button.canvas.add(outline)
        
        filling = InstructionGroup(group='filling')        
        filling.add(Color(rgba=col + [0.3 if label != "None" else 0], mode='rgba'))
        filling.add(Rectangle(pos=button.pos, size=button.size))
        button.canvas.add(filling)       

        
        return button
        
    def button_coord_to_box_coord(self, button):
        """
        Return button coordinates in box format.
        """
        x_origin = self.my_box.width/2-self.my_image.norm_image_size[0]/2
        y_origin = self.my_box.height/2-self.my_image.norm_image_size[1]/2
        self.ratio = self.my_image.norm_image_size[0]/self.my_image.texture_size[0]   
        
                
        left = (1/self.ratio)*(button.pos[0] - x_origin)
        bottom = -((1/self.ratio)*(button.pos[1] - y_origin) - self.current_document.pages[self.current_document.index_current_page].pg_size_Y)
        right = (1/self.ratio)*button.size[0]+left
        top = -((1/self.ratio)*button.size[1]-bottom)
        return [left, top, right, bottom]
    
    def box_coord_to_button_coord(self, box):
        x_origin = self.my_box.width/2-self.my_image.norm_image_size[0]/2
        y_origin = self.my_box.height/2-self.my_image.norm_image_size[1]/2
        self.ratio = self.my_image.norm_image_size[0]/self.my_image.texture_size[0]
        pos = (x_origin+self.ratio*box.left, y_origin+self.ratio*(self.current_document.pages[self.current_document.index_current_page].pg_size_Y-box.bottom))
        size =  (self.ratio*(box.right-box.left), self.ratio*(box.bottom-box.top))
        return pos, size
    
    def display_tokens(self):
        for token in self.tokens_to_buttons:
            self.my_box.add_widget(token)
        self.my_zoom.update_tokens()

    
    def hide_tokens(self):
        for token in self.tokens_to_buttons:
            self.my_box.remove_widget(token)
        
    def on_checkbox_active(self, instance, value):
        """
        Control boxes display on the document
        """
        if instance.text == "Show tokens":
            if value:
                if not self.tokens_already_loaded:
                    self.load_tokens()
                self.display_tokens()
            else:
                self.hide_tokens()
        elif instance.text == "Show boxes":
            if value:
                self.display_boxes()
            else:
                self.hide_boxes()
        elif instance.text == "Show background":
            if value:
                self.my_zoom.canvas.before.remove(self.my_zoom.canvas.before.get_group('background')[0])
                self.current_filepath = self.old_current_filepath
            else:
                background = InstructionGroup(group='background')
                background.add(Color(1, 1, 1, 1))
                page_frame = self.current_document.pages[self.current_document.index_current_page]
                back_pos, back_size = self.box_coord_to_button_coord(Box([0, page_frame.pg_size_Y, page_frame.pg_size_X, 0], 50, "50"))
                background.add(Rectangle(pos=back_pos, size=back_size))
                self.my_zoom.canvas.before.add(background)
                self.old_current_filepath = self.current_filepath
                self.current_filepath = "keyboard_icones\\transparent.png"
        elif instance.text == "Show BIO":          
            dico = self.current_document.pages[self.current_document.index_current_page].button_boxes
            if not self.during_undo:
                self.canceller.switch_BIO_checkbox()
            if not value:
                self.current_document.BIO_labelling = True
                for button in dico:
                    bio_letter=BIO_Label(pos=button.pos, size=button.size, text=dico[button].BIO_prefix)
                    self.bio_letters[bio_letter] = button
                    self.my_box.add_widget(bio_letter)
                self.my_zoom.update_BIO()
                self.tool_buttons[0].trigger_action(duration=0)
            else:
                for bio_letter in self.bio_letters:
                    self.my_box.remove_widget(bio_letter)
        

    def delete_label(self, remove_button):        
        label_name = remove_button.key
        if self.current_document.label_occurrence[label_name]:
            self.popDelLabel.remove_button = remove_button
            self.popDelLabel.open()
        else:
            self.label_box.remove_widget(remove_button.parent)
            del self.current_document.label_color[label_name]
            if label_name in self.global_label_color:
                del self.global_label_color[label_name]
            self.popCol.colpic.wheel.init_wheel(None)
            self.popCol.colpic.wheel.init_disabled_arcs(list(self.current_document.label_color.values()))
            for index, checkbox in enumerate(self.checkbox_list):
                if checkbox.text == label_name:
                    if checkbox.active:
                        self.checkbox_list[index-1].active = True   # 'None' label non-deletable at index 0 so index-1 is valid
                    self.checkbox_list.remove(checkbox)
        
        
    def untag(self, remove_button):
        label_name = remove_button.key
        for page in self.current_document.pages:
            dico = page.button_boxes
            for button in list(dico.keys()):
                if dico[button].label == label_name:
                    self.tag(button, "None", during_untag=True)
        self.delete_label(remove_button)


    def add_label(self, color, label_name, mode):
        """
        Add a new label to the tool
        """
        new_label = Label(text=label_name, color=(color.copy() if label_name != "None" else [1, 1, 1]) + [1])                            # Create a Label object
        new_checkbox = CheckBox(text=label_name, group="lab", active=True, allow_no_selection=False)                      # And the corresponding CheckBox object
        self.checkbox_list.append(new_checkbox)                                                 # Append this CheckBox to the list of checkboxes
        self.current_document.label_color[label_name] = color.copy()                            # Append the color to the corresponding label
        if mode == "general":
            self.global_label_color[label_name] = color.copy()                                      # Same in general label dictionnary
        
        remove_button = ImageButton(source='keyboard_icones\dustbin.png', on_press=self.delete_label, disabled=(label_name=="None"), opacity=0 if label_name=="None" else 1)
        remove_button.key = str(label_name)
        if label_name == "None":
            remove_button.disabled = True
            remove_button.opacit = 0
        
        new_boxLayout = BoxLayout()                                             # Create a new BoxLayout
        new_boxLayout.add_widget(new_label)                                     # Add the Label
        new_boxLayout.add_widget(self.checkbox_list[-1])                        # And the CheckBox
        new_boxLayout.add_widget(remove_button)
        self.label_box.add_widget(new_boxLayout)                                # Finallly Add the BoxLayout to the label_box BoxLayout
        
        self.current_document.label_occurrence[label_name] = 0
    
    
    def write_json_labelling(self):
        """
        Create the corresponding labelling JSON file of the current document
        """
        data = {}
        pages = []
        for numero, page in enumerate(self.current_document.pages):
            pages.append({
                'numero' : numero+1,
                'res-X': page.res_X,
                'res-Y': page.res_Y,
                'pg-size-X': page.pg_size_X,
                'pg-size-Y': page.pg_size_Y
                    })
        data['info'] = {
                'filesize': self.current_document.filesize,
                'engine': self.current_document.engine,
                'recognition-info': self.current_document.recognition_info,
                'page-conf-level': self.current_document.page_conf_level,
                'pdf': self.current_document.pdf,
                'nbPages': len(self.current_document.pages),
                'res-X': self.current_document.res_X,
                'res-Y': self.current_document.res_Y,
                'pg-size-X': self.current_document.pg_size_X,
                'pg-size-Y': self.current_document.pg_size_Y,
                'BIO_labelling': self.current_document.BIO_labelling,
                'approved': bool(self.is_approved),
                'class': self.current_document._class.name if self.current_document._class else None,
                'pages': pages
                }  
        data['labels'] = []
        for label_name in self.current_document.label_color:
            data['labels'].append({
                'name': label_name,
                'color': [int(255*val) for val in self.current_document.label_color[label_name]],
                'occurrence': self.current_document.label_occurrence[label_name]
                })
        data['metadata'] = sort_dictionnary(self.popMetadata.current_metadata)
        data['boxes-by-page'] = []
        for numero, page in enumerate(self.current_document.pages):
            box_list = []
            for box in list(page.button_boxes.values()):
                box_dic = {
                        'left': box.left,
                        'top': box.top,
                        'right': box.right,
                        'bottom': box.bottom,
                        'confidence': box.confidence,
                        'token': box.token,
                        'label': box.label
                        }
                if self.current_document.BIO_labelling:
                    box_dic['BIO-prefix'] = box.BIO_prefix
                box_list.append(box_dic)
            data['boxes-by-page'].append({
                    'page-number': numero+1,
                    'boxes': box_list
                    })
            
        with open(self.output_directory + "\\" + self.current_document.ID + ".json" , 'w') as outfile:
            json.dump(data, outfile)    
            outfile.close()
        data = {}
        data['labels'] = []
        for label_name in self.global_label_color:
            data['labels'].append({
                'name': label_name,
                'color': [int(255*val) for val in self.global_label_color[label_name]]
                })
        data['metadata'] = sorted([metainfo for metainfo in self.popMetadata.general_metadata])
        data['last-document'] = self.current_document.ID
        data['nb-approved'] = self.nb_approved
        with open(self.output_directory + "\\_labels.json" , 'w') as outfile:
            json.dump(data, outfile)
            outfile.close()
    
    def check_deletion_rights(self):
        for _class in list(self.class_directory.values()):
            for file_path in _class.batch:
                for file in glob(file_path + ".*"):
                    try:
                        f = open(file, "r")
                    except PermissionError:
                        return False
                    else:
                        f.close()
        return True
    
    def archive(self, mode):
        # Create an archive directory
        self.write_json_classification()
        try:
            os.mkdir(self.output_directory + "\\_archive")
        except OSError:  
            print("Creation of the archive directory failed")
        else:  
            print("Successfully created the archive directory")
            
        # For each class create a class directory
        for _class in list(self.class_directory.values()):
            try:
                os.mkdir(self.output_directory + "\\_archive\\" + _class.name)
            except OSError:  
                print("Creation of the directory ", _class.name, " failed")
            else:  
                print("Successfully created the directory", _class.name) 
                
            for file_path in _class.batch:
                for file in glob(file_path + ".*"):         # Take all documents with the same name
                    if mode == 'move':
                        try:
                            os.rename(file, self.output_directory + "\\_archive\\{}{}".format(_class.name, file[len(self.dataset):]))    # Move the document(s)
                        except OSError:  
                            print("File moving failed")
                        else:  
                            print("Successfully move file")
                    elif mode == 'duplicate':                
                        try:
                            shutil.copyfile(file, self.output_directory + "\\_archive\\{}{}".format(_class.name, file[len(self.dataset):]))    # Duplicate the document(s)
                        except OSError:  
                            print("File duplicating failed")
                        else:  
                            print("Successfully duplicate file") 
            for file_path in _class.batch:
                for file in glob(self.output_directory + "\\" + file_path.split("\\")[-1] + ".*"):         # Take all documents with the same name
                    if mode == 'move':
                        try:
                            os.rename(file, self.output_directory + "\\_archive\\{}{}".format(_class.name, file[len(self.output_directory):]))    # Move the document(s)
                        except OSError:  
                            print("File moving failed")
                        else:  
                            print("Successfully move file")
                    elif mode == 'duplicate':                
                        try:
                            shutil.copyfile(file, self.output_directory + "\\_archive\\{}{}".format(_class.name, file[len(self.output_directory):]))    # Duplicate the document(s)
                        except OSError:  
                            print("File duplicating failed")
                        else:  
                            print("Successfully duplicate file") 
                            
                            
                            
                            
                            
                             
        for json_file in glob(self.output_directory + "\\*.json"):
            try:
                os.rename(json_file, self.output_directory + "\\_archive\\" + json_file.split("\\")[-1])    # Move the document(s)
            except OSError:  
                print("JSON file moving failed")
            else:  
                print("Successfully move JSON file")
        self.archiving = True
        
                            
    def write_json_classification(self, mode=None):
        """
        Create the corrresponding classification JSON file of the dataset
        """
        data = {}
        data['documents_by_classes'] = []
        for key in self.class_directory:


            data['documents_by_classes'].append({
                    'name': self.class_directory[key].name,
                    'key': key,
                    'size': len(self.class_directory[key].batch),
                    'batch': self.class_directory[key].batch
                    })
        data['classes_by_documents'] = self.doc_name_to_class
        data['last-document'] = self.current_document.ID
        with open(self.output_directory + "\\_classes.json" , 'w') as outfile:
            json.dump(data, outfile)



class GuiApp(App):
    """
    The app
    """
    manager = None  # BoxLayout representing the main part of the app
    already_stopped = False
    
    def build(self):
        """
        What the app will do when it runs
        """
        Window.bind(on_request_close=self.ask_leave)
        
        self.manager = AppManager()         # Create the manager
        return self.manager                 # Call the manager
    
    
    
    
    def ask_leave(self, *largs, **kwargs):
        QuitPopup().open()
        return True
        
    def on_stop(self):
        """
        What the app will do when it stops
        """
        if self.manager.dataset and not self.already_stopped:
            Config.set('previously', 'shortcuts', self.manager.used_keys)
            Config.write()
            if self.manager.classification and not self.manager.archiving:
                self.manager.write_json_classification()
            if self.manager.sudden_stop and self.manager.current_document:
                self.manager.reinitiate_frame()                 # Allow to destroy temp files
            if self.manager.temporary_dataset:
                shutil.rmtree(self.manager.dataset)
            self.already_stopped = True

class ErrorApp(App):
    
    def __init__(self, err, **kwargs):
        super(ErrorApp, self).__init__(**kwargs)
        self.err = err
    
    def build(self):
        """
        What the app will do when it runs
        """
        ErrorPopup(type(self.err).__name__ + ": " + self.err.__str__()).open()
        return 


try:
    GuiApp().run()              # Run the app
except Exception as err:
    traceback.print_exc()
    ErrorApp(err).run()
    
