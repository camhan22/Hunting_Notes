import treelib
from sidebar.sidebarwidget import SidebarWidget
from ttkbootstrap import Label, Button, Combobox, Frame, Entry

class Sidebar():
    """
    Class to handle the functions of the sidebar
    
    :param root: The root window the sidebar should be in
    :type root: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param min_rel_detect: The minimum relative width of the root display the sidebar should activate at
    :type min_rel_detect: float (0-1)
    :param max_rel_display: The maximum size relative to the root window that the sidebar should expand to
    :type max_rel_display: float (0-1)
    :param min_rel_display: The minimum size the sidebar should be relative to the root window (Default to 0 so it doesn't show)
    :type min_rel_display: float (0-1)
    :param side: The side of the root window the sidebar should be on
    :type side: str (left or right)
    :param default_tab_height: The relative size tabs should be if no unique size is given (Defaults to 0.1)
    :type default_tab_height: float (0-1)
    :param animate: Whether to animate the sidebar expansion and collapse (Defaults to False)
    :type animate: bool
    """
    def __init__(self, root, min_rel_detect, max_rel_display, min_rel_display: float = 0, 
                 side: str="left", default_tab_height: float=0.1, animate: bool = False):
        self.root = root
        self.sidebarExpanded = False
        self.currentSize = min_rel_display
        self.minDetect = min_rel_detect
        self.sidebarMinWidth = min_rel_display
        self.sidebarMaxWidth = max_rel_display
        self.isAnimated = animate
        self.originalMenuTabRelHeight = {}
        self.expandableTabs = []
        self.expandedFrame = [None, None] #Holds the current frame to be filled and the last one that needs to be removed
        self.defaultMenuTabHeight = default_tab_height
        if side == "left":
            self.anchor = "nw"
            self.sidebarXStart = 0
        elif side == "right":
            self.anchor = "ne"
            self.sidebarXStart = 1
        self.changeIncrement = 0.2 #Increment by 20%% of the range for each step

        #Create sidebar frame
        self.widgetTree = treelib.Tree()
        rootNode = SidebarWidget("Sidebar", Frame, self.root,
                                                       widget_place_properties={"relwidth":self.currentSize, "relheight":1.0, 
                                                                         "relx": self.sidebarXStart, "anchor":self.anchor, 
                                                                         "rely":0})
        self.widgetTree.add_node(rootNode)
        self.enable()
        self.root.bind("<Motion>", self.check_in_sidebar,"+")
        self.root.bind("<FocusOut>", self.disable)
        self.root.bind("<FocusIn>", self.enable)         

    def check_in_sidebar(self, event):
        """
        Check to see if the motion event in the root window is within the sidebars activation/deactivation range
    
        :param event: The motion event that occured
        :type event: Event(Motion)
        """
        if not self.sidebarExpanded: #If the sidebar is collapsed
            if abs((event.x_root-self.root.winfo_x())/self.root.winfo_width() - self.sidebarXStart) < self.minDetect: #Check if it is inside in the x direction
                self.expand()
        else:
            if abs((event.x_root-self.root.winfo_x())/self.root.winfo_width() - self.sidebarXStart) > self.sidebarMaxWidth: #Check if it is inside in the x direction
                self.contract()

    def expand(self):
        """
        Expands the sidebar widget onto the screen. If the animate flag is True, then it will also animate the sidebar.
        """
        if not self.enabled:
            return
        #If we are not animated, then just make the size the max
        if not self.isAnimated:
            self.currentSize = self.sidebarMaxWidth
            self.sidebarExpanded = True
        else:
            if self.currentSize < self.sidebarMaxWidth:
                self.currentSize = self.currentSize + self.changeIncrement*(self.sidebarMaxWidth-self.sidebarMinWidth)
                self.root.after(10, self.expand)
            else:
                self.sidebarExpanded = True
        self.widgetTree["Sidebar"].place(True, relwidth=self.currentSize)
        self.root.update()
        self.root.update_idletasks()
        if self.sidebarExpanded:
            self.fill_frames()

    def contract(self):
        """
        Contracts the sidebar widget from the screen. Also animates the widegt contraction if animate flag is True.
        """
        if self.isAnimated:
            if self.currentSize > self.sidebarMinWidth:
                self.currentSize = self.currentSize - self.changeIncrement*(self.sidebarMaxWidth-self.sidebarMinWidth)
                self.widgetTree["Sidebar"].place(True, relwidth=self.currentSize)
                self.root.after(10, self.contract)
            else:
                self.sidebarExpanded = False
                self.widgetTree["Sidebar"].place_forget()
        else:
            self.currentSize = self.sidebarMinWidth
            self.sidebarExpanded = False
            self.widgetTree["Sidebar"].place_forget()
        self.root.update()
        self.root.update_idletasks()
        self.expandedFrame = [None, None]
        self.fill_frames()
                
    def label_clicked(self, event):
        """
        Called when one of the labels is clicked inside the sidebar to expand the menu up or down 
        
        :param event: The event that called this function
        :type event: tkinter.Event
        """
        for frame in self.widgetTree.children("Sidebar"):
            if frame.widget == event.widget:
                if frame.tag.replace("Tab", "WidgetFrame") == self.expandedFrame[1]: #Check if we already clicked on the already expanded tab
                    self.expandedFrame[0] = self.expandedFrame[1]
                    self.expandedFrame[1] = None
                else: #Otherwise we will expand the frame that was just clicked on
                    self.expandedFrame[0] = self.expandedFrame[1]
                    self.expandedFrame[1] = frame.tag.replace("Tab","WidgetFrame")
                self.fill_frames()
                
    def fill_frames(self):
        """
        Looks to see if any of the widget frames should be expanded and shown on the sidebar. Also collapses any that shouldn't be open
        """
        frameRelTotal = 0
        for child in self.widgetTree.children("Sidebar"):
            if "Tab" in child.identifier: #Always place the label part of the tab
                child.place(relheight=self.defaultMenuTabHeight, rely=frameRelTotal)
                frameRelTotal += self.defaultMenuTabHeight
            elif child.tag == self.expandedFrame[0]: #De-expand the last open tab
                child.place_forget()
            elif child.tag == self.expandedFrame[1]: #Expand the newest opened tab
                child.place(rely=frameRelTotal)
                frameRelTotal += child.placeProperties["relheight"]
            else:
                child.place_forget()

    def add_widget(self, name: str, type, menu_name:str="Sidebar", properties:dict={}, place_properties:dict={}):
        """
        Adds a widget to the tree under a menu tab if given, otherwise the widget will appear on the root

        :param name: The name to give the widget, used for later searching of the tree
        :type name: str
        :param type: The type of the widget to make
        :type type:
        """
        newNode = SidebarWidget(name, type, self.widgetTree[menu_name], properties.copy(), place_properties.copy())
        self.widgetTree.add_node(newNode, self.widgetTree[menu_name])

    def add_menu_tab(self, name:str, tab_expandable:bool = True, tab_properties:dict={}, tab_place_properties:dict={}):
        """
        Adds a menu tab to the sidebar
    
        :param name: The name to give the tab
        :type name: str
        :param tab_expandable: Determines if the tab can be clicked on and expanded (Defaults to True)
        :type tab_expandable: bool
        :param tab_properties: Any keyword arguments to give to the tab label
        :type tab_proerties: dict
        :param tab_place_properties: Keyword arguments to place the tab in a specific way
        :type tab_place_properties: dict
        """
        tabPlaceProperties = tab_place_properties.copy()
        tabProperties = tab_properties.copy()
        if tab_expandable:
            self.expandableTabs.append(name)
            tabProperties.update({"command":self.label_clicked})         
        self.add_widget(name+"Tab", Label, properties=tabProperties)
        self.add_widget(name+"WidgetFrame", Frame, place_properties=tabPlaceProperties)

    def add_menu_button(self, name:str, button_command, menu_name:str="Sidebar", properties:dict={}, place_properties:dict={}):
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
        buttonProperties = properties.copy()
        buttonProperties.update({"command":button_command, "text":name,"style":"TButton"})
        if not menu_name == "Sidebar":
            tabName = menu_name + "WidgetFrame" 
        self.add_widget(name, Button, tabName, properties=buttonProperties, place_properties=place_properties.copy())
        self.place_children(tabName)

    def add_combobox(self, name: str, tabname:str, combo_values:list, combo_command, combo_variable, combo_default:str=""):
        """
        Adds a combo box to a menu tab
    
        :param name: The name to give to the combobox
        :type name: str
        :param tabname: The parent tab to put the combobox in
        :type tabname: str
        :param combo_values: The list of values to give to the combobox
        :type combo_values: list
        :param combo_command: The function to call when the combobox changes value
        :type combo_command: Callable
        :param combo_variable: The variable to link to the combobox
        :type combo_variable: Tk.IntVar or Tk.BooleanVar
        :param combo_default: The default value to give to the combo box (Defaults to "")
        :type combo_default: str
        """
        self.add_widget(name+"Text", Label, tabname+"WidgetFrame", properties={"text":name, "anchor":"center","style":"TLabel"}, place_properties={"relwidth":0.5, "relheight":1.0, "relx":0, "rely":0})
        self.add_widget(name+"Combobox", Combobox, tabname+"WidgetFrame", properties={"values":combo_values, "textvariable":combo_variable},place_properties={"relwidth":0.5, "relheight":1.0, "relx":0.5, "rely":0})
        self.widgetTree[name+"Combobox"].widget.set(combo_default)
        self.widgetTree[name+"Combobox"].widget.bind("<<ComboboxSelected>>", combo_command)
        self.place_children(tabname+"WidgetFrame")

    def add_entry(self, name, label_text, tabname:str="Sidebar", command_func=None, properties:dict={}, place_properties:dict={}):
        """
        Adds and entry box to the tab
    
        :param name: The name to give the entry
        :type name: str
        :param label_text: The text to be displayed above the entry box
        :type label_text: str
        :param tabname: The name of the tab to add the entry to (Defaults to the root of the sidebar)
        :type tabname: str
        :param command_func: The function to call when the entry box gets data
        :type command_func: Callable
        :param properties: Any key word arguments to give the entry
        :type properties: dict
        :param place_properties: Any keyword arguments to place the entry
        :type place_properties: dict
        """
        self.add_widget(name+"Text", Label, tabname+"WidgetFrame", properties={"text":label_text, "anchor":"center"})
        entryProperties = properties.copy()
        placeProperties = place_properties.copy()
        self.add_widget(name, Entry, tabname+"WidgetFrame", entryProperties, placeProperties)
        self.widgetTree[name].widget.bind("<Button-1>", lambda event: self.switch_entry_binds(event,command_func))
        self.place_children(tabname+"WidgetFrame")
     
    def change_widget_properties(self, widget_name, **kwargs):
        """
        Changes some properties of any child in the sidebar
    
        :param widget_name: The name of the widget to change
        :type widget_name: str
        :param kwargs: The keyword arguments to send to the widget
        :type kwargs: keyword=keyword_value
        """  
        self.widgetTree[widget_name].set_widget_property(**kwargs)
      
    def change_widget_place_property(self, widget_name, **kwargs):
        """
        Changes some of the place properties of a widget in the sidebar
    
        :param widget_name: The name of the widget to change the place properties of
        :type widget_name: str
        :param kwargs: The keyword arguments that you want to pass to the widget
        :type kwargs: keyword=keyword_value
        """
        self.widgetTree[widget_name].set_widget_place_property(**kwargs)
     
    def place_children(self, tab_tag):
        """
        Places the children within the specified frame for a specific tab. Accounts for some children having a specified relheight. 
        Then distributes the rest of the relheight equally amongst the rest of the children
    
        :param tab_tag: The name of the tab to place the children in
        :type tab_tag: str
        """
        widgetFrameRelTotal = 0
        tabChildren = self.widgetTree.children(tab_tag)
        if tabChildren == []: #Don't place any children if there are none
            return
        numChildrenRelHeight, childRelTotal = self.count_total_child_relheight(tab_tag)
        for child in tabChildren:
            if numChildrenRelHeight > 0:
                widgetRelHeight = (1-childRelTotal)/(len(tabChildren)-numChildrenRelHeight)
            else:
                widgetRelHeight = 1/len(tabChildren)
            child.place(relheight = widgetRelHeight, rely=widgetFrameRelTotal)
            widgetFrameRelTotal += widgetRelHeight

    def count_total_child_relheight(self, widget_frame):
        """
        Counts the number of child widgets that have a relheight assigned to them from the user and the total relheight of all those children
    
        :param widget_frame: The frame that holds the children to get the relheights from
        :type widget_frame: ttkboostrap.Frame
    
        :returns: The count of children with relheights assigned and the total that those children make up
        :rtype: tuple(count, total)
        """
        count = 0
        total = 0
        for child in self.widgetTree.children(widget_frame):
            if "relheight" in child.placeProperties:
                count += 1
                total += child.placeProperties["relheight"]
        return (count , total)
   
    def switch_entry_binds(self, event, command_func):
        """
        When an entry is clicked on, bind the enter button to call the command function
    
        :param event: The event that called this function
        :type event: tkinter.Event
        :param command_func: The function call when the enter button is pressed
        :type command_func: Callable
        """
        event.widget.unbind("<Button-1")
        event.widget.bind("<Return>", command_func)
        
    def disable(self, event=None):
        """
        Used to diable the sidebars from expanding when the root widget goes out of focus

        :param event: The focus out event that occurs or None if we want to manually disable it
        :type event: Event(FocusOut)
        """
        self.enabled = False
        self.contract()

    def enable(self, event=None):
        """
        Used to enable the sidebars when the root widget goes in focus

        :param event: The focus in event that occurs or None if we want to manually enable it
        :type event: Event(FocusIn)
        """
        self.enabled = True








