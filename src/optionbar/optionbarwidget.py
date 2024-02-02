from ttkbootstrap import Frame, Label, Button, Entry
import treelib

class OptionbarWidget(treelib.Node):
    """
    Class to handle a widget in the tree
    
    :param name: The name to give the widget
    :type name: str
    :widget_type: The type of widget to make
    :type widget_type: type
    :parent_node: The node that should be the parent of this one
    :type parent_node: treelib.Node or ttkbootstrap.Window or ttkbootstrap.Frame or tkinter.Tk or tkinter.Frame
    :param properties: Any properties that the widget should have (Defaults will be set if they don't exist)
    :type properties: dict
    :param place_properties: Any properties that would place the widget in a specific manner
    :type place_properties: dict
    """
    def __init__(self, name, widget_type, parent_node, properties:dict={}, place_properties:dict={}):
        super().__init__(name, name)
        self.properties = properties.copy()
        self.placeProperties = place_properties.copy()
        if not isinstance(parent_node, treelib.Node):
            self.placeOrder = 0
            self.widget = widget_type(parent_node, **self.properties)
        else:
            self.check_load_defaults(widget_type)
            self.widget = widget_type(parent_node.widget, **self.properties)
                  
    def set_widget_propery(self, **kwargs):
        """
        Sets properties of the widget
        """ 
        for prop in kwargs:
            if prop in self.properties:
                self.properties[prop] = kwargs[prop]
            else:
                self.properties.update({prop:kwargs[prop]})
        self.widget.configure(**self.properties)
        
    def set_widget_place_property(self, **kwargs):
        """
        Sets place properties of the widget
        """
        for prop in kwargs:
            if prop in self.placeProperties:
                self.placeProperties[prop] = kwargs[prop]
            else:
                self.placeProperties.update({prop:kwargs[prop]})
        self.widget.place(**self.placeProperties)
            
    def delete_widget_place_property(self, *args):
        """
        Deletes a place property that is set within the widget
        """  
        for arg in args:
            if arg in self.placeProperties:
                self.placeProperties.pop(arg)

    def place(self, save: bool=False, **kwargs):
        """
        Places the widget
    
        :param save: Whether to save any kwargs to the widget or just set them but leave the place properties alone
        :type save: bool
        """
        if not kwargs == {} and save:
            self.set_widget_place_property(**kwargs)
        else:
            self.widget.place(**kwargs, **self.placeProperties)
            
    def place_forget(self):
        """
        Forgets where a widget is placed on the screen
        """
        self.widget.place_forget()

    def check_load_defaults(self, widget_type):
        """
        Checks to see if any of the defaults need to be placed inside the widget properties
    
        :param widget_type: The type of widget to load defaults for
        :type widget_type: type
        """
        if isinstance(widget_type(), (Frame, Label, Button, Entry)):
            if not "relwidth" in self.placeProperties:
                self.placeProperties.update({"relwidth":1.0})
                
            if not "takefocus" in self.properties:
                self.properties.update({"takefocus":False})








