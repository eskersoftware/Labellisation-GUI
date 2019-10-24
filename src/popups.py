# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 13:47:29 2019

@author: Duvernay
"""

from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.lang import Builder
import ast
from PieChart import PieChart
from random import randint
from kivy.uix.stacklayout import StackLayout
from util import *



Builder.load_string("""  
<MetaInfo>:
	
	label: label
	text_input: text_input
	spacing: 10
	padding: 10
	
	Label:
		id: label
		size_hint_x: .4
		pos_hint: {'center_y': 0.5}

		
	TextInput:
		id: text_input
		size_hint: (.4, None)
		height: self.minimum_height
		pos_hint: {'center_y': 0.5}
		write_tab: False
		multiline: False
		on_focus:
			app.root.inside_textbox = 1 - app.root.inside_textbox
			app.root.popMetadata.update_info(self.parent)
			
		
	FloatLayout:
		size_hint_x: 0.2
		
		ImageButton:
			source: 'keyboard_icones\dustbin.png'
			size_hint: None, None
			height: text_input.height
			width: self.image_ratio * self.height
			pos_hint: {'center_x': .5, 'center_y':.5}
			on_press:
				app.root.popMetadata.del_info(self.parent.parent)
""")  

class MetaInfo(BoxLayout):
    
    label = ObjectProperty(None)
    text_input = ObjectProperty(None)
    
    def __init__(self, metaname, metavalue, **kwargs):
        super(MetaInfo, self).__init__(**kwargs)
        self.label.text = metaname + ": "
        self.text_input.text = metavalue




Builder.load_string("""  
<MetadataPopup>:
	id: pop
	size_hint: (None, None)
	size: 900, 700
    title: 'Metadata'
	title_size: 30
	auto_dismiss: False
	on_open: app.root.in_Popup['MetadataPopup'] = True
	on_dismiss: app.root.in_Popup['MetadataPopup'] = False
	
	info_grid: info_grid
	
	BoxLayout:
		orientation: 'vertical'
		
		BoxLayout:
			size_hint_y: 0.05
			
			Button:
				size_hint_x: 0.05
				text: "+"
				on_release:
					F.AddMetaNamePopup().open()
			
			BoxLayout:
				size_hint_x: 0.95
			
		GridLayout:
			id: info_grid
			spacing: 10
			padding: 10
			size_hint_y: 0.9
			cols: 3
		
		BoxLayout:
			size_hint_y: 0.05
				
			Button:
				text: 'Done'
				on_release:
					app.root.in_MetadataPopup = False
					pop.dismiss()

<AddMetaNamePopup@Popup>:
	id: pop
	size_hint: (None, None)
	size: 500, 120
	title: "Add data"
	title_size: 16
	auto_dismiss: False
	
	BoxLayout:
		orientation: 'vertical'
		
		BoxLayout:
			
			Label:
				size_hint_x: 0.2
				text: "name:"
				
			TextInput:
				id: new_data_name
				size_hint_x: 0.7
				multiline: False
				on_focus:
					app.root.inside_textbox = 1 - app.root.inside_textbox
		
		BoxLayout:
		
			Button:
				text: "Add only for this document"
				on_release:
					app.root.popMetadata.add_info(new_data_name.text, "")
					pop.dismiss()
			
			Button:
				text: "Add for the whole dataset"
				on_release:
					app.root.popMetadata.add_info(new_data_name.text, "", True)
					pop.dismiss()
