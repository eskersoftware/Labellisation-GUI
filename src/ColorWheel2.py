from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, BoundedNumericProperty,
                             ListProperty, ObjectProperty,
                             ReferenceListProperty, StringProperty,
                             AliasProperty)
from kivy.clock import Clock
from kivy.graphics import Mesh, InstructionGroup, Color
from kivy.utils import get_color_from_hex, get_hex_from_color
from math import cos, sin, pi, sqrt, atan
from colorsys import rgb_to_hsv, hsv_to_rgb
from threading import Timer
from kivy.lang import Builder


'''
Color Picker
============

.. versionadded:: 1.7.0

.. warning::

    This widget is experimental. Its use and API can change at any time until
    this warning is removed.

.. image:: images/colorpicker.png
    :align: right

The ColorPicker widget allows a user to select a color from a chromatic
wheel where pinch and zoom can be used to change the wheel's saturation.
Sliders and TextInputs are also provided for entering the RGBA/HSV/HEX values
directly.

Usage::

    clr_picker = ColorPicker()
    parent.add_widget(clr_picker)

    # To monitor changes, we can bind to color property changes
    def on_color(instance, value):
        print "RGBA = ", str(value)  #  or instance.color
        print "HSV = ", str(instance.hsv)
        print "HEX = ", str(instance.hex_color)

    clr_picker.bind(color=on_color)


'''



def distance(pt1, pt2):
    return sqrt((pt1[0] - pt2[0]) ** 2. + (pt1[1] - pt2[1]) ** 2.)


def polar_to_rect(origin, r, theta):
    return origin[0] + r * cos(theta), origin[1] + r * sin(theta)


def rect_to_polar(origin, x, y):
    if x == origin[0]:
        if y == origin[1]:
            return (0, 0)
        elif y > origin[1]:
            return (y - origin[1], pi / 2.)
        else:
            return (origin[1] - y, 3 * pi / 2.)
    t = atan(float((y - origin[1])) / (x - origin[0]))
    if x - origin[0] < 0:
        t += pi

    if t < 0:
        t += 2 * pi

    return (distance((x, y), origin), t)




Builder.load_string("""  
<ColorWheel2>:
    _origin: self.center
    _radius: 0.45 * min(self.size)
""")  

