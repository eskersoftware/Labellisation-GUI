# -*- coding: utf-8 -*-


from kivy.properties import ObjectProperty, ListProperty
from util import *
from Resizer import ResizableButton
from graphical_elements import Token
from data_description import Box
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout


from kivy.lang import Builder



Builder.load_string("""  
<LinePlayground>:

    canvas:
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Line:
            points: self.points
            close: True
""")  

class LinePlayground(FloatLayout):
    """
    A layout in which rectangles can be drawn.
    This is used to tag, remove, merge and encapsulate several boxes
    as well as to create a new box.
    """

    points = ListProperty([])        # Used to save the four points of the rectangle
    obj = ObjectProperty()           # Used to call the main app
    
    has_moved = False                # Used to now if mouse has actually moved between touch_down and touch_up events
    cancellation = False
    
    
    def __init__(self, **kwargs):
        super(LinePlayground, self).__init__(**kwargs)
        Window.bind(on_touch_up=self.potentially_cancel)
        
    def potentially_cancel(self, *args):
        if 1 in Window._mouse_buttons_down and self.obj.root.cursor_tool != "Move/Resize": # User was ussing another mouse button, so it has to cancel the rectangle creation
            self.cancellation = True
            
    
    def on_touch_down(self, touch):
        """
        Place the first point.
        """
        # Reset booleans
        self.has_moved = False                                  
        self.cancellation = False
        if touch.button == 'left' and self.obj.root.dataset and self.obj.root.cursor_tool != "Move/Resize":    # If user is using left mouse button and dataset has already been defined
            touch.grab(self)                                    # This allows to dispatch a touch event to a child widget
            self.points.append(touch.pos)                       # Append the curent mouse position (first point of the rectangle)
        
        return super(LinePlayground, self).on_touch_down(touch)
        
        
    def on_touch_move(self, touch):
        """
        Drawn the rectangle.
        """
        self.has_moved = True                                   # Set this boolean to true because the mouse is moving
        if touch.button == 'left' and self.obj.root.dataset and self.obj.root.cursor_tool != "Move/Resize":    # If user is using left mouse button and dataset has already been defined
            if len(self.points) == 1:                               # This correspond to the first movement
                # Add the three other points
                second_point = (touch.pos[0], self.points[0][1])    
                self.points.append(second_point)
                self.points.append(touch.pos)
                fourth_point = (self.points[0][0], touch.pos[1])
                self.points.append(fourth_point)
            if touch.grab_current is self:                          # This correspond to the rest of the movements
                # Update positions of the three other points
                self.points[2] = touch.pos
                second_point = (touch.pos[0], self.points[0][1])
                self.points[1] = second_point
                fourth_point = (self.points[0][0], touch.pos[1])
                self.points[3] = fourth_point
        return super(LinePlayground, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        """
        Effectively create the rectangle.
        """
        if self.obj.root.current_pressed_button:                                        # If a button is currently pressed
                self.obj.root.current_pressed_button.background_color = (1, 1, 1, 0)    # Reset the background of the button because user has release the mouse button
        
        if touch.button == 'left' and self.obj.root.dataset:                            # If user is using left mouse button and dataset has already been defined
            
            if touch.grab_current is self:
                
                touch.ungrab(self)
                
                manager = self.obj.root      
                                                       # The app manager
                transfo_points = [manager.my_zoom.transform_to_local(p) for p in self.points]       # Turn current points coordinates into my_zoom local coordinates
                transfo_points_LB, transfo_points_RT = give_bottom_left_corner(transfo_points), give_top_right_corner(transfo_points)   # Take the bottom left and top right point of the rectangle
                
                dico = manager.current_document.pages[manager.current_document.index_current_page].button_boxes       # Dictionnary for accessing boxes from buttons of the current document
                
                undo_delete = []
                undo_create = {}
                undo_tag = []
                undo_labels = []
                undo_bio_letter= []
                
                # TAG SEVERAL BOXES     
                if manager.cursor_tool == "Tag" and self.has_moved and self.obj.root.checkbox_showboxes.active and not self.cancellation: # If 'Tag' mode is selected, mouse has moved and 'Show boxes' checkbox is activated and no cancellation 
                         
                                                                                       # (this checkbox condition avoid to tag the first document without showing other boxes)
                    beginning_button = ResizableButton(pos=(transfo_points_RT[0], transfo_points_LB[1]))
                    beginning_exists = False
                    for button in dico:     # For each button
                        button_LB = button.pos                                                         # Take the bottom left point of the button
                        button_RT = (button.pos[0]+button.size[0], button.pos[1]+button.size[1])        # Take the top right point of the button
                        if is_inside([transfo_points_LB, transfo_points_RT], [button_LB, button_RT]):   # If the button is inside the rectangle
                            undo_tag.append(button)
                            
                            if not manager.accordion_BIO.collapse:
                                if manager.bio_tool == "Select chunk":
                                    undo_bio_letter.append(dico[button].BIO_prefix)
                                    manager.tag(button, multiple=True, bio_letter='I'+manager.BIO_ID)
                                    if button.pos[1] >= beginning_button.pos[1]:
                                        if  button.pos[0] < beginning_button.pos[0]:
                                            beginning_button = button
                                            beginning_exists = True
                                else:
                                    undo_bio_letter.append(dico[button].BIO_prefix)
                                    manager.tag(button, multiple=True)        # Tag it 
                            else:
                                undo_labels.append(dico[button].label)
                                manager.tag(button, multiple=True)        # Tag it 
                                
                    if manager.bio_tool == "Select chunk" and beginning_exists:
                        manager.tag(beginning_button, multiple=True, bio_letter='B'+manager.BIO_ID)
                    manager.canceller.update(undo_delete, undo_create, undo_tag, undo_labels, undo_bio_letter)        
                    
                
                # CREATE A NEW BOX
                elif manager.cursor_tool == "Create" and self.has_moved and self.obj.root.checkbox_showboxes.active and not self.cancellation:           # If 'Create' mode is selected, mouse has moved
                    button = manager.new_button(transfo_points_LB, transfo_points_RT)                  # Create a new button and the outline of the new box
                    
                    undo_delete.append(button)
                    
                    coordinates = manager.button_coord_to_box_coord(button)
                    page_frame = manager.current_document.pages[manager.current_document.index_current_page]
                    # Check the new box is actually inside the document page
                    
                    
                    if (coordinates[0] >= 0 and coordinates[1] >= 0 and coordinates[2] <= page_frame.pg_size_X and coordinates[3] <= page_frame.pg_size_Y) or not manager.checkbox_boxinside.active:

                        dico[button] = Box(coordinates, 100, "new token")    # Add the new box to the dictionnary
                        
                        # Draw it on the app
                        manager.my_zoom.add_widget(button)
                        manager.tag(button, during_box_creation=True)   # Create and tag the new box at the same time
                        
    
                        # Draw the smaller buttons over the new button (this allows user to click on them)                    
                        for other_button in list(dico.keys()):
                            button_LB = other_button.pos
                            button_RT = (other_button.pos[0]+other_button.size[0], other_button.pos[1]+other_button.size[1])
                            if is_inside([transfo_points_LB, transfo_points_RT], [button_LB, button_RT]):
                                box = dico[other_button]                                                    # Get the same order in dico
                                del dico[other_button]
                                dico[other_button] = box
                                manager.my_zoom.remove_widget(other_button)
                                manager.my_zoom.add_widget(other_button)
                        
                        # Load the new token if other tokens have already been loaded
                        if manager.tokens_already_loaded:
                            new_pos = manager.my_zoom.transform_to_parent((button.pos[0], button.pos[1]+button.size[1]))
                            token = Token(new_pos, dico[button].token)
                            manager.tokens_to_buttons[token] = button
                            manager.buttons_to_tokens[button] = token
                        
                        # Show the token if the 'Show tokens' checkbox is activated
                        if manager.checkbox_showtokens.active:
                            manager.my_box.add_widget(token)
                        
                        manager.canceller.update(undo_delete, undo_create, undo_tag, undo_labels, [])
                
                # MERGE SEVERAL BOXES           
                elif manager.cursor_tool == "Merge" and self.has_moved and self.obj.root.checkbox_showboxes.active and not self.cancellation:               # If 'Merge' mode is selected, mouse has moved and no cancellation
                    
                    buttons_to_merge_coord = []
                    merge_token = ""                # Used to create a new token from the merged boxes tokens
                    
                    # Remove buttons which are inside the rectangle in order to merge them
                    for button in list(dico.keys()):
                        button_LB = button.pos
                        button_RT = (button.pos[0]+button.size[0], button.pos[1]+button.size[1])
                        if is_inside([transfo_points_LB, transfo_points_RT], [button_LB, button_RT]):
                            merge_token += dico[button].token + " "
                            undo_create[button] = dico[button]
                            manager.remove(button, multiple=True)
                            buttons_to_merge_coord += [button_LB, button_RT]
                    
                    # If there are buttons to merge, effectively create the corresponding button
                    if buttons_to_merge_coord:
                        new_box_LB = give_bottom_left_corner(buttons_to_merge_coord)
                        new_box_RT = give_top_right_corner(buttons_to_merge_coord)
                        
                        button = manager.new_button(new_box_LB, new_box_RT)    
                        undo_delete.append(button)
                        dico[button] = Box(manager.button_coord_to_box_coord(button), 100, merge_token)
                        
                        manager.my_zoom.add_widget(button)
                        manager.tag(button, during_box_creation=True)
                        
                        
                        if manager.tokens_already_loaded:
                            new_pos = manager.my_zoom.transform_to_parent((button.pos[0], button.pos[1]+button.size[1]))
                            token = Token(new_pos, dico[button].token)
                            manager.tokens_to_buttons[token] = button
                            manager.buttons_to_tokens[button] = token
                        
                        if manager.checkbox_showtokens.active:
                            manager.my_box.add_widget(token)
                     
                    manager.canceller.update(undo_delete, undo_create, undo_tag, undo_labels, [])
                            
                # ENCAPUSLATE SEVERAL BOXES      
                elif manager.cursor_tool == "Encapsulate" and self.has_moved and self.obj.root.checkbox_showboxes.active and not self.cancellation:     # If 'Encapsulate' mode is selected, mouse has moved and no cancellation
                    
                    buttons_to_encapsulate_coord = []
                    buttons_to_encapsulate = []
                    
                    # Detect buttons to encapsulate
                    for button in list(dico.keys()):
                        button_LB = button.pos
                        button_RT = (button.pos[0]+button.size[0], button.pos[1]+button.size[1])
                        if is_inside([transfo_points_LB, transfo_points_RT], [button_LB, button_RT]):
                            buttons_to_encapsulate_coord += [button_LB, button_RT]
                            buttons_to_encapsulate.append(button)
                    
                    # If there are buttons buttons to encapsulate, effectively create the corresponding button
                    if buttons_to_encapsulate_coord:
                        new_box_LB = give_bottom_left_corner(buttons_to_encapsulate_coord)
                        new_box_LB = (new_box_LB[0] - 2, new_box_LB[1] - 2)                 # -2 and +2 in order to discern that there is a bigger box aroung the boxes to encapsulate
                        new_box_RT = give_top_right_corner(buttons_to_encapsulate_coord)
                        new_box_RT = (new_box_RT[0] + 2, new_box_RT[1] + 2)
                        
                        button = manager.new_button(new_box_LB, new_box_RT)     
                        undo_delete.append(button)
                        
                        dico[button] = Box(manager.button_coord_to_box_coord(button), 100, "new token")
                        for encased_button in buttons_to_encapsulate:
                            box = dico[encased_button]
                            del dico[encased_button]
                            dico[encased_button] = box
                        
                        manager.my_zoom.add_widget(button)
                        manager.tag(button, during_box_creation=True)
#                        manager.my_zoom.canvas.add(outline)
                        
                        # Draw the smaller buttons over the new button (this allows user to click on them) 
                        for encased_button in buttons_to_encapsulate:
                            manager.my_zoom.remove_widget(encased_button)
                            manager.my_zoom.add_widget(encased_button)
                        
                        if manager.tokens_already_loaded:
                            new_pos = manager.my_zoom.transform_to_parent((button.pos[0], button.pos[1]+button.size[1]))
                            token = Token(new_pos, dico[button].token)
                            manager.tokens_to_buttons[token] = button
                            manager.buttons_to_tokens[button] = token
                        
                        if manager.checkbox_showtokens.active:
                            manager.my_box.add_widget(token)
                            
                    manager.canceller.update(undo_delete, undo_create, undo_tag, undo_labels, [])
                # REMOVE SEVERAL BOXES
                elif manager.cursor_tool == "Remove" and self.has_moved and self.obj.root.checkbox_showboxes.active and not self.cancellation:          # If 'Remove' mode is selected, mouse has moved and no cancellation
                    
                    # Remove all buttons that are inside the rectangle
                    for button in list(dico.keys()):
                        button_LB = button.pos
                        button_RT = (button.pos[0]+button.size[0], button.pos[1]+button.size[1])
                        if is_inside([transfo_points_LB, transfo_points_RT], [button_LB, button_RT]):
                            undo_create[button] = dico[button]
                            manager.remove(button, multiple=True)
                            
                    manager.canceller.update(undo_delete, undo_create, undo_tag, undo_labels, [])
                
                self.points = []    # Reset the rectangle position (the four points)
                
        return super(LinePlayground, self).on_touch_up(touch)
    
    

    
    
    