""")  

    
    
    
class MetadataPopup(Popup):
    """
    'Metadata' popup.
    """    
    
    info_grid = ObjectProperty(None)
    general_metadata = set()
    current_metadata = {}
    
    def __init__(self, **kwargs):
        super(MetadataPopup, self).__init__(**kwargs)
        
    def add_info(self, metaname, metavalue, general=False):
        if general:
            self.general_metadata.add(metaname)
        if metaname not in self.current_metadata:
            self.info_grid.add_widget(MetaInfo(metaname, metavalue))
            self.current_metadata[metaname] = metavalue
        
    
    def del_info(self, metainfo):
        metaname = metainfo.label.text[:-2]
        if metaname in self.general_metadata:
            self.general_metadata.remove(metaname)
        self.info_grid.remove_widget(metainfo)
        del self.current_metadata[metaname]
    
    def load_info(self, metaname, metavalue):
        self.add_info(metaname, metavalue, False)
    
    def update_info(self, metainfo):
        metaname = metainfo.label.text[:-2]
        metavalue = metainfo.text_input.text
        self.current_metadata[metaname] = metavalue
    
    def reinitiate(self):
        self.current_metadata = {}
        self.info_grid.clear_widgets()




Builder.load_string("""  
<ProjectPopup>:
	id: pop
	size_hint: (None, None)
	size: 1100, 600
    title: 'Project metrics'
	title_size: 16
	piechart_box: piechart_box
	on_open: app.root.in_Popup['ProjectPopup'] = True
	on_dismiss: app.root.in_Popup['ProjectPopup'] = False
	
	BoxLayout:
		orientation: "vertical"
		
		BoxLayout:
			id: piechart_box
			size_hint_y: 0.95
			
		Button:
			size_hint_y: 0.05
			text: "Close"
			on_release:
				pop.dismiss()
""")  

class ProjectPopup(Popup):
    
    piechart_box = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ProjectPopup, self).__init__(**kwargs)
    
    def open(self, caller, *largs, **kwargs):
        self.piechart_box.clear_widgets()
        if caller.labelling:
            in_data={"Approved": (caller.nb_approved, [.19, .80, .84, 1]),
                  "Not approved": (caller.nb_documents-caller.nb_approved, [.83, .86, .89, 1])}
            boxlayout = BoxLayout(orientation='vertical')
            box = BoxLayout(size_hint_y=0.9)            
            box.add_widget(PieChart(in_data=in_data))
            boxlayout.add_widget(box)
            boxlayout.add_widget(Label(text="Labelling", size_hint_y=0.1, halign='center', valign='middle', font_size=25))
            self.piechart_box.add_widget(boxlayout)
        if caller.classification:
            colors = [[randint(10, 50)/50 for i in range(3)] + [1]]
            in_data = {"Unclassified": (caller.nb_documents, colors[0])}
            for _class in list(caller.class_directory.values()):
                new_col = [randint(10, 50)/50 for i in range(3)] + [1]
                limit = 0
                while True in [dist(new_col, col)<0.3 for col in colors] and limit<10:
                    new_col = [randint(10, 50)/50 for i in range(3)] + [1]
                    limit += 1
                colors.append(new_col)
                in_data[_class.name] = (len(_class.batch), new_col)
                in_data["Unclassified"] = (in_data["Unclassified"][0]-len(_class.batch), in_data["Unclassified"][1]) 
            _temp = in_data["Unclassified"]
            del in_data["Unclassified"]
            in_data["Unclassified"] = _temp            
            boxlayout = BoxLayout(orientation='vertical')
            box = BoxLayout(size_hint_y=0.9)
            box.add_widget(PieChart(in_data=in_data))
            boxlayout.add_widget(box)
            boxlayout.add_widget(Label(text="Classification", size_hint_y=0.1, halign='center', valign='middle', font_size=25))
            self.piechart_box.add_widget(boxlayout)
        super(ProjectPopup, self).open(*largs, **kwargs)
        
        
        
        
Builder.load_string("""  
<ColorPopup>:
	id: pop	
	size_hint: (None, None)
	size: 500, 500
    title: 'Choose a name and pick a color'
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['ColorPopup'] = True
	on_dismiss: app.root.in_Popup['ColorPopup'] = False
	
	text_label: text_label
	colpic: colpic
	
	on_open:
		create_button.disabled = True
	
	BoxLayout:
		orientation: "vertical"
		spacing: 10
		padding: 10
		text_label: text_label
		colpic: colpic
		
		BoxLayout:
			size_hint_y: 0.1
			
			Label:
				size_hint_x: 0.2
				text: "Label name: "
			TextInput:
				id: text_label
				size_hint_x: 0.8
				multiline: False
				on_focus:
					app.root.inside_textbox = 1 - app.root.inside_textbox
					create_button.disabled = False
				
		ColorPicker2:
			id: colpic
			
		BoxLayout:
			size_hint_y: 0.1
			
			
			
			Button:
				id: create_button
				text: "Create Label"
				disabled: True
				on_release:
					app.root.add_label(colpic.color[:3], text_label.text, root.mode)
					pop.dismiss()
					text_label.text = ""
					colpic.wheel.disable_arc()
					
					
			Button:
				text: "Cancel"
				on_release:
					pop.dismiss()