class ColorWheel2(Widget):
    '''Chromatic wheel for the ColorPicker.

    .. versionchanged:: 1.7.1
        `font_size`, `font_name` and `foreground_color` have been removed. The
        sizing is now the same as others widget, based on 'sp'. Orientation is
        also automatically determined according to the width/height ratio.

    '''

    r = BoundedNumericProperty(0, min=0, max=1)
    '''The Red value of the color currently selected.

    :attr:`r` is a :class:`~kivy.properties.BoundedNumericProperty` and
    can be a value from 0 to 1. It defaults to 0.
    '''

    g = BoundedNumericProperty(0, min=0, max=1)
    '''The Green value of the color currently selected.

    :attr:`g` is a :class:`~kivy.properties.BoundedNumericProperty`
    and can be a value from 0 to 1.
    '''

    b = BoundedNumericProperty(0, min=0, max=1)
    '''The Blue value of the color currently selected.

    :attr:`b` is a :class:`~kivy.properties.BoundedNumericProperty` and
    can be a value from 0 to 1.
    '''

    a = BoundedNumericProperty(0, min=0, max=1)
    '''The Alpha value of the color currently selected.

    :attr:`a` is a :class:`~kivy.properties.BoundedNumericProperty` and
    can be a value from 0 to 1.
    '''

    color = ReferenceListProperty(r, g, b, a)
    '''The holds the color currently selected.

    :attr:`color` is a :class:`~kivy.properties.ReferenceListProperty` and
    contains a list of `r`, `g`, `b`, `a` values.
    '''

    _origin = ListProperty((100, 100))
    _radius = NumericProperty(100)

    _piece_divisions = NumericProperty(3)
    _pieces_of_pie = NumericProperty(12)

    _inertia_slowdown = 1.25
    _inertia_cutoff = .25

    _num_touches = 0

    _hsv = ListProperty([1, 1, 1, 0])
    
    current_arc = None
    
    
    


    
    

    def __init__(self, **kwargs):
        super(ColorWheel2, self).__init__(**kwargs)

        pdv = self._piece_divisions
        self.sv_s = [(float(x) / pdv, 1) for x in range(pdv)] + [
            (1, float(y) / pdv) for y in reversed(range(pdv))]
        
        

    def on__origin(self, instance, value):
        self.init_wheel(None)

    def on__radius(self, instance, value):
        self.init_wheel(None)

    def init_wheel(self, dt):
        # initialize list to hold all meshes
        self.canvas.clear()
        self.arcs = []
        self.sv_idx = 0
        pdv = self._piece_divisions
        ppie = self._pieces_of_pie

        for r in range(pdv):
            for t in range(ppie):
                self.arcs.append(
                    _ColorArc(
                        self._radius * (float(r) / float(pdv)),
                        self._radius * (float(r + 1) / float(pdv)),
                        2 * pi * (float(t) / float(ppie)),
                        2 * pi * (float(t + 1) / float(ppie)),
                        origin=self._origin,
                        color=(float(t) / ppie,
                               self.sv_s[self.sv_idx + r][0],
                               self.sv_s[self.sv_idx + r][1],
                               1)))

                self.canvas.add(self.arcs[-1])


    def on_touch_down(self, touch):
        r = self._get_touch_r(touch.pos)
        if r > self._radius:
            return False

        # code is still set up to allow pinch to zoom, but this is
        # disabled for now since it was fiddly with small wheels.
        # Comment out these lines and  adjust on_touch_move to reenable
        # this.
        if self._num_touches != 0:
            return False

        touch.grab(self)
        self._num_touches += 1
        touch.ud['anchor_r'] = r
        touch.ud['orig_sv_idx'] = self.sv_idx
        touch.ud['orig_time'] = Clock.get_time()

    def init_disabled_arcs(self, rgb_list):
        for rgb in rgb_list:
            for arc in self.arcs:
                if [int(255*val) for val in rgb] == [int(255*val) for val in arc.rgb]:
                    self.current_arc = arc
                    self.disable_arc_now()

    def disable_arc(self):
        t = Timer(0.5, self.disable_arc_now)
        t.start()
        
    def disable_arc_now(self):
        if self.current_arc.r_min:
            old_arc = self.current_arc
            new_arc = _ColorArc(old_arc.r_min, old_arc.r_max, old_arc.theta_min, old_arc.theta_max, color=(.2, .2, .2, 1), origin=old_arc.origin)
            self.arcs[self.arcs.index(self.current_arc)] = new_arc
            self.canvas.clear()
            for arc in self.arcs:
                self.canvas.add(arc)
            self.color = (1, 1, 1, 1)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        self._num_touches -= 1
        
        r, theta = rect_to_polar(self._origin, *touch.pos)
        # if touch up is outside the wheel, ignore
        if r >= self._radius:
            return
        # compute which ColorArc is being touched (they aren't
        # widgets so we don't get collide_point) and set
        # _hsv based on the selected ColorArc
        piece = int((theta / (2 * pi)) * self._pieces_of_pie)
        division = int((r / self._radius) * self._piece_divisions)
        hsva = list(
            self.arcs[self._pieces_of_pie * division + piece].color)
        self.current_arc = self.arcs[self._pieces_of_pie * division + piece]
        if hsva != [.2, .2, .2, 1]:
            self.color = list(hsv_to_rgb(*hsva[:3])) + hsva[-1:]
            


    def _get_touch_r(self, pos):
        return distance(pos, self._origin)



