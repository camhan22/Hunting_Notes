from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Frame, Button, Label, Entry
from tkinter import StringVar

class AnimalFinderResults(DialogTemplate):
    def __init__(self, main_window, species, best_distance, best_location, best_time: str = ""):
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