""")  

class ColorPopup(Popup):
    """
    'Choose a color' popup.
    """    
    
    mode = None
    
    def __init__(self, **kwargs):
        super(ColorPopup, self).__init__(**kwargs)

    
    
    
Builder.load_string("""  
<DelClassPopup>:
	id: pop
	size_hint: (None, None)
	size: 500, 200
    title: 'Delete a used class'
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['DelClassPopup'] = True
	on_dismiss: app.root.in_Popup['DelClassPopup'] = False
	
	BoxLayout:
		orientation: 'vertical'
		
		Label:
			size_hint_y: 0.7
			text: "Are you sure you want to delete this class?\\nThis currently contains files so it will unlist them."
			text_size: self.size
			halign: 'center'
			valign: 'middle'
			
		BoxLayout:
			orientation: 'horizontal'
			size_hint_y: 0.3
			
			Button:
				text: 'Yes'
				on_release:	
					app.root.unlist_files(root.remove_button)
					pop.dismiss()
					
			Button:
				text: 'No'
				on_release: 
					pop.dismiss()
""")  

class DelClassPopup(Popup):
    """
    'Delete Class' popup.
    """    
    remove_button = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(DelClassPopup, self).__init__(**kwargs)



Builder.load_string("""  
<ErrorPopup>:
	size_hint: (None, None)
	size: 600, 300
    title: 'Error'
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['ErrorPopup'] = True
	on_dismiss: app.root.in_Popup['ErrorPopup'] = False
	
	BoxLayout:
		orientation: 'vertical'
	
		BoxLayout:
			size_hint_y: 0.9
		
			Image:
				size_hint_x: 0.2
				source: "keyboard_icones\\error.png"
			
			Label:
				size_hint_x: 0.8
				text: root.message 
				text_size: self.size
				halign: 'center'
				valign: 'middle'
				
		Button:
			size_hint_y: 0.1
			text: 'Close'
			on_release:
				app.stop()
""")          

class ErrorPopup(Popup):
    """
    When an exception is raised.
    """
    message = StringProperty("None")
    
    def __init__(self, message, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.message = message
        
        
        

Builder.load_string("""  
<WarningPopup>:
	id: pop
	size_hint: (None, None)
	size: 600, 300
    title: 'Warning'
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['WarningPopup'] = True
	on_dismiss: app.root.in_Popup['WarningPopup'] = False
	
	
	BoxLayout:
		orientation: 'vertical'
	
		BoxLayout:
			size_hint_y: 0.9
		
			Image:
				size_hint_x: 0.2
				source: "keyboard_icones\\warning.png"
			
			Label:
				size_hint_x: 0.8
				text: root.message 
				text_size: self.size
				halign: 'center'
				valign: 'middle'
				
		Button:
			size_hint_y: 0.1
			text: 'Close'
			on_release:
				pop.dismiss()
