from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Text
import datetime
from os.path import join as ospathjoin

class AddMarkerNoteDialog(DialogTemplate):
    """
    Class to handle adding notes to a marker
    
    :param main_window: The window this pop-up should be in front of
    :type main_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param marker: The marker that we want to add a note to
    :type marker: markers.Marker
    """
    def __init__(self, main_window, marker):
        super().__init__(main_window)
        self.top.geometry("675x425")
        self.top.minsize(675,425)
        self.top.title(marker.name+" Note Entry")
        self.marker = marker
        self.result = "Cancelled" #Assume the user cancelled the operation
        #Create entry boxes and labels
        self.top.unbind("<Return>") #The enter key should allow new lines to be typed in instead of saving the note
        self.textEntry = Text(self.top, wrap="word", takefocus=True)
        #Pack items into box
        self.textEntry.place(relwidth=1, relheight=1)
        #Pack Frames and Position
        self.pack_frames({self.textEntry:[1,0.8,0,0],
                          self.buttonFrame:[1,0.2,0,0.8]})
        self.show()
          
    def on_okay(self):
        """
        Called when the okay button is pushed
        """  
        try:
            with open(ospathjoin(self.marker.notesPath, str(datetime.now()).replace(":", "_").replace("-", "_").replace(" ","_").split(".")[0]+".txt"),"w") as file:
                file.write("Date: "+str(datetime.now().strftime("%m/%d/%Y"))+"\n")
                file.write("Time: "+str(datetime.now().strftime("%H:%M:%S"))+"\n")
                file.write(self.textEntry.get("1.0", "end"))
                self.result = "Success"
        except Exception as e:
            self.result = e.args[0]
        self.close_dialog()




