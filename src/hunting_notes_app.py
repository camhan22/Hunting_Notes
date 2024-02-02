import utils
import haversine
import subprocess
import multiprocessing
from os import rmdir as osrmdir
from os import mkdir as osmkdir
from os import listdir as oslistdir
from os import remove as osremove
from os.path import join as ospathjoin
from os.path import exists as ospathexists
from shutil import move as shutilmove
from csv import reader as csvreader
from csv import writer as csvwriter
from tkintermapview import TkinterMapView
from tkinter import messagebox, StringVar, BooleanVar
from ttkbootstrap import Style, Window
from ttkbootstrap.tooltip import ToolTip
from sidebar.sidebar import Sidebar
from optionbar.optionbar import OptionBar
from dialogs.propertyselect import PropertySelectDialog
from dialogs.addmarker import AddMarkerDialog
from dialogs.addmarkernote import AddMarkerNoteDialog
from dialogs.addmarkerimages import AddMarkerImagesDialog
from dialogs.noteviewer import NoteViewer
from dialogs.hunt import HuntDialog
from dialogs.trainanimalfinder import AnimalFinderTrainingDialog
from dialogs.infobox import InfoBox
from dialogs.resultsviewer import AnimalFinderResults
from dialogs.weatherreport import WeatherReportDialog 
from markers import Marker

