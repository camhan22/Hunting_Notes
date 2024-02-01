from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Label, Combobox

"""Class to handle the retraining of the animal finder models"""
class AnimalFinderTrainingDialog(DialogTemplate):
    """
    Initialize the retrain dialog
    
    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    """
    def __init__(self, main_window):
        super().__init__(main_window)
        self.top.title("Train Finder Model")
        self.top.geometry("250x100")
        self.speciesLabel = Label(self.widgetFrame, text="Species to hunt")
        self.speciesComboBox = Combobox(self.widgetFrame, justify="center")
        self.speciesComboBox.configure(values=["Deer", "Turkey", "Rabbit"])
        self.speciesComboBox.current(0)
        #Pack widget frames
        self.speciesLabel.place(relwidth=1.0, relheight=0.5)
        self.speciesComboBox.place(relwidth=1.0, relheight=0.5, rely=0.5)
        #Frame packing and positioning
        self.pack_frames({self.widgetFrame:[1,0.7,0,0],
                          self.buttonFrame:[1,0.3,0,0.7]})
        self.show()

    """
    Called when the okay button is pushed
    """           
    def on_okay(self):
        self.result = self.speciesComboBox.get()
        self.close_dialog()




