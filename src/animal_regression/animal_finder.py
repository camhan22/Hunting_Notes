from sklearn.svm import OneClassSVM
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import make_pipeline
from weather.weather import Weather
from os.path import join as ospathjoin
from os.path import exists as ospathexists
from os import listdir as oslistdir
from os import mkdir as osmkdir
from csv import reader as csvreader
from exif import Image
from datetime import datetime
from datetime import timedelta
from pandas import DataFrame
import joblib
import utils
from timezonefinder.timezonefinder import TimezoneFinder
import pytz


class AnimalFinder:
    """
    Takes in current data to predict how many deer you should see at each stand location

    :param root: The main window that this belongs to
    :type root: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param data_directory: The directory to look for any data the finder might need
    :type data_directory: str
    :param db_name: The name of the database that is being used
    :type db_name: str
    :param weather_fields: The list of fields to use for the weather when using the model
    :type weather_fields: list[str]
    :param property_center: The center of the property. We assume the property is small enough the variation in weather is negligible
    :type property_center: tuple(lat, long)
    :param species_classes: The list of species we can choose to hunt
    :type species_classes: list[str]
    :param desired_species: The species we want to hunt (Defaults to Deer)
    :type desired_species: str
    :param first_week_day: The day to consider as the first of the week. (Defaults to sunday)
    :type first_week_day: str
    :param retrain: Whether to force a model retrain or not (Defaults to False)
    :type retrain: bool

    .. note::

       The OneClassSVM model may not be the best model for this type of problem, especially as other variables are added.

    .. note::

       * This system assumes the weather is the same across the entire property. Most changes are going to be insignificant to most species and not worth the added complexity
       * The weather API only has a resolution of about 1-2km which would correspond to about 247 - 1000 acres. Most people are not hunting on land that large

    .. todo::

       * Remove some species from the dialog to be able to hunt for (Shouldn't allow hunting for humans)
       * Add in predators since that will affect any patterns animals may have.
       * Change algorithm to use a count of animals instead of whether some exist or not, since two areas may have animals but one may have more leading to better oppurtunities.
       * Add code to switch between metric and imperial units. Most likely, the models will always be in imperial units and metric will need to be converted over
       * Find the oldest date to get historical weather by the pictures loaded
       * Save the weather data externally so we don't need to fetch it everytime
       * Potentially add a system to create a weather grid depending on how large it is. Some state lands have 1000's of acres to hunt on

    """

    def __init__(
        self,
        root,
        data_directory: str,
        db_name: str,
        weather_fields: list,
        property_center: tuple,
        species_classes: dict,
        desired_species: str = "Deer",
        first_week_day: str = "sunday",
        retrain: bool = False,
    ):
        self.logger = utils.setup_logger("Finder", "Animal Finder.log")
        self.logger.info("Finder Started")
        self.rootWindow = root
        self.dataDirectory = data_directory
        self.modelsFolderPath = utils.resource_path(
            "Models/Finder Models", file_name=__file__
        )
        self.propertyCenter = property_center
        self.database = db_name
        self.detectorThreshold = 0.5
        self.isLoading = False
        self.weatherFields = weather_fields
        self.firstWeekDay = first_week_day
        self.fields = ["Day of Year", "Time of Day", "Weekday", *self.weatherFields]
        self.speciesClasses = species_classes
        self.desiredSpecies = desired_species
        self.timezoneStr = TimezoneFinder().timezone_at(
            lat=property_center[0], lng=property_center[1]
        )
        self.timeZone = pytz.timezone(self.timezoneStr)
        self.newWeather = Weather(
            property_center
        )  # Always train in imperial units no matter what
        # Generate the dictionary of all camera locations in the database including any abandoned images
        self.camerasDict = {}
        self.modelsDict = {}
        with open(
            ospathjoin(self.dataDirectory, self.database, "db", "markers.csv"), "r"
        ) as markercsv:
            reader = csvreader(markercsv)
            for line in reader:
                if not line == []:  # If the line is not blank
                    if line[3] == "Camera":
                        self.camerasDict.update(
                            {line[2]: (line[0], line[1])}
                        )  # Update the stand dictionary with the name and a tuple of the gps coordinates
        self.modelsDict = {}.fromkeys(self.camerasDict.keys())

        if not self.load_model() or retrain:  # We need to train a new model
            self.modelsDict = {}.fromkeys(self.camerasDict.keys())
            for camera in self.modelsDict.keys():
                self.modelsDict.update(
                    {camera: make_pipeline(RobustScaler(), OneClassSVM())}
                )
            self.isLoading = True
            self.trainer = utils.ModelTrainer(
                self.logger,
                "Animal Finder",
                self.load_required_modules,
                self.load_training_data,
                None,
                self.train,
                self.save_models,
            )

    def load_model(self):
        """
        Tries to load the model from the disk.

        :returns: Whether the model loaded correctly or not
        :rtype: bool
        """
        try:
            for camera in self.camerasDict.keys():
                self.modelsDict[camera] = joblib.load(
                    self.modelsDict[camera],
                    open(
                        ospathjoin(
                            self.modelsFolderPath,
                            camera + " " + self.desiredSpecies + ".pkl",
                        ),
                        "rb",
                    ),
                )
        except Exception:
            return False
        return True

    def load_required_modules(self):
        """
        Loads in the required modules needed to train this model

        :returns: The list of modules the system needs before it can train
        :rtype: list[Any]
        """
        from animal_detector.animal_detector import HuntingAnimalDetector

        try:
            self.detector = HuntingAnimalDetector(self.rootWindow)
        except Exception:
            return None
        return [self.detector]

    def load_training_data(self):
        """
        Loads in any training data the model will need
        """
        self.trainingData = {}

        self.imagesPath = ospathjoin(self.dataDirectory, self.database, "pictures")
        
        oldestDate = datetime.now()
        #Look for the oldest date in the pictures, but don't include the abandoned folder
        for location in [folder for folder in oslistdir(self.imagesPath) if not "abandonded" in folder]:
            for imagePath in oslistdir(ospathjoin(self.imagesPath,location)):
                imageDate = datetime.strptime(imagePath.split(".")[0],"%Y_%m_%d_%H_%M_%S")
                if imageDate < oldestDate:
                    oldestDate = imageDate                    

        oldestDate = oldestDate.replace(hour=0, minute=0, second=0, microsecond=0)
        self.oldWeatherData = Weather(
            self.propertyCenter,
        )  # The weather models have a spatial resolution of about 1km. Most properties will be less than that.
        # Also the weather across a couple km probably won't change that much unless you have very moutaineous terrain.
        # This system assumes the weather is the same for the entire property.
        # ANy differences
        # The old weather is only able to get data from 5 days prior, so any pictures earlier than that will not have data
        self.oldWeatherData.get_forecast(
            oldestDate,
            datetime.now(),
            self.timezoneStr,
            self.weatherFields,
        )
        for location in oslistdir(self.imagesPath):
            if not location in self.camerasDict.keys():
                continue
            trainData = []
            countData = []
            for file in oslistdir(ospathjoin(self.imagesPath, location)):
                imageFile = Image(ospathjoin(self.imagesPath, location, file))
                imageDateTime = datetime.strptime(
                    imageFile.datetime_original, "%Y:%m:%d %H:%M:%S"
                )
                animalCount = self.detector.detect_animals(
                    ospathjoin(self.imagesPath, location, file), self.detectorThreshold
                )
                if self.firstWeekDay == "sunday":
                    weekDay = (imageDateTime.weekday() + 1) % 6
                else:
                    weekDay = imageDateTime.weekday()
                minuteOfDay = (
                    imageDateTime.hour * 60 + imageDateTime.minute
                )  # Get the time of the day for the image
                numDayOfYear = imageDateTime.timetuple().tm_yday
                imageWeatherData = self.oldWeatherData.get_data(
                    imageDateTime, self.weatherFields
                )
                trainData.append(
                    [numDayOfYear, minuteOfDay, weekDay, *imageWeatherData]
                )
                countData.append(
                    animalCount.count(self.speciesClasses[self.desiredSpecies])
                )
            self.trainingData.update({location: [trainData, countData]})

    def train(self):
        """
        Trains the model
        """
        for camera in self.modelsDict.keys():
            samples = [
                sample
                for sample, count in zip(
                    self.trainingData[camera][0], self.trainingData[camera][1]
                )
                if count > 0
            ]
            if samples == []:
                print(
                    "Cannot train model due to no observational training data, retrain the animal detector model with better data or more epochs"
                )
                return
            self.modelsDict[camera].fit(samples)

    def save_models(self):
        """
        Saves the model to disk after training
        """
        self.isLoading = False
        for camera in self.modelsDict.keys():
            if not ospathexists(self.modelsFolderPath):
                osmkdir(self.modelsFolderPath)
            joblib.dump(
                self.modelsDict[camera],
                open(
                    ospathjoin(
                        self.modelsFolderPath,
                        camera + " " + self.desiredSpecies + ".pkl",
                    ),
                    "wb",
                ),
            )

    def predict(self, start_time: datetime, time_length: int, time_increment: int = 15):
        """
        Predicts if at a given time and location there will be the desired species

        :param start_time: The time to start the predicition at
        :type start_time: datetime.datetime
        :param time_length: The length of time to predict on
        :type time_length: int (Units of hours)
        :param time_increment: The time between data points (Defaults to 15 minutes)
        :type time_increment: int (Units of minutes)

        :returns: A dictionary containing whether the model saw the desired species or not
        :rtype: dict
        """
        self.newWeather.get_forecast(
            datetime(start_time.year, start_time.month, start_time.day),
            datetime(start_time.year, start_time.month, start_time.day, 0)
            + timedelta(days=1),
            self.weatherFields,
        )
        for camera in self.camerasDict.keys():
            timeData = []
            for timeIndex in [
                start_time + timedelta(minutes=minuteIndex)
                for minuteIndex in range(0, time_length * 60, time_increment)
            ]:
                if self.firstWeekDay == "sunday":
                    weekDay = (timeIndex.weekday() + 1) % 6
                else:
                    weekDay = timeIndex.weekday()
                minuteOfDay = (
                    timeIndex.hour * 60 + timeIndex.minute
                )  # Get the time of the day for the image
                numDayOfYear = timeIndex.timetuple().tm_yday
                timeData.append(
                    [
                        numDayOfYear,
                        minuteOfDay,
                        weekDay,
                        *self.newWeather.get_data(timeIndex, self.weatherFields),
                    ]
                )
            frame = DataFrame(
                timeData,
                columns=self.fields,
                index=[
                    str(datetime.utcfromtimestamp(time))
                    for time in range(
                        int(start_time.timestamp()),
                        int((start_time + timedelta(hours=time_length)).timestamp()),
                        int(3600 / (60 / time_increment)),
                    )
                ],
            )
            self.camerasDict.update({camera: frame.transpose()})
        self.predDict = {}
        for camera in self.camerasDict.keys():
            predicitons = self.modelsDict[camera].predict(
                [
                    self.camerasDict[camera][time].tolist()
                    for time in self.camerasDict[camera]
                ]
            )
            predFrame = DataFrame(
                predicitons,
                columns=["Predictions"],
                index=[
                    str(datetime.fromtimestamp(time))
                    for time in range(
                        int(start_time.timestamp()),
                        int((start_time + timedelta(hours=time_length)).timestamp()),
                        int(3600 / (60 / time_increment)),
                    )
                ],
            )
            self.predDict.update({camera: predFrame})
        return self.predDict

    def dms2dd(self, dmsr):
        """
        Converts a degree:minute:second GPS coordinate to a decimal coordinate

        :param dmsr: The input coordinate in degree, minute, second format
        :type dmsr: list[int]

        :returns: The equivalent GPS coordinate in decimal degrees
        :rtype: float
        """
        dd = float(dmsr[0]) + float(dmsr[1]) / 60 + float(dmsr[2]) / 3600
        if dmsr[3] == "S" or dmsr[3] == "W":
            dd = -dd
        return dd