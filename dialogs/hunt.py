from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Frame, Label, Entry, Combobox, DateEntry
from datetime import datetime
from datetime import timedelta

class HuntDialog(DialogTemplate):
    def __init__(self, main_window, timestep: int = 15, first_week_day: int = 7):
        super().__init__(main_window)
        self.top.title("Hunt")
        self.top.geometry("300x350")
        self.inputFrame = Frame(self.widgetFrame)
        self.speciesLabel = Label(self.inputFrame, text="Species to hunt", anchor="center")
        self.speciesComboBox = Combobox(self.inputFrame, justify="center")
        self.speciesComboBox.configure(values= ["Deer", "Turkey", "Rabbit"])
        self.speciesComboBox.current(0)
        self.calendar = DateEntry(self.widgetFrame, first_week_day, startdate=datetime.now())
        #self.calendar = Calendar(master=self.widgetFrame, mindate=datetime.now(), maxdate=datetime.now()+timedelta(days=5), firstweekday=first_week_day)
        self.lengthLabel = Label(self.inputFrame, text="Hours to hunt", anchor="center")
        self.lengthEntry = Entry(self.inputFrame, justify="center")
        self.startLabel = Label(self.inputFrame, text="Starting time", anchor="center")
        self.startTime = Combobox(self.inputFrame, justify="center")
        self.startTime.set("")
        self.startTime.configure(values=["{0:02d}:{1:02d}".format(int(time/60),int(time % 60)) for time in range(0, 1440,timestep)])
        #Pack widget frames
        self.speciesLabel.place(relwidth=1.0, relheight=1/6)
        self.speciesComboBox.place(relwidth=1.0, relheight=1/6, rely=1/6)
        self.startLabel.place(relwidth=1.0, relheight=1/6, rely=2/6)
        self.startTime.place(relwidth=1.0, relheight=1/6, rely=3/6)
        self.lengthLabel.place(relwidth=1.0, relheight=1/6, rely=4/6)
        self.lengthEntry.place(relwidth=1.0, relheight=1/6, rely=5/6)
        #Widget packing
        self.inputFrame.place(relwidth=1.0, relheight=0.75)
        self.calendar.place(relwidth=1.0, relheight=0.2, rely=0.8)
        #Pack widget and button frame together
        self.pack_frames({self.widgetFrame:[1,0.9,0,0],
                          self.buttonFrame:[1,0.1,0,0.9]})
        self.show()
        
    def on_okay(self):
        desiredSpecies = self.speciesComboBox.get()
        huntDate = datetime.strptime(self.calendar.get_date(), "%m/%d/%y")
        huntDate = self.huntDate+timedelta(minutes = int(self.startTime.get().split(":")[0])*60+int(self.startTime.get().split(":")[1]))
        huntLength = int(self.lengthEntry.get())
        self.result = {"Species":desiredSpecies,"Date":huntDate,"Time Length":huntLength}
        self.close_dialog()




