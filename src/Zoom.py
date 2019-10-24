from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty

        
class Zoom(ScatterLayout):
    move_lock = False
    scale_lock_left = False
    scale_lock_right = False
    scale_lock_top = False
    scale_lock_bottom = False
    auto_bring_to_front = False
 
    initial_pos = None
    
    obj = ObjectProperty(None)
    
    
    def focus(self):
        self.scale = 1
        self.pos = self.initial_pos
        if self.obj.root.checkbox_showtokens.active:
            self.update_tokens()
    
    def update_tokens(self):
        for token in self.obj.root.tokens_to_buttons:
            the_button = self.obj.root.tokens_to_buttons[token]
            new_pos = self.transform_to_parent((the_button.pos[0], the_button.pos[1]+the_button.size[1]))
            token.pos = new_pos
    
    def update_BIO(self):
        for bio_letter in self.obj.root.bio_letters:
            the_button = self.obj.root.bio_letters[bio_letter]
            new_pos = self.transform_to_parent(the_button.pos)
            bio_letter.pos = new_pos
            size_pos = self.transform_to_parent((the_button.pos[0]+the_button.size[0], the_button.pos[1]+the_button.size[1]))
            bio_letter.size = (size_pos[0]-new_pos[0], size_pos[1]-new_pos[1])
            
    def on_touch_move(self, touch):
        if touch.button != 'left' and self.obj.root.dataset:
            super(Zoom, self).on_touch_move(touch)
            if self.obj.root.checkbox_showtokens.active:
                self.update_tokens()
            if not self.obj.root.accordion_BIO.collapse:
                self.update_BIO()
    
    def on_touch_up(self, touch):
        if self.obj.root.dataset:
            self.move_lock = False
            self.scale_lock_left = False
            self.scale_lock_right = False
            self.scale_lock_top = False
            self.scale_lock_bottom = False
            if touch.grab_current is self:
                touch.ungrab(self)
                x = self.pos[0] / 10
                x = round(x, 0)
                x = x * 10
                y = self.pos[1] / 10
                y = round(y, 0)
                y = y * 10
                self.pos = x, y
                
                if self.obj.root.checkbox_showtokens.active:
                    self.update_tokens()
                if not self.obj.root.accordion_BIO.collapse:
                    self.update_BIO()
                
                return super(Zoom, self).on_touch_up(touch)

    def transform_to_local(self, point):
        return super(Zoom, self).to_local(point[0], point[1])
    
    def transform_to_parent(self, point):
        return super(Zoom, self).to_parent(point[0], point[1])
        

    def on_touch_down(self, touch):
        
        
        
        if self.obj.root.dataset:
            x, y = touch.x, touch.y
            self.prev_x = touch.x
            self.prev_y = touch.y
    
            if touch.is_mouse_scrolling:
                
                (x_before, y_before) = self.transform_to_local(touch.pos) # Take the position under the pointer
                
                ## zoom
                if touch.button == 'scrolldown':
                    ## zoom in
                    if self.scale < 10:
                        self.scale = self.scale * 1.1
                            
                elif touch.button == 'scrollup':
                    ## zoom out
                    if self.scale > 0.8:                # avant c'était à 1
                        self.scale = self.scale * 0.9
                        
                (x_before, y_before) = self.transform_to_parent((x_before, y_before))   # Update where it is now
                (x_after, y_after) = touch.pos                                          # Take the new position under the pointer
                dx, dy = x_after-x_before, y_after-y_before                             # Calculate translation do to
                self.center = (self.center[0]+dx, self.center[1]+dy)                    # Apply the translation
                
    
            # if the touch isnt on the widget we do nothing
            if not self.do_collide_after_children:
                if not self.collide_point(x, y):
                    return False
    
            if touch.button != 'right':
                # let the child widgets handle the event if they want
                touch.push()
                touch.apply_transform_2d(self.to_local)
                if super(Scatter, self).on_touch_down(touch):
                    # ensure children don't have to do it themselves
                    if 'multitouch_sim' in touch.profile:
                        touch.multitouch_sim = True
                    touch.pop()
                    self._bring_to_front(touch)
                    return True
                touch.pop()
        
                # if our child didn't do anything, and if we don't have any active
                # interaction control, then don't accept the touch.
                if not self.do_translation_x and \
                        not self.do_translation_y and \
                        not self.do_rotation and \
                        not self.do_scale:
                    return False
        
            if self.do_collide_after_children:
                if not self.collide_point(x, y):
                    return False
    
            if 'multitouch_sim' in touch.profile:
                touch.multitouch_sim = True
            # grab the touch so we get all it later move events for sure
            self._bring_to_front(touch)
            touch.grab(self)
            self._touches.append(touch)
            self._last_touch_pos[touch] = touch.pos
            
            
    
            return True