""")  

class WarningPopup(Popup):
    """
    When an exception is raised.
    """
    message = StringProperty("None")
    
    def __init__(self, message, **kwargs):
        super(WarningPopup, self).__init__(**kwargs)
        self.message = message




Builder.load_string("""  
<DelLabelPopup>:
	id: pop
	size_hint: (None, None)
	size: 600, 200
    title: 'Delete a used label'
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['DelLabelPopup'] = True
	on_dismiss: app.root.in_Popup['DelLabelPopup'] = False
	
	BoxLayout:
		orientation: 'vertical'
		
		Label:
			size_hint_y: 0.7
			text: "Are you sure you want to delete this label ?\\nThis document contains boxes tagged with it so it will tag them by 'None'."
			text_size: self.size
			halign: 'center'
			valign: 'middle'
			
		BoxLayout:
			orientation: 'horizontal'
			size_hint_y: 0.3
			
			Button:
				text: 'Yes'
				on_release:	
					app.root.untag(root.remove_button)
					app.root.canceller.reset()
					pop.dismiss()
					
			Button:
				text: 'No'
				on_release: 
					pop.dismiss()
""")  

class DelLabelPopup(Popup):
    """
    'Delete Label' popup.
    """    
    remove_button = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(DelLabelPopup, self).__init__(**kwargs)




Builder.load_string("""  
<AddClassPopup>:
	id: pop
    size_hint: (None, None)
	size: 500, 100
    title: 'Add a new class'
	title_size: 16
	on_open:
		app.root.inside_textbox = True
		app.root.in_Popup['AddClassPopup'] = True
	
	on_dismiss:
		text_input.text = ""
		app.root.inside_textbox = False
		app.root.in_Popup['AddClassPopup'] = False
	
	BoxLayout:
					
		Label:
			size_hint_x: 0.2
			text: "Name:"
			
		TextInput:
			id: text_input
			size_hint_x: 0.8			
			multiline: False
			focus: True
			on_text_validate:
				verif = self.text not in [_class.name for _class in list(app.root.class_directory.values())]
				if verif: root.class_name = self.text
				if verif: pop.dismiss()
				if verif: app.root.popKey.open(mode="add_class")
				if verif: app.root.in_DefineKeyPopup = True
""")  

class AddClassPopup(Popup):
    """
    'Add Class' popup.
    """    
        
    def __init__(self, **kwargs):
        super(AddClassPopup, self).__init__(**kwargs)




Builder.load_string("""  
<DefineHotKeyPopup>:
	id: popDefineKey
    size_hint: (None, None)
	size: 500, 500
    title: 'Define a hotkey'
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['DefineHotKeyPopup'] = True
	on_dismiss: app.root.in_Popup['DefineHotKeyPopup'] = False
	
	Label:
		text: "Press key"


""")  

class DefineHotKeyPopup(Popup):
    """
    'Define key Class' popup.
    """
    caller = None
    mode = None
    
    def __init__(self, **kwargs):
        super(DefineHotKeyPopup, self).__init__(**kwargs)
        
    def open(self, caller=None, mode=None, *largs, **kwargs):
        self.caller = caller
        self.mode = mode
        super(DefineHotKeyPopup, self).open(*largs, **kwargs)
        
    
    

Builder.load_string("""  
<ArchivePopup>:
	id: pop
    size_hint: (None, None)
	size: 500, 200
    title: "Effectively class in folders"
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['ArchivePopup'] = True
	on_dismiss: app.root.in_Popup['ArchivePopup'] = False
	
	BoxLayout:
		orientation: "vertical"
	
		Label:
			size_hint_y: 0.6
			text: "You are about to archive your work.\\n This action will generate an _archive folder and quit the app."
			text_size: self.size
			halign: 'center'
			valign: 'middle'
			
		BoxLayout:
			size_hint_y: 0.2
		
			Button:
				text: "Move files"
				disabled: not root.deletion_rights
				on_release:
					app.root.archive('move')
					pop.dismiss()
					app.stop()
				
			Button:
				text: "Duplicate files"
				on_release:
					app.root.archive('duplicate')
					pop.dismiss()
					app.stop()

		Button:
			size_hint_y: 0.2
			text: "Cancel"
			on_release:
				pop.dismiss()

