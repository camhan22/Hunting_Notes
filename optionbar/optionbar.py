import treelib
from optionbar.optionbarwidget import OptionbarWidget
from ttkbootstrap import Label, Button, Combobox, Frame, Checkbutton
from tkinter import PhotoImage

"""Class to add a option bar to a window"""
class OptionBar():
    """
    Initialize the option bar
    
    :param root: The root window the sidebar should be in
    :type root: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param side: The side of the root window the sidebar should be on
    :type side: str (left or right)
    :param animate: Whether to animate the sidebar expansion and collapse (Defaults to False)
    :type animate: bool
    :param frame_properties: Any properties to give to the option bar frame
    :type frame_properties: dict
    :param frame_place_properties: Any place properties to give to the option bar frame
    :type frame_place_properties: dict
    :param expand_button_properties: Any properties to give to the expand button
    :type expand_button_properties: dict
    :param expand_button_place_properties: Any place properties to give to the expand button
    :type expand_button_place_properties: dict
    """
    def __init__(self, root, side: str="left", animate: bool = False, 
                 frame_properties:dict={}, frame_place_properties:dict={},
                 expand_button_properties:dict={}, expand_button_place_properties:dict={}):
        self.root = root
        self.optionbarExpanded = False
        self.currentSize = 0
        self.optionbarMaxWidth = frame_place_properties["relwidth"]
        self.optionbarProperties = frame_properties.copy()
        self.optionbarPlaceProperties = frame_place_properties.copy()
        self.expandButtonProperties = expand_button_properties.copy()
        self.expandButtonPlaceProperties = expand_button_place_properties.copy()
        self.isAnimated = animate
        if side == "left":
            self.anchor = "nw"
            self.optionbarXStart = 0
        elif side == "right":
            self.anchor = "ne"
            self.optionbarXStart = 1
        self.changeIncrement = 0.2 #Increment by 0.2% of the range for each step
        
        if "image" in self.expandButtonProperties:
            if "zoom" in self.expandButtonProperties:
                zoom = self.expandButtonProperties["zoom"]
                self.expandButtonProperties.pop("zoom")
                if zoom >= 1:
                    self.expandButtonProperties["image"] = PhotoImage(file=self.expandButtonProperties["image"]).zoom(int(zoom))
                else:
                    self.expandButtonProperties["image"] = PhotoImage(file=self.expandButtonProperties["image"]).subsample(int(1/zoom))
            else:
                self.expandButtonProperties["image"] = PhotoImage(file=self.expandButtonProperties["image"])
        self.expandButton = Button(self.root, command=self.open_close, **self.expandButtonProperties, takefocus=False)
        if not "relwidth" in self.expandButtonPlaceProperties:
            self.expandButtonPlaceProperties.update({"relwidth":0.05})
        if not "relheight" in self.expandButtonPlaceProperties:
            self.expandButtonPlaceProperties.update({"relheight":0.05})
        self.expandButtonPlaceProperties.update({"relx":self.optionbarXStart-self.expandButtonPlaceProperties["relx"], 
                                               "anchor":self.anchor})
        self.expandButton.place(**self.expandButtonPlaceProperties)
        
        self.optionbarPlaceProperties.update({"rely":self.expandButtonPlaceProperties["rely"]+self.expandButtonPlaceProperties["relheight"]})
        self.optionbarPlaceProperties.update({"relx":self.expandButtonPlaceProperties["relx"]})

        #Create sidebar frame
        self.widgetTree = treelib.Tree()
        rootNode = OptionbarWidget("Optionbar", Frame, self.root,
                                    place_properties={"relwidth":self.currentSize, 
                                                             "relheight":self.optionbarPlaceProperties["relheight"], 
                                                             "relx": self.optionbarPlaceProperties["relx"], 
                                                             "anchor":self.anchor, 
                                                             "rely":self.optionbarPlaceProperties["rely"]})
        self.widgetTree.add_node(rootNode)

    """
    Opens the option bar if it isn't and closes it if it is
    """
    def open_close(self):
        if not self.optionbarExpanded:
            self.expand()
        else:
            self.contract()
    """
    Expands the sidebar widget onto the screen
    If the animate flag is True, then it will also animate the sidebar
    """
    def expand(self):  
        if not self.isAnimated:
            self.currentSize = self.optionbarMaxWidth
            self.optionbarExpanded = True
        else:
            if self.currentSize < self.optionbarMaxWidth:
                self.currentSize = self.currentSize + self.changeIncrement*self.optionbarMaxWidth
                self.root.after(10, self.expand)
            else:
                self.optionbarExpanded = True
        self.widgetTree["Optionbar"].place(True, relwidth=self.currentSize)
        self.root.update()
        self.root.update_idletasks()
        if self.optionbarExpanded:
            self.fill()

    """
    Contracts the sidebar widget from the screen
    Also animates the widegt contraction if animate flag is True
    """
    def contract(self):
        if self.isAnimated:
            if self.currentSize > 0:
                self.currentSize = self.currentSize - self.changeIncrement*self.optionbarMaxWidth
                self.widgetTree["Optionbar"].data.place(True, relwidth=self.currentSize)
                self.root.after(10, self.contract)
            else:
                self.optionbarExpanded = False
                self.widgetTree["Optionbar"].data.place_forget()      
            self.root.update()
            self.root.update_idletasks()
        else:
            self.currentSize = 0
            self.optionbarExpanded = False
            self.widgetTree["Optionbar"].place_forget()
            self.root.update()
            self.root.update_idletasks()
            
    """
    Adds a widget to the option bar
    
    :param name: The name to give the widget
    :type name: str
    :param widget_type: The type of widget to add
    :type widget_type: type
    :param parent_node: The parent of this node
    :type parent_node: treelib.Node
    :param properties: Any key word arguments to give the widget
    :type properties: dict
    :param place_properties: Any keyword arguments to place the widget
    :type place_properties: dict
    """
    def add_widget(self,name, widget_type, parent_node=None, properties:dict={}, place_properties:dict={}):
        if parent_node is None:
            parent_node = self.widgetTree["Optionbar"]
        newNode = OptionbarWidget(name, widget_type, parent_node, 
                                  properties=properties, place_properties=place_properties)
        self.widgetTree.add_node(newNode, parent_node)
        return newNode
    
    """
    Adds a button to a specific menu tab
    
    :param name: The text to display on the button
    :type name: str
    :param button_command: The command that should get called when the button is pressed
    :type button_command: Callable
    :param menu_name: The name of the menu to add the button to (Defaults to the root of the sidebar)
    :type menu_name: str
    :param properties: Any keyword arguments to pass to the button
    :type properties: Any keyword arguments to pass to place the button in the sidebar
    """       
    def add_menu_button(self, text, button_command, menu_name:str="Optionbar", properties:dict={}, place_properties:dict={}):
        prop = properties.copy()
        properties.update({"command":button_command, "text":text,"style":"TButton"})
        self.add_widget(text, Button, menu_name, properties=prop, place_properties=place_properties.copy())
        
    """
    Adds a combo box to a menu tab
    
    :param name: The name to give to the combobox
    :type name: str
    :param combo_values: The list of values to give to the combobox
    :type combo_values: list
    :param combo_default: The default value to give to the combo box (Defaults to "")
    :type combo_default: str
    :param combo_command: The function to call when the combobox changes value
    :type combo_command: Callable
    :param combo_variable: The variable to link to the combobox
    :type combo_variable: Tk.IntVar or Tk.BooleanVar
    """
    def add_combobox(self, name, combo_values, combo_default, combo_command, combo_variable, place_properties:dict={}):
        place_properties = place_properties.copy()
        comboFrameNode = self.add_widget(name, Frame, place_properties=place_properties)
        self.add_widget(name+"Text", Label, comboFrameNode, properties={"text":name, "anchor":"center","style":"TLabel"}, place_properties={"relwidth":0.5, "relheight":1.0, "relx":0, "rely":0})
        self.add_widget(name+"Combobox", Combobox, comboFrameNode, properties={"state":"readonly","values":combo_values, "textvariable":combo_variable},place_properties={"relwidth":0.5, "relheight":1.0, "relx":0.5, "rely":0})
        self.widgetTree[name+"Combobox"].widget.set(combo_default)
        self.widgetTree[name+"Combobox"].widget.bind("<<ComboboxSelected>>", combo_command)
        self.place_children(comboFrameNode)
       
    """
    Adds a checkbutton to the option bar
    
    :param name: The name to give the checkbutton
    :type name: str
    :param button_command: The command to call when the checkbutton is changed
    :type button_command: Callable
    :param properties: Any key word arguments to give the checkbutton
    :type properties: dict
    :param place_properties: Any keyword arguments to place the checkbutton
    :type place_properties: dict
    """
    def add_checkbutton(self, name, button_command, properties:dict={}, place_properties:dict={}):
        prop = properties.copy()
        prop.update({"command":button_command, "text":name})
        self.add_widget(name, Checkbutton, properties=prop, place_properties=place_properties.copy())
    """
    Fills in the sidebar frame with the frames placed into it (Only runs once when it first gets expanded)
    """
    def fill(self):
        relTotal = 0
        for child in self.widgetTree.children("Optionbar"):
            child.place(rely=relTotal)
            relTotal += child.placeProperties["relheight"]

    """
    places any children of the input node
    
    :param node: The node to place the children of
    :type node: treelib.Node
    """
    def place_children(self, node):
        children = self.widgetTree.children(node.identifier)
        childRelTotal = 0
        if children == []:
            return
        
        for child in children:
            if "rely" in child.placeProperties:
                child.place()
            else:
                child.place(rely=childRelTotal)
            childRelTotal += child.placeProperties["relheight"]








