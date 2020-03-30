# -*- coding: utf-8 -*-


from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from math import sqrt
from util import *


Builder.load_string("""  
<ResizableButton>:

	canvas:
	
		Color:
			rgba: 0, 1, 1, 0
			group: "BL"
		Ellipse:
			pos: (self.corner_centers[0][0]-self.corner_radius, self.corner_centers[0][1]-self.corner_radius)
			size: (2*self.corner_radius, 2*self.corner_radius)
			group: "BL"
			
		Color:
			rgba: 0, 1, 1, 0
			group: "BR"
		Ellipse:
			pos: (self.corner_centers[1][0]-self.corner_radius, self.corner_centers[1][1]-self.corner_radius)
			size: (2*self.corner_radius, 2*self.corner_radius)
			group: "BR"
			
		Color:
			rgba: 0, 1, 1, 0
			group: "TR"
		Ellipse:
			pos: (self.corner_centers[2][0]-self.corner_radius, self.corner_centers[2][1]-self.corner_radius)
			size: (2*self.corner_radius, 2*self.corner_radius)
			group: "TR"
			
		Color:
			rgba: 0, 1, 1, 0
			group: "TL"
		Ellipse:
			pos: (self.corner_centers[3][0]-self.corner_radius, self.corner_centers[3][1]-self.corner_radius)
			size: (2*self.corner_radius, 2*self.corner_radius)
			group: "TL"
""")  

class ResizableButton(Button):
    
    corner_centers = ListProperty([(0, 0), (0, 0), (0, 0), (0, 0)])
    corner_radius = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(ResizableButton, self).__init__(**kwargs)
        self.corner_radius = 3
        self.update_corners()
        
    def switch_corners(self):
        for corner_name in ['BL', 'BR', 'TR', 'TL']:
            self.canvas.get_group(corner_name)[0].rgba[3] = 1 - self.canvas.get_group(corner_name)[0].rgba[3]
    
    def update_corners(self):
        for corner_name in ['BL', 'BR', 'TR', 'TL']:
            if corner_name == 'BL':
                self.corner_centers[0] = (self.pos[0], self.pos[1])
            elif corner_name == 'BR':
                self.corner_centers[1] = (self.pos[0]+self.size[0], self.pos[1])
            elif corner_name == 'TR':
                self.corner_centers[2] = (self.pos[0]+self.size[0], self.pos[1]+self.size[1])
            else:
                self.corner_centers[3] = (self.pos[0], self.pos[1]+self.size[1])
    
    def update_outline(self):
        if self.canvas.get_group('outline'):
            self.canvas.get_group('outline')[0].children[2].rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update_filling(self):
        if self.canvas.get_group('filling'):
            self.canvas.get_group('filling')[0].children[2].pos = self.pos
            self.canvas.get_group('filling')[0].children[2].size = self.size




