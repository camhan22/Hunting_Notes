from dialogs.templatedialog import DialogTemplate
from dialogs.hunt import HuntDialog
from ttkbootstrap.tableview import Tableview
from weather.weather import Weather
from timezonefinder.timezonefinder import TimezoneFinder
from pandas import DataFrame
import datetime


class WeatherReportDialog(DialogTemplate):
    """
    Class to handle showing the weather report for the selected times to the user

    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param location: The location to get the weather at
    :type location: tuple(lat,long)
    :param hunt_date: The date the user wishes to go hunting. (Defaults to None)
    :type hunt_date: datetime.datetime
    :param hunt_start_time: The start time you want to go hunting at (Defaults to None)
    :type hunt_start_time: str
    :param hunt_length: The length of time we are going hunting for (Defaults to None)
    :type hunt_length: int (Units of hours)
    :param time_interval: The interval of time between data points to show (Defaults to 15)
    :type time_interval: int (Units of minutes)
    :param units: The units to get the weather in ("Imperial" or "Metric")
    :type units: str

    .. todo::

       * Add conversions from metric to imperial
    """

    def __init__(
        self,
        main_window,
        location: tuple,
        hunt_date: datetime.datetime = None,
        hunt_start_time: str = None,
        hunt_length: int = None,
        time_interval: int = 15,
        units: str = "Imperial",
    ):
        super().__init__(main_window, False, True)
        self.location = location
        self.weatherFields = [
            "Weather Code",
            "Temperature",
            "Real Feel",
            "Humidity",
            "Wind Speed",
        ]
        self.date = hunt_date
        self.startTime = hunt_start_time
        self.timeLength = hunt_length
        self.interval = time_interval
        self.unit = units
        self.futureWeather = Weather(self.location, "1h", self.unit)

        dialog = HuntDialog(
            main_window, self.date, self.startTime, self.timeLength, time_interval
        )
        if dialog.result is not None:
            self.date = dialog.result["Date"]
            self.timeLength = dialog.result["Time Length"]
        else:
            return

        self.futureWeather.get_forecast(
            datetime.datetime(self.date.year, self.date.month, self.date.day),
            datetime.datetime(self.date.year, self.date.month, self.date.day, 0)
            + datetime.timedelta(days=1),
            TimezoneFinder().timezone_at(lat=self.location[0], lng=self.location[1]),
            self.weatherFields,
        )

        # Create the data structure to hold all the data
        data = []
        for timeIndex in [
            self.date + datetime.timedelta(minutes=minuteIndex)
            for minuteIndex in range(0, self.timeLength * 60, time_interval)
        ]:
            data.append(
                [
                    timeIndex.strftime("%H:%M"),
                    *self.futureWeather.get_data(timeIndex, self.weatherFields),
                ]
            )

        # Create the dataframe to hold all the data
        self.times = [
            str(datetime.datetime.fromtimestamp(time))
            for time in range(
                int(self.date.timestamp()),
                int(
                    (self.date + datetime.timedelta(hours=self.timeLength)).timestamp()
                ),
                int(3600 / (60 / self.interval)),
            )
        ]
        # Create the data frame
        self.dataFrame = DataFrame(
            data,
            columns=["Time", *self.weatherFields],
            index=self.times,
        )

        # Load the weather data into the table and pack the table widegt into the widget frame
        self.generate_table()

        # Create the widgets
        self.pack_frames({self.widgetFrame: [1, 1, 0, 0]})
        self.show(no_wait=True)

    def generate_table(self):
        """
        Gathers the weather data into a pandas.DataFrame for displaying in a ttkboostrap.Tableview
        """
        columnData = ["Time", *self.weatherFields]
        rowData = []
        # Gather the data for each timestep into a 2D list
        for time in self.times:
            row = [self.dataFrame["Time"][time]]
            for header in self.weatherFields:
                row.append(self.dataFrame[header][time])
            rowData.append(row)

        # Create the table
        table = Tableview(
            self.widgetFrame,
            coldata=columnData,
            rowdata=rowData,
            autofit=True,
        )

        table.pack(fill="both", expand=True)
        self.top.update_idletasks()
        self.top.minsize(table.winfo_reqwidth(), 100)
        self.top.geometry(
            str(table.winfo_reqwidth()) + "x" + str(table.winfo_reqheight())
        )
