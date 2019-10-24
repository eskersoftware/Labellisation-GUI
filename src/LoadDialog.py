# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:39:15 2019

@author: Duvernay
"""

from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from os.path import join, isdir
import os
from kivy.lang import Builder

Builder.load_string("""  
<LoadDialog>:
	
	button_box: button_box
	pb: pb
	extraction_box: extraction_box
	
	FloatLayout:
	
		ProgressBar:
			id: pb
			pos: button_box.pos
			size: button_box.size
			size_hint: None, None
			height: '48dp'
			value: 0
			opacity: 0
		
		
		BoxLayout:
			id: extraction_box
			pos: button_box.pos
			size: button_box.size
			size_hint: None, None
			opacity: 0
			
			AnchorLayout:
				anchor_x: 'right'
				anchor_y: 'center'
				
				Image:
					pos_hint: {'center_x': 0.5}
					size_hint: None, None
					source: "keyboard_icones\\loading.gif"
					anim_delay: 0.1
					
			AnchorLayout:
				anchor_x: 'left'
				anchor_y: 'center'
				
				Label: 
					size_hint: None, None
					text: "Extracting..."
	
	
    BoxLayout:
		orientation: "vertical"
		pos: root.pos
        size: root.size
        
		BoxLayout:
			size_hint_y: 0.9
			spacing: 10
			padding: 10
			BoxLayout:
				orientation: "vertical"
				spacing: 10
				padding: 10
				
				Label:
					size_hint_y: 0.1
					text: "Input dataset"
					font_size: sp(40)
				
				BoxLayout:
					size_hint_y: 0.1
					orientation: 'horizontal'
					size_hint_y: None
					height: 30
					
					Label:
						size_hint_x: None
						size: self.texture_size
						text: 'Path:  '
					
					TextInput:
						id: text_input
						text: filechooser_input.path if not filechooser_input.selection else filechooser_input.selection[0]
						multiline: False
						on_text_validate:
							the_path = self.text
							filechooser_input.path = the_path if root.verify(the_path) else "\"
							filechooser_input.selection = [the_path] if root.verify(the_path) else []
							self.text = the_path if root.verify(the_path) else "\"

				
				FileChooserListView:
					id: filechooser_input
					size_hint_y: 0.8
					dirselect: True
					filters: [root.is_dir, '*.zip']
					selection: [root.potential_input_dataset]
					path: root.potential_input_dataset
					
			BoxLayout:
				orientation: "vertical"
				spacing: 10
				padding: 10
				
				Label:
					size_hint_y: 0.1
					text: "Ouput directory"
					font_size: sp(40)
					
				BoxLayout:
					size_hint_y: 0.1
					orientation: 'horizontal'
					size_hint_y: None
					height: 30
					
					Label:
						size_hint_x: None
						size: self.texture_size
						text: 'Path:  '
					
					TextInput:
						id: text_output
						text: filechooser_output.path if not filechooser_output.selection else filechooser_output.selection[0]
						multiline: False
						on_text_validate:
							the_path = self.text
							filechooser_output.path = the_path if root.verify(the_path) else "\"
							filechooser_output.selection = [the_path] if root.verify(the_path) else []
							self.text = the_path if root.verify(the_path) else "\"
				
				FileChooserListView:
					id: filechooser_output
					size_hint_y: 0.8
					dirselect: True
					filters: [root.is_dir]
					selection: [root.potential_output_directory]
					path: root.potential_output_directory
					
					

        BoxLayout:
			id: button_box
			orientation: "vertical"
            size_hint_y: 0.1			
			
			Button:
                text: "Load"
				disabled: not (root.verify(text_input.text) and root.verify(text_output.text)) or not button_box.opacity
                on_release: 
					root.load(text_input.text, text_output.text)
					app.root.box_beginning.parent.remove_widget(app.root.box_beginning)

			
            Button:
                disabled : not button_box.opacity
                text: "Cancel"
                on_release: root.cancel()
""")  

class LoadDialog(FloatLayout):
    """
    This allows to use FileChooser for selecting input dataset and output directory.
    """
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    potential_input_dataset = StringProperty("\\")
    potential_output_directory = StringProperty("\\")
    pb = ObjectProperty(None)
    extraction_box = ObjectProperty(None)
    button_box = ObjectProperty(None)
    
    
    def is_dir(self, directory, filename):
        """
        Allow to only display directories.
        """
        return isdir(join(directory, filename))
    
    def verify(self, input_path):
        return os.path.exists(input_path) and input_path != "/"