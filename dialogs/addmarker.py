from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Entry, Combobox, Frame, Label
from ttkbootstrap.tooltip import ToolTip
from utils import validate_coord

class AddMarkerDialog(DialogTemplate):
    """class to bring up the add marker dialog"""
    def __init__(self, main_window, coords=None):
        super().__init__(main_window)
        entryRelHeight = 3/8
        comboboxRelHeight = 1/4
        self.coords = coords
        if coords is None:
            self.top.geometry("400x150")
        else:
            self.top.geometry("400x100")
        self.top.title("Create Marker")
        #Create frames for entrys and labels
        self.labelFrame = Frame(self.widgetFrame)
        self.entryFrame = Frame(self.widgetFrame)
        #Create entry boxes and labels
        self.nameEntry = Entry(self.entryFrame)
        self.latLongEntry = Entry(self.entryFrame)
        self.typeEntry = Combobox(self.entryFrame, justify="center")
        self.typeEntry.configure(values=["Stand", "Camera", "Point of Interest"])
        self.typeEntry.set("")
        self.nameLabel = Label(self.labelFrame, text="Name of Marker:")
        self.latLongLabel = Label(self.labelFrame, text="Coordinates:")
        self.typeLabel = Label(self.labelFrame, text="Marker Type:")
        #Add items to grid
        if coords is None:
            self.nameLabel.place(relwidth=1.0, relheight=entryRelHeight)
            self.latLongLabel.place(relwidth=1.0, relheight=entryRelHeight, rely=entryRelHeight)
            self.typeLabel.place(relwidth=1.0, relheight=comboboxRelHeight, rely=2*entryRelHeight)
        else:
            self.nameLabel.place(relwidth=1.0, relheight=0.6)
            self.typeLabel.place(relwidth=1.0, relheight=0.4, rely=0.6)
            
        if coords is None:
            self.nameEntry.place(relwidth=1.0, relheight=entryRelHeight)
            self.latLongEntry.place(relwidth=1.0, relheight=entryRelHeight, rely=entryRelHeight)
            self.typeEntry.place(relwidth=1.0, relheight=comboboxRelHeight, rely=2*entryRelHeight)
        else:
            self.nameEntry.place(relwidth=1.0, relheight=0.6)
            self.typeEntry.place(relwidth=1.0, relheight=0.4, rely=0.6)
        #Add frames to widgetFrame
        self.labelFrame.place(relwidth=0.5,relheight=1.0)
        self.entryFrame.place(relwidth=0.5, relheight=1.0, relx=0.5)
        #Pack Frame Widgets and Position
        if coords is None:
            self.pack_frames({self.widgetFrame:[1,0.8,0,0],
                          self.buttonFrame:[1,0.2,0,0.8]})
            #ttkval.add_validation(self.latLongEntry, validate_coord)
        else:
            self.pack_frames({self.widgetFrame:[1,0.6,0,0],
                          self.buttonFrame:[1,0.4,0,0.6]}) 
        #Tooltip
        self.helpToolTip = ToolTip(self.latLongEntry,"Format: latitude, longitude (eg. -42.5464, -83.5734)")
        self.show()
        
    def on_okay(self):
        #Check if we got coordinates from outside this dialog
        if self.coords is None:
            #Validate the coordinate input
            
            valArgs = ["-1","-1","","","","","Final",self.latLongEntry]
            if not validate_coord(*valArgs):
                self.latLongEntry.configure(style="danger.TEntry")
                self.helpToolTip.show_tip()
                return
            else:
                self.latLongEntry.configure(style="TEntry")
                self.helpToolTip.hide_tip()
                coord = self.latLongEntry.get().split(",")
        else:
            coord = self.coords.split(",")
        lat = float(coord[0])
        long = float(coord[1].strip()) #Replace any spaces with nothing before trying to convert it
        name = self.nameEntry.get()
        markerType = self.typeEntry.get()
        self.result = {"lat":lat, "long":long,"name":name, "markerType":markerType}
        self.close_dialog()




