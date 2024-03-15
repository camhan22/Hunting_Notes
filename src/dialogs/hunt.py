from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Frame, Label, Entry, Combobox, DateEntry
from datetime import datetime
from datetime import timedelta


class HuntDialog(DialogTemplate):
    """
    Class to handle the dialog that finds the best place to hunt

    :param main_window: The window this pop-up should be in front of
    :type main_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param date: The default date to display if one exists (Default is None)
    :type date: datetime.datetime
    :param start_time: The starting time to go hunting (Default is None)
    :type start_time: str
    :param length: The length of time to hunt (Default is None)
    :type length: int
    :param timestep: The time between data points when gathering data (Defaults to 15 minutes)
    :type timestep: int (Units of minutes)
    :param first_week_day: The first day of the week (Defaults to 6 for sunday)
    :type first_week_day: int
    """

    def __init__(
        self,
        main_window,
        date: datetime = None,
        start_time: str = None,
        length: int = None,
        timestep: int = 15,
        first_week_day: int = 6,
    ):
        super().__init__(main_window)
        self.top.title("Hunt")
        self.inputFrame = Frame(self.widgetFrame)
        self.top.geometry("300x200")
        if date is None: #If no date is set, then default it to the current date instead
            date = datetime.now()
            
        self.calendar = DateEntry(
            self.widgetFrame,
            firstweekday=first_week_day,
            startdate=date
        )

        self.lengthLabel = Label(self.inputFrame, text="Hours to hunt", anchor="center")
        self.lengthEntry = Entry(self.inputFrame, justify="center")
        if length is not None:
            self.lengthEntry.delete(0, "end")
            self.lengthEntry.insert(0, length)
        self.startLabel = Label(self.inputFrame, text="Starting time", anchor="center")
        self.startTime = Combobox(self.inputFrame, justify="center", state="readonly")
        if start_time is not None:
            self.startTime.set(start_time)
        else:
            self.startTime.set("")
        self.startTime.configure(
            values=[
                "{0:02d}:{1:02d}".format(int(time / 60), int(time % 60))
                for time in range(0, 1440, timestep)
            ]
        )
        # Pack widget frames
        self.startLabel.place(relwidth=1.0, relheight=1 / 4)
        self.startTime.place(relwidth=1.0, relheight=1 / 4, rely=1 / 4)
        self.lengthLabel.place(relwidth=1.0, relheight=1 / 4, rely=2 / 4)
        self.lengthEntry.place(relwidth=1.0, relheight=1 / 4, rely=3 / 4)
        # Widget packing
        self.inputFrame.place(relwidth=1.0, relheight=0.7)
        self.calendar.place(relwidth=1.0, relheight=0.3, rely=0.7)
        # Pack widget and button frame together
        self.pack_frames(
            {self.widgetFrame: [1, 0.8, 0, 0], self.buttonFrame: [1, 0.2, 0, 0.8]}
        )
        self.show()

    def on_okay(self):
        """
        Called when the okay button is pushed.
        """
        huntDate = datetime.strptime(self.calendar.entry.get(), "%m/%d/%Y")
        huntDate = huntDate + timedelta(
            minutes=int(self.startTime.get().split(":")[0]) * 60
            + int(self.startTime.get().split(":")[1])
        )
        huntLength = int(self.lengthEntry.get())
        self.result = {
            "Date": huntDate,
            "Start Time": self.startTime.get(),
            "Time Length": huntLength,
        }
        self.close_dialog()
