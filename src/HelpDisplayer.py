from kivy.animation import Animation
from kivy.uix.label import Label
from functools import partial
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout


# -*- coding: utf-8 -*-


class HelpDisplayer(FloatLayout):
    """
    Display some information signs about app functionalities.
    """
    
    def __init__(self, object_list, info_list, hide_list, **kwargs):
        super(HelpDisplayer, self).__init__(**kwargs)
        self.object_list = object_list                      # Objects to explain
        self.info_list = info_list                          # Info to display
        self.hide_list = hide_list                          # Objects to hide
        self.displayed = False                              # Either or not the help is displayed
        self.temp = []                                      # Used to modify canvases of each info sign
        self.anim_hide = Animation(opacity=0, duration=0.5) # Animation to apply: disappearance
        self.anim_disp = Animation(opacity=1, duration=0.5) # Animation to apply: appearance
        self.opacity = 0                                    # Help is not displayed at the beggining
        self.already_loaded = False                         # Help has been loaded
        self.frame_width = 1.2                              # Outline of info signs
        
    def load_help(self):
        """
        Load what is necesary to create the help.
        """
        for index, (object_box, info) in enumerate(zip(self.object_list, self.info_list)):  # For each object to explain
            
            if object_box.opacity: # If object is actually present
            
                # Surround it
                self.canvas.add(Color(1, 0, 0, 1))
                self.canvas.add(Line(width=self.frame_width, rectangle=(object_box.x, object_box.y, object_box.width, object_box.height)))
                
                # Create the corresponding sign
                label = Label(size_hint=(None, None), text=info[1], font_size='18sp', halign='justify', valign='middle')
                label.bind(texture_size=partial(self._update_labe_size, index), size=partial(self._update_label_pos, index), pos=partial(self._update_label_canvas, index))
                self.add_widget(label)
                
                connexion = Line(width=self.frame_width)
                outline = Line(width=self.frame_width)
                
                self.temp.append((connexion, outline, object_box)) # Save canvases
                
                self.canvas.add(Color(1, 0, 0, 1))
                self.canvas.add(self.temp[index][0])
                self.canvas.add(Color(1, 0, 0, 1))
                self.canvas.add(self.temp[index][1])
            
            else:
                self.temp.append(None)
            
        self.already_loaded = True
        
    def display_help(self):
        """
        Display or hide the help.
        """
        
        if not self.already_loaded:
            self.load_help()
            
        # Display
        if not self.displayed:
            for object_to_hide in self.hide_list:
                self.anim_hide.start(object_to_hide)    # Progressively hide objects to hide
            self.anim_disp.start(self)                  # Progressively display the help
            self.displayed = True
        # Hide
        else:
            for object_to_hide in self.hide_list:
                self.anim_disp.start(object_to_hide)
            self.anim_hide.start(self)
            self.displayed = False
    
    def _update_labe_size(self, index, instance, value):
        """
        Update sign size and potentially texture size.
        """
        connexion, outline, object_box = self.temp[index]
        if instance.texture_size[0] < Window.width/3.5:
            instance.size = (instance.texture_size[0]+instance.font_size, instance.texture_size[1]+instance.font_size/2)
        else:
            instance.width = Window.width/3.5
            instance.text_size = (instance.width-instance.font_size, None)
            
    def _update_label_pos(self, index, instance, value):
        """
        Update sign position.
        """
        connexion, outline, object_box = self.temp[index]
        if self.info_list[index][0] == 'left':
            instance.x=object_box.x-instance.width-30
        elif self.info_list[index][0] == 'right':
            instance.x=object_box.x+object_box.width+30
        instance.center_y=object_box.center_y                

        
    def _update_label_canvas(self, index, instance, value):
        """
        Update canvases of sign.
        """
        connexion, outline, object_box = self.temp[index]
        if self.info_list[index][0] == 'left':
            connexion.points = [(object_box.x, object_box.y+object_box.height/2), (instance.x+instance.width, instance.y+instance.height/2)]
        elif self.info_list[index][0] == 'right':     
            connexion.points = [(object_box.x+object_box.width, object_box.y+object_box.height/2), (instance.x, instance.y+instance.height/2)]
        outline.rectangle = [instance.x, instance.y, instance.width, instance.height]
        
        
