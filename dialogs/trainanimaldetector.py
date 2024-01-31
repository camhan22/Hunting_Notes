from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Label, Entry, Combobox
import ttkbootstrap.validation as ttkval
from torch.cuda import is_available as torchcudaavailable
from torch.cuda import device_count as torchcudadevicecount
from torch.cuda import get_device_name as torchcudagetdevicename
from numpy import Infinity

class AnimalDetectorTrainingDialog(DialogTemplate):
    def __init__(self, root_window):
        super().__init__(root_window)
        self.top.geometry("300x200")
        self.top.title("Training Parameters")
        self.device = "None"
        self.epochLabel = Label(self.widgetFrame, text="Training Epochs", anchor="center")
        self.batchLabel = Label(self.widgetFrame, text="Batch Size", anchor="center")
        self.epochBox = Entry(self.widgetFrame, justify="center")
        self.batchBox = Entry(self.widgetFrame, justify="center")
        ttkval.add_range_validation(self.epochBox,1,Infinity)
        ttkval.add_range_validation(self.batchBox,1, Infinity)
        if torchcudaavailable():
            self.deviceLabel = Label(self.widgetFrame, text="Device", anchor="center")
            self.deviceComboBox = Combobox(self.widgetFrame, justify="center")
            self.deviceComboBoxValues = {torchcudagetdevicename(item):item for item in range(0,torchcudadevicecount())}
            self.deviceComboBoxValues.update({"CPU":"cpu"})
            self.deviceComboBox.configure(values=list(self.deviceComboBoxValues.keys()))
            self.deviceComboBox.current(0)
            relativeHeights = 1/6
        else:
            relativeHeights = 1/4
            self.device = "cpu"
           
        #Place widgets in the entry frame
        self.epochLabel.place(relwidth=1.0, relheight=relativeHeights)
        self.epochBox.place(relwidth=1.0, relheight=relativeHeights, rely=relativeHeights)
        self.batchLabel.place(relwidth=1.0, relheight=relativeHeights, rely=2*relativeHeights)
        self.batchBox.place(relwidth=1.0, relheight=relativeHeights, rely=3*relativeHeights)
        if relativeHeights == 1/6:
            self.deviceLabel.place(relwidth=1.0, relheight=relativeHeights, rely=4*relativeHeights)
            self.deviceComboBox.place(relwidth=1.0, relheight=relativeHeights, rely=5*relativeHeights)
            
        self.pack_frames({self.widgetFrame:[1.0,0.8,0,0], self.buttonFrame:[1.0,0.2,0,0.8]})
        self.show()
         
    def on_okay(self):
        if not self.epochBox.state() == ():
            return
        if not self.batchBox.state() == ():
            return
        self.result = {"Batch Size":int(self.batchBox.get()), "Epochs": int(self.epochBox.get())}
        if self.device == "cpu":
            self.result.update({"Device":self.device})
        else:
            self.result.update({"Device":self.deviceComboBoxValues[self.deviceComboBox.get()]})
        self.close_dialog()