class Resizer(FloatLayout):

    obj = ObjectProperty()
    current_button = None
    current_area = None
    is_grab = False
    buttons = []
    is_active = False

    
    def __init__(self, **kwargs):
        super(Resizer, self).__init__(**kwargs)
  
    
    def activate(self):
        self.manager = self.obj.root
        self.buttons = list((self.manager.current_document.pages[self.manager.current_document.index_current_page].button_boxes.keys()))
        Window.bind(mouse_pos=self.highlight)
        Window.bind(on_touch_move=self.potentially_resize_button)
        Window.bind(on_touch_down=self.select)
        Window.bind(on_touch_up=self.reset)
        for button in self.buttons:
            button.switch_corners()
        self.is_active = True
    
    def disable(self):
        
        Window.unbind(mouse_pos=self.highlight)
        Window.unbind(on_touch_move=self.potentially_resize_button)
        Window.unbind(on_touch_down=self.select)
        Window.unbind(on_touch_up=self.reset)
        for button in self.buttons:
            button.switch_corners()
        self.is_active = False
        

    def highlight(self, mouse, pos):
        pos = self.manager.my_zoom.transform_to_local(pos)
        find_button = False
        find_area = False
        if not self.is_grab:
            for button in self.buttons:
                if button.pos[0] < pos[0] < button.pos[0]+button.size[0] and button.pos[1] < pos[1] < button.pos[1]+button.size[1]:
                    if not find_button or \
                        is_inside([self.current_button.pos, 
                                  (self.current_button.pos[0]+self.current_button.size[0], 
                                   self.current_button.pos[1]+self.current_button.size[1])],
                                   [button.pos, (button.pos[0]+button.size[0], 
                                                button.pos[1]+button.size[1])]): 
                            self.current_button = button
                            find_button = True
                for index, corner_name in enumerate(['BL', 'BR', 'TR', 'TL']):
                    corner_center = button.corner_centers[index]
                    if sqrt((pos[0]-corner_center[0])**2+(pos[1]-corner_center[1])**2) < button.corner_radius:
                        button.canvas.get_group(corner_name)[0].rgba = (1, 0, 0, 1)
                        self.current_button = button
                        find_button = True
                        self.current_area = corner_name
                        find_area = True
                        break
                    else:
                        button.canvas.get_group(corner_name)[0].rgba = (0, 1, 1, 1)
            if not find_area:
                self.current_area = None
            if not find_button:
                self.current_button = None

    def update_current_button(self):
        self.current_button.update_corners()
        self.current_button.update_outline()
        self.current_button.update_filling()
        dico = self.manager.current_document.pages[self.manager.current_document.index_current_page].button_boxes
        box = dico[self.current_button]
        coordinates = [int(val) for val in self.manager.button_coord_to_box_coord(self.current_button)]
        box.update_coord(coordinates)
        
        
    def potentially_resize_button(self, mouse, touch):
        pos = self.manager.my_zoom.transform_to_local(touch.pos)

        if self.current_button and self.is_grab:
            
            # Bottom left corner is grab
            if self.current_area == "BL":
                limit_point = (self.current_button.pos[0]+self.current_button.size[0]-5, self.current_button.pos[1]+self.current_button.size[1]-5)
                if pos[0] < limit_point[0] and pos[1] < limit_point[1]:
                    dx = pos[0] - self.current_button.pos[0]
                    dy = pos[1] - self.current_button.pos[1]
                    self.current_button.pos = pos
                    self.current_button.size = (self.current_button.size[0] - dx, self.current_button.size[1] - dy)
            
            # Bottom right corner is grab
            elif self.current_area == "BR":
                limit_point = (self.current_button.pos[0]+5, self.current_button.pos[1]+self.current_button.size[1]-5)
                if pos[0] > limit_point[0] and pos[1] < limit_point[1]:
                    dx = pos[0] - self.current_button.pos[0]
                    dy = pos[1] - self.current_button.pos[1]
                    self.current_button.pos = (self.current_button.pos[0], self.current_button.pos[1] + dy)
                    self.current_button.size = (dx, self.current_button.size[1] - dy)
            
            # Top right corner is grab
            elif self.current_area == "TR":
                limit_point = (self.current_button.pos[0]+5, self.current_button.pos[1]++5)
                if pos[0] > limit_point[0] and pos[1] > limit_point[1]:
                    dx = pos[0] - self.current_button.pos[0]
                    dy = pos[1] - self.current_button.pos[1]
                    self.current_button.size = (dx,dy)
            
            # Top left corner is grab
            elif self.current_area == "TL":
                limit_point = (self.current_button.pos[0]+self.current_button.size[0]-5, self.current_button.pos[1]+5)
                if pos[0] < limit_point[0] and pos[1] > limit_point[1]:
                    dx = pos[0] - self.current_button.pos[0]
                    dy = pos[1] - self.current_button.pos[1]
                    self.current_button.pos = (self.current_button.pos[0] + dx, self.current_button.pos[1])
                    self.current_button.size = (self.current_button.size[0] - dx, dy)
            
            else:
                self.current_button.pos = (pos[0] - self.relative_button_pos[0], pos[1] - self.relative_button_pos[1])
               
            self.update_current_button()
            
    def select(self, mouse, touch):
        pos = self.manager.my_zoom.transform_to_local(touch.pos)
        if self.current_button:
            self.relative_button_pos = (pos[0] - self.current_button.pos[0], pos[1] - self.current_button.pos[1])
            poss = (self.current_button.pos[0], self.current_button.pos[1])
            sizee = (self.current_button.size[0], self.current_button.size[1])
            self.manager.canceller.modified_box(self.current_button, poss, sizee)
        self.is_grab = True    
            
    def reset(self, mouse, touch):
        if self.current_button:
            dico = self.manager.current_document.pages[self.manager.current_document.index_current_page].button_boxes
            new_button_LB = self.current_button.pos
            new_button_RT = (self.current_button.pos[0]+self.current_button.size[0], self.current_button.pos[1]+self.current_button.size[1])
            for other_button in dico:
                button_LB = other_button.pos
                button_RT = (other_button.pos[0]+other_button.size[0], other_button.pos[1]+other_button.size[1])
                if is_inside([new_button_LB, new_button_RT], [button_LB, button_RT]):
                    box = dico[other_button]
                    del dico[other_button]
                    dico[other_button] = box
                    self.manager.my_zoom.remove_widget(other_button)
                    self.manager.my_zoom.add_widget(other_button)
        self.is_grab = False
        self.current_button = None