""")  

class ArchivePopup(Popup):
    """
    'Move files to folders' popup.
    """
    deletion_rights = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(ArchivePopup, self).__init__(**kwargs)
    
    def open(self, deletion_rights, *largs, **kwargs):
        self.deletion_rights = deletion_rights
        super(ArchivePopup, self).open(*largs, **kwargs)
        
        
        

Builder.load_string("""  
<Field>:
	size_hint: 1, None
	height: 40
	padding: 5
	spacing: 5

	BoxLayout:
		size_hint_x: None
		width: root.indent_length
	
	Label:
		size_hint_x: None
		width: self.texture_size[0]
		text: 'FIELD: '
		
	TextInput:
		size_hint_x: None
		width: 200
		write_tab: False
		multiline: False
		text: root.field_name
		on_focus:
			root.field_name = self.text
		
	Label:
		size_hint_x: None
		width: self.texture_size[0]
		text: '  Label: '
		
	Spinner:
		size_hint_x: None
		text: root.label_name
		width: 200
		values: ("None")
		on_press:
			self.values = (val for val in list(app.root.current_document.label_color.keys())) if app.root and app.root.current_document else ("None")
		on_text:
			root.label_name = self.text
			
	ImageButton:
		source: 'keyboard_icones\dustbin.png'
		size_hint: None, None
		height: 20
		width: self.image_ratio * self.height
		pos_hint: {'center_x': .5, 'center_y':.5}
		on_press:
			root.parent.remove_widget(root)
			
	BoxLayout:
""")     
    
class Field(BoxLayout):
    
    indent_length = NumericProperty(0)
    field_name = StringProperty("")
    label_name = StringProperty("None")
    
    def __init__(self, indent_length, field_name, label_name, **kwargs):
        super(Field, self).__init__(**kwargs)
        self.indent_length = indent_length
        self.field_name = field_name
        self.label_name = label_name




Builder.load_string("""  
<Table>:
	orientation: 'lr-tb'
	size_hint: 1, None
	height: self.minimum_height
	padding: 5
	spacing: 5
	
	_content: _content
	
	BoxLayout:
		size_hint: 1, None
		height: 30
	
		BoxLayout:
			size_hint_x: None
			width: root.indent_length
			
		Label:
			size_hint_x: None
			width: self.texture_size[0]
			text: 'From TABLE   '
			
		TextInput:
			size_hint_x: None
			width: 200
			write_tab: False
			multiline: False
			text: root.table_name
			on_focus:
				root.table_name = self.text
		Label
			size_hint_x: None
			width: self.texture_size[0]
			text: ':   '
		
		Button:
			size_hint_x: None
			width: self.texture_size[0]
			text: '   +   '
			on_press:
				root.fill_content()
				
		ImageButton:
			source: 'keyboard_icones\dustbin.png'
			size_hint: None, None
			height: 20
			width: self.image_ratio * self.height
			pos_hint: {'center_x': .5, 'center_y':.5}
			on_press:
				root.parent.remove_widget(root)

			
	StackLayout:
		id: _content
		orientation: 'lr-tb'
		size_hint: 1, None
		height: self.minimum_height