class _ColorArc(InstructionGroup):
    def __init__(self, r_min, r_max, theta_min, theta_max,
                 color=(0, 0, 1, 1), origin=(0, 0), **kwargs):
        super(_ColorArc, self).__init__(**kwargs)
        self.origin = origin
        self.r_min = r_min
        self.r_max = r_max
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.color = color
        self.color_instr = Color(*color, mode='hsv')
        self.add(self.color_instr)
        self.mesh = self.get_mesh()
        self.add(self.mesh)
        self.rgb = list(hsv_to_rgb(*list(self.color[:3])))
        self.index = -1

    def __str__(self):
        return "r_min: %s r_max: %s theta_min: %s theta_max: %s color: %s" % (
            self.r_min, self.r_max, self.theta_min, self.theta_max, self.color
        )

    def get_mesh(self):
        v = []
        # first calculate the distance between endpoints of the inner
        # arc, so we know how many steps to use when calculating
        # vertices
        end_point_inner = polar_to_rect(
            self.origin, self.r_min, self.theta_max)

        d_inner = d_outer = 3.
        theta_step_inner = (self.theta_max - self.theta_min) / d_inner

        end_point_outer = polar_to_rect(
            self.origin, self.r_max, self.theta_max)

        if self.r_min == 0:
            theta_step_outer = (self.theta_max - self.theta_min) / d_outer
            for x in range(int(d_outer)):
                v += (polar_to_rect(self.origin, 0, 0) * 2)
                v += (polar_to_rect(
                    self.origin, self.r_max,
                    self.theta_min + x * theta_step_outer) * 2)
        else:
            for x in range(int(d_inner + 2)):
                v += (polar_to_rect(
                    self.origin, self.r_min - 1,
                    self.theta_min + x * theta_step_inner) * 2)
                v += (polar_to_rect(
                    self.origin, self.r_max + 1,
                    self.theta_min + x * theta_step_inner) * 2)

        v += (end_point_inner * 2)
        v += (end_point_outer * 2)

        return Mesh(vertices=v, indices=range(int(len(v) / 4)),
                    mode='triangle_strip')


Builder.load_string("""  
<ColorPicker2>:
    foreground_color: (1, 1, 1, 1) if self.hsv[2] * root.color[3] < .5 else (0, 0, 0, 1)
	
    wheel: wheel
    
	BoxLayout:
        orientation: 'vertical' if root.width < root.height else 'horizontal'
        spacing: '5sp'
		
		canvas:
			Color:
				rgba: root.color
			Rectangle:
				pos: self.pos
				size: self.size
				
		ColorWheel2:
			id: wheel
			color: root.color
			on_color: root.set_color(args[1][:3])

""")  

class ColorPicker2(RelativeLayout):
    '''
    See module documentation.
    '''

    font_name = StringProperty('data/fonts/RobotoMono-Regular.ttf')
    '''Specifies the font used on the ColorPicker.

    :attr:`font_name` is a :class:`~kivy.properties.StringProperty` and
    defaults to 'data/fonts/RobotoMono-Regular.ttf'.
    '''

    color = ListProperty((1, 1, 1, 1))
    '''The :attr:`color` holds the color currently selected in rgba format.

    :attr:`color` is a :class:`~kivy.properties.ListProperty` and defaults to
    (1, 1, 1, 1).
    '''

    def _get_hsv(self):
        return rgb_to_hsv(*self.color[:3])

    def _set_hsv(self, value):
        if self._updating_clr:
            return
        self.set_color(value)

    hsv = AliasProperty(_get_hsv, _set_hsv, bind=('color', ))
    '''The :attr:`hsv` holds the color currently selected in hsv format.

    :attr:`hsv` is a :class:`~kivy.properties.ListProperty` and defaults to
    (1, 1, 1).
    '''
    def _get_hex(self):
        return get_hex_from_color(self.color)

    def _set_hex(self, value):
        if self._updating_clr:
            return
        self.set_color(get_color_from_hex(value)[:4])

    hex_color = AliasProperty(_get_hex, _set_hex, bind=('color',), cache=True)
    '''The :attr:`hex_color` holds the currently selected color in hex.

    :attr:`hex_color` is an :class:`~kivy.properties.AliasProperty` and
    defaults to `#ffffffff`.
    '''

    wheel = ObjectProperty(None)
    '''The :attr:`wheel` holds the color wheel.

    :attr:`wheel` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.
    '''

    _update_clr_ev = _update_hex_ev = None

    # now used only internally.
    foreground_color = ListProperty((1, 1, 1, 1))




    def set_color(self, color):
        self._updating_clr = True
        if len(color) == 3:
            self.color[:3] = color
        else:
            self.color = color
        self._updating_clr = False

    def __init__(self, **kwargs):
        self._updating_clr = False
        super(ColorPicker2, self).__init__(**kwargs)