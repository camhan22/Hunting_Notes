from ttkbootstrap import Frame, Label, Button, Entry, Style
import treelib

class SidebarWidget(treelib.Node):
    """
    Class to handle a widget in the tree
    
    :param name: The name to give the widget
    :type name: str
    :widget_type: The type of widget to make
    :type widget_type: type
    :parent_node: The node that should be the parent of this one
    :type parent_node: treelib.Node or ttkbootstrap.Window or ttkbootstrap.Frame or tkinter.Tk or tkinter.Frame
    :param widget_properties: Any properties that the widget should have (Defaults will be set if they don't exist)
    :type widget_properties: dict
    :param widget_place_properties: Any properties that would place the widget in a specific manner
    :type widget_place_properties: dict
    """
    def __init__(self, name, widget_type, parent_node, widget_properties:dict={}, widget_place_properties:dict={}):
        super().__init__(name, name)
        self.properties = widget_properties
        self.placeProperties = widget_place_properties
        #Check if we are adding the root node since the parent_node won't be a treelib node but the root window
        if not isinstance(parent_node, treelib.Node):
            self.widget = widget_type(parent_node, **self.properties)
        else:
            self.check_load_defaults(widget_type)
            #Check if we are adding a menu tab and get the command off it
            if "command" in self.properties and "Tab" in name:
                self.labelCommand = self.properties["command"]
                self.properties.pop("command")
            self.widget = widget_type(parent_node.widget, **self.properties)
            self.bind_labels()

    def set_widget_propery(self, **kwargs):
        """
        Sets properties of the widget
        """
        for prop in kwargs:
            if prop in self.properties:
                self.properties[prop] = kwargs[prop]
            else:
                self.properties.update({prop:kwargs[prop]})
        self.widget.configure(**self.properties) #Update the properties of the widget

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
        widget = widget_type()
        if isinstance(widget, (Frame, Label, Button, Entry)):
            if not "relwidth" in self.placeProperties:
                self.placeProperties.update({"relwidth":1.0})
            if not "takefocus" in self.properties:
                self.properties.update({"takefocus":False})
                
        if isinstance(widget, Label):
            if not "Tab" in self.identifier:
                return
            if not "text" in self.properties:
                self.properties.update({"text":self.tag.replace("Tab","")})
            if not "anchor" in self.properties:
                self.properties.update({"anchor":"center"})
            if not "relief" in self.properties:
                self.properties.update({"relief":"ridge"})
            if not "takefocus" in self.properties:
                self.properties.update({"takefocus":False})
            if not "style" in self.properties:
                Style().configure("heading.Inverse.TLabel", font=("helvetica","12","bold"))
                self.properties.update({"style":"heading.Inverse.TLabel"})
        
    def bind_labels(self):
        """
        If the widget is a tab, then we need to bind a command to open the widget frame associated with it when it is clicked
        """
        if hasattr(self,"labelCommand"):
            self.widget.bind("<Button-1>", self.labelCommand)