""")     
    
class Table(StackLayout):
    
    indent_length = NumericProperty(0)
    _content = ObjectProperty(None)
    table_name = StringProperty("")
        
    def __init__(self, indent_length, table_name, table_fields, **kwargs):
        super(Table, self).__init__(**kwargs)
        self.indent_length = indent_length
        self.table_name = table_name
        for field_name in list(table_fields.keys()):
            self.fill_content(field_name=field_name, label_name=table_fields[field_name])
        
    def fill_content(self, field_name="", label_name="None"):
        self._content.add_widget(Field(self.indent_length+100, field_name, label_name))


        
  
Builder.load_string("""  
<Branch>:
	orientation: 'lr-tb'
	size_hint: 1, None
	height: self.minimum_height
	padding: 5
	spacing: 5
	
	_content: _content

	BoxLayout:
		size_hint: 1, None
		height: 40

		BoxLayout:
			size_hint_x: None
			width: root.indent_length

		Label:
			size_hint_x: None
			width: self.texture_size[0]
			text: 'From   ' + root.name + ':   '
			
		Button:
			size_hint_x: None
			width: self.texture_size[0]
			text: '   +   '
			on_press:
				root.fill_content()
					
				
	StackLayout:
		id: _content
		orientation: 'lr-tb'
		size_hint: 1, None
		height: self.minimum_height
""")        
        
class Branch(StackLayout):
    
    
    name = StringProperty("")
    content_type = StringProperty("")
    indent_length = NumericProperty(0)
    _content = ObjectProperty(None)
        
    def __init__(self, name, content_type, indent_length, **kwargs):
        super(Branch, self).__init__(**kwargs)
        self.name = name
        self.content_type = content_type
        self.indent_length = indent_length
        
    def fill_content(self, field_name="", label_name="None", table_name="", table_fields={}):
        if self.content_type == "field":
            self._content.add_widget(Field(self.indent_length+100, field_name, label_name))
        elif self.content_type == "table":
            self._content.add_widget(Table(self.indent_length+100, table_name, table_fields))
            
        
        
Builder.load_string("""  
<QuitPopup>:
	id: pop
	size_hint: (None, None)
	size: 500, 200
    title: 'Quit the app'
	title_size: 16
	auto_dismiss: False
	on_open: app.root.in_Popup['QuitPopup'] = True
	on_dismiss: app.root.in_Popup['QuitPopup'] = False
	
	BoxLayout:
		orientation: 'vertical'
		
		Label:
			size_hint_y: 0.7
			text: "Are you sure you want to quit the app?"
			text_size: self.size
			halign: 'center'
			valign: 'middle'
			
		BoxLayout:
			orientation: 'horizontal'
			size_hint_y: 0.3
			
			Button:
				text: 'Quit'
				on_release:
					app.get_running_app().stop()
					
			Button:
				text: 'Cancel'
				on_release: 
					pop.dismiss()
""")     
        
class QuitPopup(Popup):
    """
    'Quit' popup.
    """    
    def __init__(self, **kwargs):
        super(QuitPopup, self).__init__(**kwargs)





Builder.load_string("""  
<GoToPopup>:
	id: pop
	size_hint: (None, None)
	size: 700, 150
    title: 'Move to a particular document'
	title_size: 16
	on_open: app.root.in_Popup['GoToPopup'] = True
	on_dismiss: 
        app.root.in_Popup['GoToPopup'] = False
        text_input.text = ""
    
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            
            Button:
                size_hint_x: 0.2
                text: "Move to: "
                on_release:
                    app.root.move_to('user_choice', text_input.text)
                    pop.dismiss()
                
            TextInput:
                size_hint_x: 0.8
                id: text_input
                text: ""
                multiline: False
        		on_focus:
        			app.root.inside_textbox = 1 - app.root.inside_textbox
            
        Button:
            text: "Move to first unclassified"
            disabled: not root.classification
            on_release:
                app.root.move_to('unclassified')
                pop.dismiss()
                
        Button:
            text: "Move to first not approved"
            disabled: not root.labelling
            on_release:
                app.root.move_to('not_approved')
                pop.dismiss()
                
	

""")  
    
class GoToPopup(Popup):
    """
    'Go to' popup to move to a particular document.
    """    
    
    classification = BooleanProperty(False)
    labelling = BooleanProperty(False)
    
    def __init__(self, classification, labelling, **kwargs):
        super(GoToPopup, self).__init__(**kwargs)
        self.classification = classification
        self.labelling = labelling


