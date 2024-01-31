import treelib
from sidebar.sidebarwidget import SidebarWidget
from ttkbootstrap import Label, Button, Combobox, Frame, Entry
import ttkbootstrap.validation as ttkval

class Sidebar():
    """Class to add a sidebar to a window"""
    def __init__(self, root, min_rel_detect, max_rel_display, min_rel_display: float = 0, 
                 side: str="left", default_menu_height: float=0.1, animate: bool = False):
        self.root = root
        self.sidebarExpanded = False
        self.currentSize = min_rel_display
        self.minDetect = min_rel_detect
        self.sidebarMinWidth = min_rel_display
        self.sidebarMaxWidth = max_rel_display
        self.isAnimated = animate
        self.originalMenuTabRelHeight = {}
        self.expandableFrames = []
        self.expandedFrame = None
        self.defaultMenuTabHeight = default_menu_height
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
                                                       place_properties={"relwidth":self.currentSize, "relheight":1.0, 
                                                                         "relx": self.sidebarXStart, "anchor":self.anchor, 
                                                                         "rely":0})
        self.widgetTree.add_node(rootNode)
        self.enable()
        self.root.bind("<Motion>", self.check_in_sidebar,"+")
        self.root.bind("<FocusOut>", self.disable)
        self.root.bind("<FocusIn>", self.enable)         

    """
    Check to see if the motion event in the root window is within the sidebars activation/deactivation range
    :param event: The motion event that occured
    :type event: Event(Motion)
    """
    def check_in_sidebar(self, event):
        if not self.sidebarExpanded: #If the sidebar is collapsed
            if abs((event.x_root-self.root.winfo_x())/self.root.winfo_width() - self.sidebarXStart) < self.minDetect: #Check if it is inside in the x direction
                self.expand()
        else:
            if abs((event.x_root-self.root.winfo_x())/self.root.winfo_width() - self.sidebarXStart) > self.sidebarMaxWidth: #Check if it is inside in the x direction
                self.contract()

    """
    Expands the sidebar widget onto the screen
    If the animate flag is True, then it will also animate the sidebar
    """
    def expand(self):
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
            self.fill()

    """
    Contracts the sidebar widget from the screen
    Also animates the widegt contraction if animate flag is True
    """
    def contract(self):
        if self.isAnimated:
            if self.currentSize > self.sidebarMinWidth:
                self.currentSize = self.currentSize - self.changeIncrement*(self.sidebarMaxWidth-self.sidebarMinWidth)
                self.widgetTree["Sidebar"].place(True, relwidth=self.currentSize)
                self.root.after(10, self.contract)
            else:
                self.sidebarExpanded = False
                self.widgetTree["Sidebar"].place_forget()      
            self.root.update()
            self.root.update_idletasks()
        else:
            self.currentSize = self.sidebarMinWidth
            self.sidebarExpanded = False
            self.widgetTree["Sidebar"].place_forget()
            self.root.update()
            self.root.update_idletasks()
                
    """
    Called when one of the labels is clicked inside the sidebar to expand the menu up or down 
    """
    def label_clicked(self, event):
        for frame in self.widgetTree.children("Sidebar"):
            for element in self.widgetTree.children(frame.tag):
                if element.widget == event.widget:
                    if frame.tag == self.expandedFrame: #Check if we already clicked on the already expanded tab
                        self.expandedFrame = None
                    else: #Otherwise we will expand the frame that was just clicked on
                        self.expandedFrame = frame.tag
                    self.fill_frames()
                         
    """
    Fills in the sidebar frame with the frames placed into it (Only runs once when it first gets expanded)
    
    def fill(self, expanded_frame=None):
        frameRelTotal = 0
        for child in self.widgetTree.children("Sidebar"):
            if not child.tag in self.expandableFrames: #If the frame is not a part of the expandable frames list, then we just place it and move on
                self.place_children(self.widgetTree.children(child.tag),True)
                child.place()
                continue
            #Check expandable frames now
            if expanded_frame is not None and child.tag == expanded_frame:
                self.place_children(self.widgetTree.children(child.tag),True)
                child.place(relheight=self.originalMenuTabRelHeight[child.tag], rely=frameRelTotal)
                frameRelTotal += self.originalMenuTabRelHeight[child.tag]
            else: #For every other frame that isn't expanded
                self.place_children(self.widgetTree.children(child.tag)) #Make only the label placeable
                widgetCount, usedHeight = self.count_total_child_relheight(self.widgetTree.children(child.tag))
                if widgetCount == 0 and usedHeight == 0:
                    if len(self.widgetTree.children(child.tag)) == 0:
                        labelHeight = child.placeProperties["relheight"]
                        child.place(rely=frameRelTotal)
                        frameRelTotal += labelHeight
                        continue
                    else:
                        labelHeight = self.defaultMenuTabHeight
                child.delete_widget_place_property("relheight", "rely")
                child.place(relheight=labelHeight, rely=frameRelTotal)
                frameRelTotal += labelHeight
    """
    def fill_frames(self):
            pass

    """
    Adds a widget to the tree under a menu tab if given, otherwise the widget will appear on the root

    :param name: The name to give the widget, used for later searching of the tree
    :type name: str
    :param type: The type of the widget to make
    :type type:
    """
    def add_widget(self, name: str, type, menu_name:str="Sidebar", properties:dict={}, place_properties:dict={}):
        newNode = SidebarWidget(name, type, self.widgetTree[menu_name], properties.copy(), place_properties.copy())
        self.widgetTree.add_node(newNode, self.widgetTree[menu_name])
        self.place_children(self.widgetTree.children(menu_name))

    """
    Adds a menu tab to the sidebar
    """
    def add_menu_tab(self, name, menu_name="Sidebar", tab_expandable:bool = True, tab_properties:dict={}, tab_place_properties:dict={}):
        tabPlaceProperties = tab_place_properties.copy()
        tabProperties = tab_properties.copy()
        if "relheight" in tabPlaceProperties and tab_expandable:
            self.originalMenuTabRelHeight.update({name:tabPlaceProperties["relheight"]})
            self.expandableFrames.append(name)
            tabProperties.update({"borderwidth":1})
        #Add the containing frame for the label to be placed in
        self.add_widget(name, Frame, menu_name, properties=tabProperties, place_properties=tabPlaceProperties)
        #Add the header label
        if tab_expandable:
            tabProperties.update({"command":self.label_clicked})
        self.add_widget(name+"Label", Label, name, properties=tabProperties)

    def add_menu_button(self, name, button_command, menu_name:str="Sidebar", properties:dict={}, place_properties:dict={}):
        buttonProperties = properties.copy()
        buttonProperties.update({"command":button_command, "text":name,"style":"TButton"})
        self.add_widget(name, Button, menu_name, properties=buttonProperties, place_properties=place_properties.copy())

    def add_combobox(self, name, menu_name, combo_values, combo_default, combo_command, combo_variable, place_properties:dict={}):
        placeProperties = place_properties.copy()
        self.add_widget(name, Frame, menu_name, place_properties=placeProperties)
        self.add_widget(name+"Text", Label, name, properties={"text":name, "anchor":"center","style":"TLabel"}, place_properties={"relwidth":0.5, "relheight":1.0, "relx":0, "rely":0})
        self.add_widget(name+"Combobox", Combobox, name, properties={"values":combo_values, "textvariable":combo_variable},place_properties={"relwidth":0.5, "relheight":1.0, "relx":0.5, "rely":0})
        self.widgetTree[name+"Combobox"].widget.set(combo_default)
        self.widgetTree[name+"Combobox"].widget.bind("<<ComboboxSelected>>", combo_command)
        
    def add_entry(self, name, label_text, menu_name:str="Sidebar", validation_func=None, command_func=None, properties:dict={}, place_properties:dict={}):
        self.add_widget(name+"Text", Label, menu_name, properties={"text":label_text, "anchor":"center"},place_properties={"relwidth":1})
        prop = properties.copy()
        placeProperties = place_properties.copy()
        placeProperties.update({"relwidth":1})
        self.add_widget(name, Entry, menu_name, prop, placeProperties)
        if validation_func is not None:
            ttkval.add_validation(self.widgetTree[name].widget, validation_func, when="key")
            self.widgetTree[name].widget.bind("<Button-1>", lambda event: self.switch_entry_binds(event,command_func))
            
    def change_widget_properties(self, widget_name, **kwargs):
        self.widgetTree[widget_name].set_widget_property(**kwargs)
        
    def change_widget_place_property(self, widget_name, **kwargs):
        self.widgetTree[widget_name].set_widget_place_property(**kwargs)
        
    """
    def place_children(self, children, place_all_children:bool=False):
        childRelTotal = 0
        if children == []:
            return
        only_label = True if self.widgetTree.parent(children[0].tag).tag in self.expandableFrames else False
        sortedChildren = sorted(children, key=lambda child: child.placeOrder)
        numChildrenRelHeight, childrenRelHeightTotal = self.count_total_child_relheight(sortedChildren)
        
        for child in sortedChildren:
            if "relheight" in child.placeProperties:
                widgetHeight = child.placeProperties["relheight"]
                if "rely" in child.placeProperties:
                    child.place()
                else:
                    child.place(rely=childRelTotal)
            else:
                widgetHeight = (1-childrenRelHeightTotal)/(len(sortedChildren)-numChildrenRelHeight)
                if not place_all_children:
                    if "Label" in child.tag and only_label:
                        child.place(relheight=1, rely=0)
                    elif only_label:
                        child.place_forget()
                    else:
                        child.place(relheight=widgetHeight, rely=childRelTotal)
                else:
                    child.place(relheight=widgetHeight, rely=childRelTotal)
            childRelTotal += widgetHeight

    def count_total_child_relheight(self, children):
        count = 0
        total = 0
        for child in children:
            if "relheight" in child.placeProperties:
                count += 1
                total += child.placeProperties["relheight"]

        return (count , total)
    """    
    
    def switch_entry_binds(self, event, command_func):
        event.widget.unbind("<Button-1")
        event.widget.bind("<Return>", command_func)
        

    """
    Used to diable the sidebars from expanding when the root widget goes out of focus

    :param event: The focus out event that occurs or None if we want to manually disable it
    :type event: Event(FocusOut)
    """
    def disable(self, event=None):
        self.enabled = False
        self.contract()

    """
    Used to enable the sidebars when the root widget goes in focus

    :param event: The focus in event that occurs or None if we want to manually enable it
    :type event: Event(FocusIn)
    """
    def enable(self, event=None):
        self.enabled = True








