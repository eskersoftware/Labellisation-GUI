# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 13:55:30 2019

@author: Duvernay
"""
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior 
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.stencilview import StencilView




Builder.load_string("""  
<ImageButton>: 
    size_hint_y: None
    height: self.width
    size_hint_x: 0.3
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    allow_stretch: True
    keep_ratio: False
""")  

class ImageButton(ButtonBehavior, Image):  
    """
    A button whose background is an image.
    """
        
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)


Builder.load_string("""  
<Token>:
	size_hint: None, None
	height: self.minimum_height
	multiline: False
	halign: 'center'
	valign: 'middle'
	padding: 0
	foreground_color: (1, 0, 0, 1)
	background_color: (1, 1, 1, 1)
	on_text:
		self.width = self._lines_labels[0].width + self.font_size
	on_focus:
        app.root.inside_textbox = 1 - app.root.inside_textbox
		dico = app.root.current_document.pages[app.root.current_document.index_current_page].button_boxes
		dico[app.root.tokens_to_buttons[self]].token = self.text
""")  

class Token(TextInput):
    """
    A TextInput object that represents a token.
    """
    
    def __init__(self, pos, text, **kwargs):
        super(Token, self).__init__(**kwargs)
        self.pos = pos
        self.text = text     
        
        
Builder.load_string("""  
<BIO_label>:
	size_hint: None, None
	color: (1, 0, 1, 1) if self.text[0] == 'B' else (1, 0, 0, 1) if self.text[0] == 'I' else (0, 0, 1, 1)
	font_size: self.size[1] + 5
	bold: True
""")  

class BIO_Label(Label):
    
    def __init__(self, **kwargs):
        super(BIO_Label, self).__init__( **kwargs)


class Cursor(FloatLayout):
    """
    A cursor that follows mouse position on the screen.
    """
    
    cursor = None
    
    def __init__(self, **kwargs):
        super(Cursor, self).__init__(**kwargs)
        
        win = Window                                            # The window app        
        
        with self.canvas:                                       # Draw the cursor
            Color(0.3, 0.3, 0.7, 1)
            self.cursor = [                                     # Cursor is actually to rectangles
                Rectangle(pos=(0, 0), size=(1, win.height)),
                Rectangle(pos=(0, 0), size=(win.width, 1))]
        
        win.bind(mouse_pos=self.update_cursor_position)         # Call update_cursor_position() when the mouse move
        
    def update_cursor_position(self, mouse, pos):               # Update its position
        self.cursor[0].pos = pos[0], 0
        self.cursor[1].pos = 0, pos[1]
            
            
class BoxStencil(BoxLayout, StencilView):
    """
    A box that avoid its child go out its borders.
    """
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return super(BoxStencil, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return super(BoxStencil, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return super(BoxStencil, self).on_touch_up(touch)