class HuntingNotesApp():
    """
    Class to contain all the functions needed to run the app
    
    :param main_window: The main window of the system
    :type main_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Frame, tkiner.Tk
    :param logger: The logger that will be used to store information on how the app is running
    :type logger: logging.Logger
    :param weather_fields: The list of weather fields to use in the app
    :type weather_fields: list[str]
    :param species_classes: The list of species that are available to choose from
    :type species_classes: list[str]
    """
    def __init__(self, main_window, logger, weather_fields, species_classes):
        self.logger = logger
        self.logger.info("App Started")
        self.weatherFields = weather_fields
        self.speciesClasses = species_classes
        self.root = main_window
        self.dataDirectory = utils.resource_path("Property Data", file_name=__file__) #for app making, comment line below
        
        #Class Data
        self.markers = []
        self.currentMarker = None
        
        #Call a function when the user closes the main window
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
        #Read in the settings and apply them
        self.settings = self.read_settings()
        
        try:
            Style().theme_use(self.settings["Theme"])
        except KeyError:
            self.logger.warning("Theme not selected, defaulting to \"darkly\"")
            Style().theme_use("darkly")
    
        #Select the property to be used
        try:
            self.database = self.settings["Last Map"]
            #Set common used paths
            self.databaseFolder = ospathjoin(self.dataDirectory, self.database,"db")
            if not ospathexists(self.databaseFolder): #Check that the database actually exists or we need to change it
                self.change_property()
            else:
                self.notesPath = ospathjoin(self.dataDirectory, self.database,"notes")
                self.imagesPath = ospathjoin(self.dataDirectory, self.database,"pictures")
                self.create_map()
        except KeyError: #If the "Last Map" setting doesn't exist, select a new property
            self.change_property()
        
        #Options menu
        settingsIconPath = ospathjoin(utils.resource_path("",__file__),"Resources","settings_icon.png")
        self.optionBar = OptionBar(self.root,side="right", frame_place_properties={"relheight":0.1,"relwidth":0.2},
                                   expand_button_properties={"image":settingsIconPath, "zoom":0.03},
                                   expand_button_place_properties={"relx":0.02, "rely":0.02, "relwidth":0.05,"relheight":0.05})
        self.themeVariable = StringVar(value=self.settings["Theme"])
        self.optionBar.add_combobox("Theme", Style().theme_names(), self.settings["Theme"], self.check_theme, self.themeVariable, place_properties={"relheight":0.44})                       
        self.satelliteVar = BooleanVar(value=self.settings["Satellite"])
        self.optionBar.add_checkbutton("Satellite", self.change_map_type, 
                                       properties={"style":"Roundtoggle.Toolbutton","variable":self.satelliteVar},
                                       place_properties={"relheight":0.56, "relx":0.4})
        
        #Sidebar Menu
        self.sidebar = Sidebar(self.root, 0.025, 0.3, side="left")
        #Hunt
        self.sidebar.add_menu_tab("Hunt", tab_place_properties={"relheight":0.1})
        self.sidebar.add_menu_button("Go Hunt", self.go_hunt, "Hunt")
        self.sidebar.add_menu_button("Weather Report", self.weather_report, "Hunt")
        #Add data menus
        self.sidebar.add_menu_tab("Markers", tab_place_properties={"relheight":0.2})        
        self.sidebar.add_menu_button("Add Images", self.add_images, "Markers")
        self.sidebar.add_entry("Add Marker", "New Marker Coordinates:","Markers", self.add_marker)
        #Notes menus
        self.sidebar.add_menu_tab("Notes", tab_place_properties={"relheight":0.2})
        self.sidebar.add_menu_button("View Notes", self.view_notes, "Notes")
        self.sidebar.add_menu_button("Add Note", self.create_note, "Notes")
        self.sidebar.add_menu_button("Delete Abandoned Notes", self.delete_abandoned_notes, "Notes")
        #Change property
        self.sidebar.add_menu_tab("Property", tab_place_properties={"relheight":0.1})
        self.sidebar.add_menu_button("Change Property", self.change_property, "Property")
        #Retrain
        self.sidebar.add_menu_tab("Train Models", tab_place_properties={"relheight":0.2})
        self.sidebar.add_menu_button("Train Animal Detector", self.train_animal_detector, "Train Models")
        self.sidebar.add_menu_button("Train Animal Finder", self.train_animal_finder, "Train Models")
        #Extras
        self.sidebar.add_menu_tab("Extras", tab_place_properties={"relheight":0.1})
        self.sidebar.add_menu_button("Image Annotator", self.start_image_annotator, "Extras")
        #Help
        self.sidebar.add_menu_tab("Help", tab_place_properties={"relheight":0.1})
        #TODO#
        #Add help tab with documentation
        
        #Show the main window since we are done setting it up
        self.root.place_window_center()
        self.root.deiconify()

    def create_map(self):
        """
        Creates the tkintermapview object with the correct database based on whether satellite mode is chosen or not
        """
        if hasattr(self,"map_widget"):    
            self.map_widget.destroy()
            
        if self.settings["Satellite"]:
            self.map_widget = TkinterMapView(self.root, width=1000, height=700,
                                         database_path=ospathjoin(self.databaseFolder, "satellite.db"), use_database_only=True, max_zoom=19)
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=19)
        else:
            self.map_widget = TkinterMapView(self.root, width=1000, height=700,
                                         database_path=ospathjoin(self.databaseFolder, "map.db"), use_database_only=True, max_zoom=19)
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=19)
        self.map_widget.set_zoom(self.map_widget.zoom-3)
        self.map_widget.set_zoom(self.map_widget.zoom+3)
        self.map_widget.add_right_click_menu_command(label="Add Marker", command=self.add_marker, pass_coords=False)
        self.map_widget.add_right_click_menu_command(label="Delete Marker", command=self.delete_marker, pass_coords=False)
        self.map_widget.add_left_click_map_command(self.left_click_event)
            
        #Setup the map and place the widget
        self.setup_map()
      
    def setup_map(self):
        """
        Sets up the map with the property boundry if on a regular mapview and loads the markers onto the map
        """
        with open(ospathjoin(self.dataDirectory, self.databaseFolder,"data.csv")) as csvfile:
            self.propertyLineCorners = []
            reader = csvreader(csvfile)
            row = reader.__next__()
            self.homePosition = (float(row[0]), float(row[1])) #Keep the home position since we need this for the weather data
            row = reader.__next__()
            self.boundingBox = ((float(row[0]), float(row[1])),(float(row[2]), float(row[3])))
            row = reader.__next__()
            for i in range(0, len(row), 2):
                self.propertyLineCorners.append(tuple([float(row[i]), float(row[i+1])]))
        self.map_widget.set_position(*self.homePosition)
        self.map_widget.set_zoom(10) #This is a hack to get the images to work properly and not get image tearing
        self.map_widget.fit_bounding_box(*self.boundingBox)
        if not self.settings["Satellite"]:
            self.propertyBorder = self.map_widget.set_polygon(self.propertyLineCorners, name="PropertyBorder", fill_color=None)
        self.map_widget.place(relwidth=1, relheight=1)
        self.map_widget.lower() #Make it lower than all other widgets
        self.load_markers()

    def load_markers(self):
        """
        Loads the markers from the markers.csv file
        """
        try:
            with open(ospathjoin(self.dataDirectory, self.databaseFolder, "markers.csv")) as csvfile:
                reader = csvreader(csvfile)
                for row in reader:
                    if not row == []:
                        newMarker = Marker(self.map_widget, float(row[0]), float(row[1]), row[2], row[3], self.dataDirectory, self.database)
                        if self.settings["Satellite"]:
                            newMarker.change_color(text_color="white")
                        self.markers.append(newMarker)
        except FileNotFoundError:
            self.logger.info("No marker file exists, creating one")
            with open(ospathjoin(self.dataDirectory, self.databaseFolder,"markers.csv"), "w") as csvfile:
                pass
 
    def left_click_event(self, coords=None):
        """
        Called when the user left clicks the mouse
    
        :param coords: The coordinates that the mouse was left clicked at
        :type coords: tuple(lat, long) or None
        """
        markerHighlighted = False
        for marker in self.markers:
            if marker.justHighlighted:
                self.currentMarker = marker
                markerHighlighted = True
            marker.unhighlight()
        if not markerHighlighted:
            self.currentMarker = None
        
    def add_marker(self, event=None):
        """
        Adds a marker to the map, creates necessary folders, and adds it to the markers.csv file
    
        :param event: The event that called this function
        :type event: tkinter.Event
        """
        gotCoords = False
        if event is not None:
            noneArgs = ["-1","-1","","","","","Final",event.widget]
            self.valCoordToolTip = ToolTip(event.widget,"Format: latitude, longitude (eg. -42.5464, -83.5734)")
            if not utils.validate_coord(*noneArgs):
                event.widget.configure(style="danger.TEntry")
                self.valCoordToolTip.show_tip()
                return
            else:
                event.widget.configure(style="TEntry")
                self.valCoordToolTip.hide_tip()
                gotCoords = True
            
        if gotCoords:
            markerDialog = AddMarkerDialog(self.root, event.widget.get())
        else:
            markerDialog = AddMarkerDialog(self.root)
        if markerDialog.result is None:
            return
        newMarker = Marker(self.map_widget, markerDialog.result["lat"], markerDialog.result["long"], markerDialog.result["name"], markerDialog.result["markerType"], self.dataDirectory, self.database)
        self.markers.append(newMarker)
        if markerDialog.result["markerType"] == "Camera":
            if not ospathexists(ospathjoin(self.dataDirectory,self.database,"pictures", markerDialog.result["name"])):
                osmkdir(str(ospathjoin(self.dataDirectory,self.database,"pictures", markerDialog.result["name"])))
        if not ospathexists(ospathjoin(self.dataDirectory,self.database,"notes", markerDialog.result["name"])):
            osmkdir(str(ospathjoin(self.dataDirectory,self.database,"notes", markerDialog.result["name"])))
        with open(ospathjoin(self.dataDirectory, self.databaseFolder,"markers.csv"), "a", newline="") as csvfile:
            writer = csvwriter(csvfile)
            writer.writerow([str(markerDialog.result["lat"]), str(markerDialog.result["long"]), markerDialog.result["name"], markerDialog.result["markerType"]]) #Add the marker to the data file

    def delete_marker(self):
        """
        Deletes the currently selected marker and moves any notes and images to the abandoned folder
        """
        markers = []
        if self.currentMarker is None: #If there is no current marker selected, do nothing
            return
        markerName = self.currentMarker.name
        #Check for the abandoned folder in the pictures and notes, if they don't exist, create them
        if not ospathexists(ospathjoin(self.dataDirectory, self.database,"pictures", "abandoned")):
            osmkdir(ospathjoin(self.dataDirectory, self.database,"pictures", "abandoned"))
        if not ospathexists(ospathjoin(self.dataDirectory, self.database,"notes", "abandoned")):
            osmkdir(ospathjoin(self.dataDirectory, self.database,"notes", "abandoned"))
        #Check for pictures folder and remove it
        if ospathexists(ospathjoin(self.dataDirectory, self.database,"pictures", markerName)):
            if not len(oslistdir(ospathjoin(self.dataDirectory, self.database,"pictures", markerName))) == 0:
                for file in oslistdir(ospathjoin(self.dataDirectory, self.database,"pictures", markerName)):
                    shutilmove(ospathjoin(self.dataDirectory, self.database,"pictures",markerName, file), ospathjoin(self.dataDirectory, self.database+"_pictures", "abandoned"))    
            osrmdir(ospathjoin(self.dataDirectory, self.database,"pictures", markerName))
        #Check for notes folder and remove it 
        if ospathexists(ospathjoin(self.dataDirectory, self.database,"notes", markerName)):
            if not len(oslistdir(ospathjoin(self.dataDirectory, self.database,"notes", markerName))) == 0:
                for file in oslistdir(ospathjoin(self.dataDirectory, self.database,"notes", markerName)):
                    shutilmove(ospathjoin(self.dataDirectory, self.database,"notes",markerName, file), ospathjoin(self.dataDirectory, self.database+"_notes", "abandoned"))    
            osrmdir(ospathjoin(self.dataDirectory, self.database,"notes", markerName))
        #Read current markers from file
        with open(ospathjoin(self.dataDirectory, self.databaseFolder,"markers.csv"), "r") as csvfile:
            reader = csvreader(csvfile)
            for row in reader:
                if not row == []:
                    markers.append(row)
            markers.pop(self.markers.index(self.currentMarker)) #Remove the one we want to remove

            #Write the intact rows back to file
        with open(ospathjoin(self.dataDirectory, self.databaseFolder,"markers.csv"), "w", newline="") as csvfile:
            writer = csvwriter(csvfile)
            writer.writerows(markers)
            
        #Delete the current marker from the list stored in the app
        self.markers.pop(self.markers.index(self.currentMarker)) #Remove the currently selected marker from the list
        self.currentMarker.destroy() #Delete the marker from the map
        self.currentMarker = None

    def delete_abandoned_notes(self):
        """
        Deletes any abandoned notes permenantly
        """
        if not len(oslistdir(ospathjoin(self.dataDirectory, self.database,"notes", "Abandoned"))) == 0:
            for file in oslistdir(ospathjoin(self.dataDirectory, self.database,"pictures", self.currentMarker.name)):
                osremove(file) #delete each file in the abandoned folder
            messagebox.info("Successfully deleted all abandoned notes")
            self.logger.info("User successfully deleted all abandoned notes")
        else:
            messagebox.info("No abandoned notes to delete")
            self.logger.error("User tried to delete abandoned notes when none existed")

    def view_notes(self):
        NoteViewer(self.root, self.notesPath)

    def create_note(self):
        """
        Creates a note at the selected marker
        """
        if self.currentMarker is None:
            return
        markerNote = AddMarkerNoteDialog(self.root, self.currentMarker)
        if markerNote.result == "Success":
            messagebox.showinfo("Success", "Successfully saved the note")
        elif not markerNote.result == "Cancelled":
            messagebox.showinfo("Failed", markerNote.result)     

    def add_images(self):
        """
        Called to add images to a camera
        """
        if self.currentMarker is None:
            return
        if not self.currentMarker.type == "Camera":
            messagebox.showerror("Not Camera", "Can only add images to a camera")
            self.logger.error("User tried to add images to a non-camera item")
            return
        AddMarkerImagesDialog(self.currentMarker)

    def go_hunt(self):
        """
        Called when the user wants to determine the best place to go on a certain day
        """
        self.infoBox = InfoBox(self.root, "Loading Model Data", "Please wait while model library loads")
        from animal_regression.animal_finder import AnimalFinder #Dynamically import the library, used to get faster startup time until you try to go hunting
        self.infoBox.close_info_box()

        self.huntDialog = HuntDialog(self.root)
        if self.huntDialog.result is None:
            self.logger.error("User cancelled the hunt dialog")
            return
        
        self.infoBox = InfoBox(self.root, "Loading Model Data", "Please wait while model data loads")
        self.finder = AnimalFinder(self.root, self.dataDirectory, self.database, self.weatherFields, self.homePosition, self.speciesClasses, self.huntDialog.result["Species"], self.firstWeekDay)
        
        if self.finder.isLoading:
            self.finderLoaderTimer = utils.RepeatTimer(1,self.check_finder_loaded, ["Repeating"])
            self.finderLoaderTimer.start() #Create and start a timer to check when the finder has fully loaded
        else:
            self.predict_and_process() #If the finder model was already trained, jump straight to the prediction step

    def check_finder_loaded(self):
        """
        Checks to see if the finder model is loading(training) (Allows non-blocking execution of the main display)
        """
        if self.finder.isLoading:
            return
        self.finderLoaderTimer.cancel()
        self.infoBox.close_info_box()
        self.predict_and_process()

    def predict_and_process(self):
        """
        Predicts which camera sees the mostactivity during the time period selected. Displays the results in a dialog.
        """
        bestSum = -10000000000
        bestCamera = None
        self.infoBox = InfoBox(self.root, "Predicting", "Please wait while model predicts the best time and location")
        predictions = self.finder.predict(self.huntDialog.result["Date"], self.huntDialog.result["Time Length"], self.timeInterval)
        for camera in predictions.keys():
            tempSum = sum(predictions[camera]["Predictions"])
            if  tempSum > bestSum:
                bestSum = tempSum
                bestCamera = camera
        for marker in self.markers:
            if marker.name == bestCamera:
                bestCameraCoords = (marker.lat, marker.long)
        bestLocation, bestDistance  = self.find_best_stand(bestCameraCoords)
        self.infoBox.close_info_box()
        AnimalFinderResults(self.root, self.huntDialog.result["Species"], bestDistance, bestLocation)

    def find_best_stand(self, best_camera_coords: tuple = (0,0)):
        """
        Finds the best stand based on pure distance from the most active camera during the time period selected
    
        :param best_camera_coords: The GPS coordinates of the most active camera
        :type best_camera_coords: tuple(lat, long)
    
        :returns: The name of the best stand location based on distance and the distance to that standfrom the camera
        :rtype: tuple(stand name, distance)
        """
        bestDistance = 100000000
        bestLocation = None
        for marker in self.markers:
            if marker.type == "Stand" or marker.type == "Point of Interest":
                distance = haversine.haversine(best_camera_coords, (marker.lat, marker.long), unit="mi")
                if distance < bestDistance:
                    bestDistance = distance
                    bestLocation = marker.name

        return (bestLocation, int(bestDistance*1760)) #return the distance in yds

    def train_animal_detector(self):
        """
        Trains the animal detector model to find different species in an image
        """
        self.detectorInfoBox = InfoBox(self.root, "Training Animal Detector", "Please wait while detector data loads")
        self.logger.info("User is training the animal detector")
        from animal_detector.animal_detector import HuntingAnimalDetector
        self.detectorInfoBox.close_info_box()
        HuntingAnimalDetector(self.root, True)

    def train_animal_finder(self):
        """
        Trains the animal finder model used to locate animals on the property
        """
        self.finderInfoBox = InfoBox(self.root, "Training Animal Finder", "Please wait while finder data loads")
        from animal_regression.animal_finder import AnimalFinder #Dynamically import the library, used to get faster startup time until you try to go hunting
        self.finderInfoBox.close_info_box()
        finder_train_dialog = AnimalFinderTrainingDialog(self.root)
        if finder_train_dialog.result is None:
            return
        AnimalFinder(self.root, self.dataDirectory, self.database, self.weatherFields, self.homePosition, self.speciesClasses, finder_train_dialog.result)

    def change_property(self):
        """
        Changes the property to another one, calls up the dialog
        """
        changePropertyDialog = PropertySelectDialog(self.root,self.dataDirectory)
        if changePropertyDialog.result is None:
            return
        self.database = changePropertyDialog.result
        self.notesPath = ospathjoin(self.dataDirectory, self.database,"notes")
        self.imagesPath = ospathjoin(self.dataDirectory, self.database,"pictures")
        self.databaseFolder = ospathjoin(self.dataDirectory, self.database,"db")
        self.create_map()

    def start_image_annotator(self):
        """
        Starts up the image annotator program in a seperate process
        """
        annotatorExePath = utils.resource_path("Image Annotator App.exe", __file__)
        subprocess.run(annotatorExePath, capture_output=True)

    def weather_report(self):
        """
        Shows a report of the weather for the day
        """
        #WeatherReportDialog()
        pass
    
    def check_theme(self, event=None):
        """
        Called when the theme changes
    
        :param event: The event that made this call
        :type event: tkinter.Event or None
        """
        theme = self.themeVariable.get()
        Style().theme_use(theme)
        self.save_settings("Theme", theme)
    
    def change_map_type(self):
        """
        Changes the map type from regular map to satellite
        """
        self.settings["Satellite"] = self.satelliteVar.get()
        self.create_map()
        self.save_settings("Satellite", self.satelliteVar.get())
    
    def read_settings(self):
        """
        Reads in the current settings from the settings.txt file
    
        :returns: A dictionary of the current settings
        :rtype: dict
        """
        filePath = utils.resource_path("settings.txt", file_name=__file__)
        settings = {}
        if ospathexists(filePath):
            with open(filePath, "r") as settingFile:
                data = settingFile.readlines()
                for setting in data:
                    setting = setting.split("=")
                    setting[1] = setting[1].replace("\n","")
                    if not setting == []:
                        if setting[1] == "True":
                            setting[1] = True
                        if setting[1] == "False":
                            setting[1] = False
                        settings.update({setting[0]:setting[1]})
        return settings

    def save_settings(self, setting_to_change=None, value=None):
        """
        Saves a setting to the settings.txt file
    
        :param setting_to_change: The setting to change
        :type setting_to_change: str or None
        :param value: The new value the setting will be
        :type value: Any
        """
        filePath = ospathjoin(utils.resource_path("", file_name=__file__),"settings.txt")
        with open(filePath,"w") as settingFile:
            for setting in self.settings.keys():
                if setting_to_change is not None:
                    if setting == setting_to_change:
                        self.settings[setting] = value
                settingFile.write("{0}={1}\n".format(setting,self.settings[setting]))
                
    def close(self):
        """
        Called when the main window is closed. Causes settings to be saved and detroys the root window
        """
        self.settings.update({"Last Map":self.database})
        self.save_settings()
        self.root.destroy()
    
if __name__ == "__main__":
    multiprocessing.freeze_support()
    logger = utils.setup_logger("App", "App.log")
    if not ospathexists(utils.resource_path("Logs", file_name=__file__)):
        osmkdir(utils.resource_path("Logs", file_name=__file__))
    weatherFields = ["Temperature", "Dewpoint", "Humidity","Precipitation","Wind Direction","Wind Speed", "Pressure"]
    speciesDict = {}
    with open(utils.resource_path("species.txt",file_name=__file__)) as txtfile:
        data = txtfile.readlines()
        for index, item in enumerate(data):
            speciesDict.update({item.strip():index})
    mainWindow = Window(hdpi=False)
    mainWindow.geometry(f"{1000}x{700}")
    mainWindow.title("Hunting Notes")
    mainWindow.withdraw()
    
    try:
        app = HuntingNotesApp(mainWindow, logger, weatherFields, speciesDict)
        mainWindow.mainloop()
    except Exception as e:
        logger.error(e)

    
    

    
        