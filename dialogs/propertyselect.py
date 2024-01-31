from dialogs.templatedialog import DialogTemplate
from dialogs.loadnewmap import LoadNewMapDialog
from ttkbootstrap import Label, Button, Combobox
from tkinter import messagebox
from os import listdir as oslistdir

class PropertySelectDialog(DialogTemplate):
    """Holds dialog that comes up when the system starts"""
    def __init__(self, main_window, data_directory):
        super().__init__(main_window, False)
        self.dataDirectory = data_directory
        self.top.geometry("250x150")
        self.top.title("Property Select")
        #Widgets
        self.loadNewMapButton = Button(self.top, text="Load new map", command=self.load_new_map)
        self.areaLabel = Label(self.widgetFrame, text="Property", anchor="center")
        self.areaBox = Combobox(self.widgetFrame, justify="center")

        self.areaLabel.place(relwidth=1.0, relheight=0.5)
        self.areaBox.place(relwidth=1.0, relheight=0.5, rely=0.5)
        #Pack Frames and Position
        self.pack_frames({self.widgetFrame:[1,1-2*self.relativeButtonHeight,0,0], 
                          self.buttonFrame:[1,self.relativeButtonHeight,0,1-2*self.relativeButtonHeight],
                          self.loadNewMapButton:[1,self.relativeButtonHeight,0,1-self.relativeButtonHeight]})
        self.load_map_options()
        self.areaBox.current(0)
        self.show()
        
    def on_okay(self):
        self.result = self.areaBox.get()
        self.close_dialog()

    def load_new_map(self):
        self.top.withdraw()
        loadDialog = LoadNewMapDialog(self.mainWindow, self.dataDirectory)
        if loadDialog.result is not None:
            self.load_map_options()
            self.areaBox.set(loadDialog.result)
        self.top.deiconify()

    def load_map_options(self):
        files = oslistdir(self.dataDirectory)
        if files == []: #If there is no data, then force a map loading session
            messagebox.showwarning("No Map Data", "There are no maps currently downloaded, please download one now")
            self.load_new_map()
        files = [f for f in files if not f.endswith(".csv")] #Remove any files that have csv at end
        files = [f.replace("_"," ") for f in files] #Replace any underscores with spaces
        files = [f.title() for f in files] #Titleize the string (Every character after a space is capital)
        files = [f.split(".")[0] for f in files] #Remove the .db extension
        self.areaBox.configure(values=files) #Convert the files list to a tuple and store it in the combo box




