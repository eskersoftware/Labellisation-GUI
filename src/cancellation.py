# -*- coding: utf-8 -*-

from graphical_elements import Token
from util import *


class Stratum:
        """
        Contain description of one passed action
        """
        def __init__(self, to_delete, to_create, to_tag, labels, bio_letters, switch_accordion_BIO=False, button=None, old_pos=None, old_size=None):
            self.to_delete = to_delete
            self.to_create = to_create
            self.to_tag = to_tag
            self.labels = labels
            self.bio_letters = bio_letters
            self.switch_accordion_BIO = switch_accordion_BIO
            self.button = button
            self.old_pos = old_pos
            self.old_size = old_size
            
            
        def __str__(self):
            return "to_delete = " + str(self.to_delete) + \
                    "\nto_create = " + str(self.to_create) + \
                    "\nto_tag = " + str(self.to_tag) + \
                    "\nlabels = " + str(self.labels) + \
                    "\nbio_letters = " + str(self.bio_letters) + \
                    "\nswitch_accordion_BIO = " + str(self.switch_accordion_BIO) + \
                    "\nbutton = " + str(self.button) + \
                    "\nold_pos = " + str(self.old_pos) + \
                    "\nold_size = " + str(self.old_size)


class Canceller:
    """
    Contain 3 strata that enable to reverse actions three times
    """
    
    strata = []   
    
    def __init__(self, manager):
        self.manager = manager
    
    def modified_box(self, _button, _old_pos, _old_size):
        self.strata.append(Stratum([], [], [], [], [], button=_button, old_pos=_old_pos, old_size=_old_size))
    
    def update(self, to_delete, to_create, to_tag, labels, bio_letters):
        self.strata.append(Stratum(to_delete, to_create, to_tag, labels, bio_letters))
        
    def switch_BIO_checkbox(self):
        self.strata.append(Stratum([], [], [], [], [], switch_accordion_BIO=True))
    
    def undo(self):
        self.manager.during_undo = True
        
        if self.strata:
            
            stratum = self.strata.pop()
            
            if stratum.switch_accordion_BIO:
                if self.manager.accordion_BIO.collapse:
                    self.manager.accordion_BIO.collapse = False
                else:
                    self.manager.accordion_tool.collapse = False
            elif stratum.button:
                stratum.button.pos = stratum.old_pos
                stratum.button.size = stratum.old_size
                self.manager.resizer.current_button = stratum.button
                self.manager.resizer.update_current_button()
                
            else:
                # delete
                for button in stratum.to_delete:
                    self.manager.remove(button)
                # create
                dico = self.manager.current_document.pages[self.manager.current_document.index_current_page].button_boxes
                for button in stratum.to_create:
                    
    
                    box = stratum.to_create[button]
                    label = box.label
                    box.label = "None" # like a new button
                    dico[button] = box
                    
                    # Draw it on the app
                    self.manager.my_zoom.add_widget(button)
                    self.manager.tag(button, label_name=label, during_box_creation=True)   # Create and tag the new box at the same time
    
                    # Draw the smaller buttons over the new button (this allows user to click on them)                    
                    for other_button in list(dico.keys()):
                        button_LB = other_button.pos
                        button_RT = (other_button.pos[0]+other_button.size[0], other_button.pos[1]+other_button.size[1])
                        if is_inside([button.pos, (button.pos[0]+button.size[0], button.pos[1]+button.size[1])], [button_LB, button_RT]):
                            box = dico[other_button]
                            del dico[other_button]
                            dico[other_button] = box
                            self.manager.my_zoom.remove_widget(other_button)
                            self.manager.my_zoom.add_widget(other_button)
                    
                    # Load the new token if other tokens have already been loaded
                    if self.manager.tokens_already_loaded:
                        new_pos = self.manager.my_zoom.transform_to_parent((button.pos[0], button.pos[1]+button.size[1]))
                        token = Token(new_pos, dico[button].token)
                        self.manager.tokens_to_buttons[token] = button
                        self.manager.buttons_to_tokens[button] = token
                    
                    # Show the token is the 'Show tokens' checkbox is activated
                    if self.manager.checkbox_showtokens.active:
                        self.manager.my_box.add_widget(token)
                                    
                # tag
                for button, label in zip(stratum.to_tag, stratum.labels):
                    self.manager.tag(button, label_name=label)
                for button, _bio_letter in zip(stratum.to_tag, stratum.bio_letters):
                    self.manager.tag(button, bio_letter=_bio_letter)
            
        self.manager.during_undo = False
    
    def reset(self):
        self.strata = []
    
    def __str__(self):
        buffer = ""
        for stratum, index in enumerate(self.strata[::-1]):
            buffer += "\n\n = = = stratum" + str(index) + " = = =\n" + str(stratum)
        return buffer
