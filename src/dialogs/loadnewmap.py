from dialogs.templatedialog import DialogTemplate
from ttkbootstrap import Frame, Label, Entry, Progressbar
import ttkbootstrap.validation as ttkval
from utils import validate_coord
from os.path import join as ospathjoin
from os import mkdir as osmkdir
from tkinter import IntVar
from tkintermapview import OfflineLoader
from csv import writer as csvwriter


class LoadNewMapDialog(DialogTemplate):
    """
    Class to load a new map into the system

    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param data_directory: The directory where the new map information will be stored
    :type data_directory: str
    """

    def __init__(self, main_window, data_directory):
        super().__init__(main_window)
        self.top.geometry("400x150")
        self.top.title("Create Map")
        self.dataDirectory = data_directory
        # Create entry boxes and labels
        self.labelFrame = Frame(self.widgetFrame)
        self.entryFrame = Frame(self.widgetFrame)
        self.nameEntry = Entry(self.entryFrame)
        self.topLeftCoordEntry = Entry(self.entryFrame)
        self.bottomRightCoordEntry = Entry(self.entryFrame)
        # Labels
        self.nameLabel = Label(self.labelFrame, text="Property Name:")
        self.topLeftCoordLabel = Label(self.labelFrame, text="Top Left Coordinate:")
        self.bottomRightCoordLabel = Label(
            self.labelFrame, text="Bottom Right Coordinate:"
        )
        # Add items to grid
        self.nameLabel.place(relwidth=1.0, relheight=1 / 3)
        self.topLeftCoordLabel.place(relwidth=1.0, relheight=1 / 3, rely=1 / 3)
        self.bottomRightCoordLabel.place(relwidth=1.0, relheight=1 / 3, rely=2 / 3)
        # Entry placing
        self.nameEntry.place(relwidth=1.0, relheight=1 / 3)
        self.topLeftCoordEntry.place(relwidth=1.0, relheight=1 / 3, rely=1 / 3)
        self.bottomRightCoordEntry.place(relwidth=1.0, relheight=1 / 3, rely=2 / 3)
        # Frame Packing and Positioning
        self.labelFrame.place(relwidth=0.5, relheight=1.0)
        self.entryFrame.place(relwidth=0.5, relheight=1.0, relx=0.5)
        self.pack_frames(
            {self.widgetFrame: [1, 0.8, 0, 0], self.buttonFrame: [1, 0.2, 0, 0.8]}
        )
        ttkval.add_validation(self.topLeftCoordEntry, validate_coord)
        ttkval.add_validation(self.bottomRightCoordEntry, validate_coord)
        self.show()

    def on_okay(self):
        """
        Called when the okay button is pushed. Creates all the necessary folders to store the new map and all the markers
        """
        # Load in the map contents and add them to our database
        if not self.topLeftCoordEntry.state() == ():
            return
        if not self.bottomRightCoordEntry.state() == ():
            return
        tileServers = {
            "map": "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
            "satellite": "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
        }
        # tileServers = {"map":"https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga"}

        topLeftLat = float(self.topLeftCoordEntry.get().split(",")[0])
        topLeftLong = float(self.topLeftCoordEntry.get().split(",")[1].strip())
        bottomRightLat = float(self.bottomRightCoordEntry.get().split(",")[0])
        bottomRightLong = float(self.bottomRightCoordEntry.get().split(",")[1].strip())
        name = self.nameEntry.get()
        self.result = name
        self.loaders = []

        # Create required folders inside the new location
        osmkdir(ospathjoin(self.dataDirectory, name))
        osmkdir(ospathjoin(self.dataDirectory, name, "db"))
        osmkdir(ospathjoin(self.dataDirectory, name, "notes"))
        osmkdir(ospathjoin(self.dataDirectory, name, "pictures"))

        self.progressPercent = IntVar(self.top, value=0)
        self.widgetFrame.place_forget()
        self.progressLabel = Label(
            self.top, text="Downloading maps...", anchor="center"
        )
        self.progressbar = Progressbar(
            self.top, variable=self.progressPercent, mode="determinate", maximum=100
        )
        self.progressLabel.pack(fill="both", expand=True)
        self.progressbar.pack(fill="both", expand=True)
        for server in tileServers:
            database_path = ospathjoin(self.dataDirectory, name, "db", server + ".db")
            self.loaders.append(
                OfflineLoader(path=database_path, tile_server=tileServers[server])
            )
            self.loaders[-1].save_offline_tiles(
                (topLeftLat + 0.01, topLeftLong - 0.01),
                (bottomRightLat - 0.01, bottomRightLong + 0.01),
                6,
                19,
            )
        self.percent = 0
        self.top.after(100, self.update_progress_bar)

        with open(
            ospathjoin(self.dataDirectory, name, "db", "data.csv"), "w", newline=""
        ) as csvfile:
            writer = csvwriter(csvfile)
            writer.writerows(
                [
                    [
                        bottomRightLat + abs(bottomRightLat - topLeftLat) / 2,
                        topLeftLong + abs(topLeftLong - bottomRightLong) / 2,
                    ],
                    [
                        topLeftLat + 0.01,
                        topLeftLong - 0.01,
                        bottomRightLat - 0.01,
                        bottomRightLong + 0.01,
                    ],
                    [
                        topLeftLat,
                        topLeftLong,
                        bottomRightLat,
                        topLeftLong,
                        bottomRightLat,
                        bottomRightLong,
                        topLeftLat,
                        bottomRightLong,
                    ],
                ]
            )

    def update_progress_bar(self):
        """
        Updates the progress bar when downloading a map
        """
        for loader in self.loaders:
            self.percent += loader.get_progress()
        self.percent /= len(self.loaders)
        # print(self.percent)
        self.progressPercent.set(self.percent)
        if self.percent < 100:
            self.top.after(100, self.update_progress_bar)
        else:
            self.close_dialog()
