from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Frame, Button, Label, Entry
from tkinter import StringVar

class AnimalFinderResults(DialogTemplate):
    """
    Class to show the results of the animal finder predicitions
    
    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param species: The species the user is trying to hunt
    :type species: str
    :param best_distance: The distance the stand is from the best camera location
    :type best_distance: float
    :param best_location: The best stand to go to during the time selected
    :type best_location: str
    :param best_time: The time at which the most deer were seen
    :type best_time: str
    """
    def __init__(self, main_window, species:str, best_distance:float, best_location:str, best_time: str = ""):
        super().__init__(main_window, False, True)
        #Variables
        speciesOutputVar = StringVar()
        locationOutputVar = StringVar()
        timeOutputVar = StringVar()
        distanceOutputVar = StringVar()
        #Widgets
        self.top.title("Finder Results")
        self.top.geometry("200x100")
        #Buttons
        buttonFrame = Frame(self.top)
        exitButton = Button(buttonFrame, text="Close", command=self.close_dialog)
        #Labels
        labelsFrame = Frame(self.widgetFrame)
        speciesLabel = Label(labelsFrame, text="Species to hunt")
        locationLabel = Label(labelsFrame, text="Closest location")
        timeLabel = Label(labelsFrame, text="Best time")
        distanceLabel = Label(labelsFrame, text="Distance")
        #Output Boxes
        outputBoxFrame = Frame(self.widgetFrame)
        speciesOutputBox = Entry(outputBoxFrame, state="disabled", textvariable=speciesOutputVar)
        locationOutputBox = Entry(outputBoxFrame, state="disabled", textvariable=locationOutputVar)
        timeOutputBox = Entry(outputBoxFrame, state="disabled", textvariable=timeOutputVar)
        distanceOutputBox = Entry(outputBoxFrame, state="disabled", textvariable=distanceOutputVar)
        #Set variables
        speciesOutputVar.set(species)
        locationOutputVar.set(best_location)
        timeOutputVar.set(best_time)
        distanceOutputVar.set(best_distance)
        #Pack widget frames
        #Labels
        speciesLabel.pack(fill="both", expand=True)
        locationLabel.pack(fill="both", expand=True)
        distanceLabel.pack(fill="both", expand=True)
        timeLabel.pack(fill="both", expand=True)
        #OutputBoxes
        speciesOutputBox.pack(fill="both", expand=True)
        locationOutputBox.pack(fill="both", expand=True)
        distanceOutputBox.pack(fill="both", expand=True)
        timeOutputBox.pack(fill="both", expand=True)
        #Pack button frame
        exitButton.pack(fill="both", expand=True)
        #Frame packing and positioning
        labelsFrame.pack(fill="both", expand=True, side="left")
        outputBoxFrame.pack(fill="both", expand=True, side="left")
        self.widgetFrame.pack(fill="both", expand=True)
        buttonFrame.pack(fill="both", expand=True)
        self.show(no_wait=True)



