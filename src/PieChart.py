from kivy.app import App
from kivy.graphics import Ellipse, Color, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from random import random

class PieChart(GridLayout):
    """
    A piechart data representation composed of a pie and a legend.
    """
    
    def __init__(self, in_data={"None": (100, [1, 1, 1, 1])}, legend_enable=True, **kwargs):
        super(PieChart, self).__init__(**kwargs)            

        self.data = {}  # Represent in_data with percentage and color
        self.cols = 2   # Number of columns : one for the pie and (potentially) one for the legend
        self.rows = 1   # Number of rows

        for key, value in in_data.items():                                      # For each category
            
            # If the color is not mentionned
            if type(value) is int:  
                percentage = (value / float(sum(in_data.values())) * 100)       # Calcul percentage
                color = [random(), random(), random(), 1]                       # Choose a random color
                self.data[key] = [value, percentage, color]                     # Add it to the data

            # If the color is mentionned
            elif type(value) is tuple:
                percentage = (value[0] / float(sum([val[0] for val in in_data.values()])) * 100)    # Calcul percentage
                color = value[1]                                                                    # Set the chosen color
                self.data[key] = [value[0], percentage, color]                                      # Add it to the data

        self.pie = Pie(self.data) # Instanciate the pie
        self.add_widget(self.pie)           # Add it

        # If legend is required
        if legend_enable:                                   
            self.legend = Legend(self.data)   # Instanciate the legend
            self.add_widget(self.legend)      # Add it    


class Legend(BoxLayout):
    """
    Legend gather all LegendItem in order to generate the legend.
    """
    
    def __init__(self, data, **kwargs):
        super(Legend, self).__init__(**kwargs)

        self.spacing = 5                    # Add a space between each LegendItems
        self.orientation = "vertical"       # A vertical BoxLayout

        for key, value in data.items():                                                           # For each category          
            self.legend = LegendItem(name=key, nb=value[0], percentage=value[1], color=value[2])  # Create the corresponding LegendItem
            self.add_widget(self.legend)                                                          # Add it to the legend


class LegendItem(BoxLayout):
    """
    Correspond to legend of one category.
    """
    
    def __init__(self, name, nb, percentage, color, **kwargs):
        super(LegendItem, self).__init__(**kwargs)
             
        # Add the color box
        with self.canvas:   
            Color(*color)
            self.rect = Rectangle(size=(20, 20))
        self.label = Label(text=str(nb) + str(" (%.2f" % percentage + "%) - ") + name)  # Create the label
        self.add_widget(self.label)                                                     # Add it
        
        self.bind(size=self._update_rect, pos=self._update_rect)    # Update color box and label positions

    def _update_rect(self, instance, value):
        """
        Update color box and label positions.
        """
        self.rect.pos = (instance.pos[0] + instance.size[0]/8 - self.rect.size[0]/2, instance.pos[1] + instance.size[1]/2 - self.rect.size[1]/2)    # The color box position
        self.label.pos = (instance.pos[0] + instance.size[0]/4, instance.pos[1] + instance.size[1]/2 - self.label.size[1]/2)                        # The label position



class Pie(BoxLayout):
    """
    The pie itself.
    """
    
    def __init__(self, data, **kwargs):
        super(Pie, self).__init__(**kwargs)
        
        angle_start = 0                 # Actually it is pi/2
        count = 0                       # Index of the current ellipse
        self.temp = []                  # In order to store the ellipses that form the pie
        
        for key, value in data.items():                     # For each category
            percentage = value[1]                           # Get the percentage
            angle_end = angle_start + 3.6 * percentage      # Prepare the corresponding angle
            color = value[2]                                # Get the color
            self.temp.append(Ellipse(angle_start=angle_start, angle_end=angle_end))      # Store the current ellipse
            self.canvas.add(Color(*color))                                                          # Add the corresponding color
            self.canvas.add(self.temp[count])                                                       # And the current ellipse
            angle_start = angle_end     # Update the current angle position
            count += 1                  # Incremente the index of the current ellipe

        self.bind(size=self._update_temp, pos=self._update_temp)    # Update the ellipses

    def _update_temp(self, instance, value):
        """
        Update the ellipses.
        """
        for i in self.temp: # For each ellipses
            i.size = (0.8*min(self.size), 0.8*min(self.size))
            i.pos = (instance.pos[0] + instance.size[0]/2 - i.size[0]/2, instance.pos[1] + instance.size[1]/2 - i.size[1]/2) # The ellipse position
