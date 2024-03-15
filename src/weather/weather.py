from datetime import datetime
from datetime import timedelta
import openmeteo_requests
from pandas import DataFrame
from pandas import concat as pandasconcat
from joblib import dump as joblibdump
from joblib import load as joblibload
from utils import resource_path
from os.path import exists as ospathexists
from os import mkdir as osmkdir
import pandas


class Weather:
    weatherCodes = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Heavy Drizzle",
        56: "Light Freezing Drizzle",
        57: "Heavy Freezing Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Light Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Slight Snowfall",
        73: "Moderate Snowfall",
        75: "Heavy Snowfall",
        77: "Snow Grains",
        80: "Light Rain Shower",
        81: "Moderate Rain Shower",
        82: "Heavy Rain Shower",
        85: "Slight Snow Shower",
        86: "Heavy SNow Shower",
    }
    weatherAttributes = {
        "Temperature": "temperature_2m",
        "Real Feel": "apparent_temperature",
        "Dewpoint": "dew_point_2m",
        "Humidity": "relative_humidity_2m",
        "Precipitation": "precipitation",
        "Snowfall": "snowfall",
        "Wind Direction": "wind_direction_10m",
        "Wind Speed": "wind_speed_10m",
        "Peak Wind Gust": "wind_gusts_10m",
        "Pressure": "pressure_msl",
        "Cloud Cover": "cloud_cover",
        "Weather Code": "weather_code",
        "Daytime": "is_day",
        "Rain": "rain",
        "Showers": "showers",
        "Visibility": "visibility",
        "Soil Temperature": "soil_temperature_0cm",
        "Soil Moisture": "soil_moisture_0_to_1cm",
        "Precipitation Probability": "precipitation_probability",
        "Snowfall": "snowfall",
    }

    """
    Class to handle getting the future forecast of the weather
    
    :param coordinates: The GPS coordinates to get the weather at
    :type coordinates: tuple(lat, long)
    :param timestep: The timestep to get the data in (This is set by the openmeteo api)
    :type timestep: str
    :param units: The type of units to use (Metric or Imperial)
    :type units: str
    """

    def __init__(
        self, coordinates: tuple, timestep: str = "1hr", units: str = "Imperial"
    ):
        self.coordinates = coordinates
        self.timestep = timestep
        self.units = units

    def get_forecast(
        self, start_time: datetime, end_time: datetime, timezone: str, fields: list
    ):
        """
        Get the forecast for the times requested

        :param start_time: The time to start getting data at
        :type start_time: datetime.datetime
        :param end_time: The time to stop getting data at (Can only get 7 days without a license)
        :type end_time: datetime.datetime
        :param timezone: What timezone the system is getting data for
        :type timezone: str
        :fields: The list of weather fields to get
        :type fields: list[str]
        """
        self.forecastEnd = end_time.replace(minute=0, second=0, microsecond=0)
        if self.forecastEnd < datetime.now():
            self.forecastEnd += timedelta(
                hours=1
            )  # Round the end time up to the next whole hour if we are getting past data
        self.fieldsList = fields
        self.timeZone = timezone
        oldest_date_to_get = self.load_data(start_time)
        if oldest_date_to_get < self.forecastEnd:
            if oldest_date_to_get > datetime.strptime(self.hourlyData.index[0],"%Y-%m-%d %H:%M:%S"):
                lastGotWeatherData = self.get_weather_data(oldest_date_to_get, self.forecastEnd)
                self.hourlyData = pandasconcat([self.hourlyData, lastGotWeatherData])
            else:
                self.hourlyData = self.get_weather_data(oldest_date_to_get, datetime.strptime(self.hourlyData.index[-1],"%Y-%m-%d %H:%M:%S"))
            #pandas.set_option("display.max_rows", 500)
            #print(self.hourlyData)
            self.save_data()
        
              
    def get_weather_data(self, start_time, end_time):
        """
        Gets the weather data between the requested start and end times
        
        :param start_time: The time to start gathering data at
        :type start_time: datetime.datetime
        :param end_time: The time to stop gathering data at
        :type end_time: datetime.datetime
        
        :returns: The weather data for the given fields between the given start and end times
        :rtype: pandas.DataFrame
        """
        om = openmeteo_requests.Client()
        apiTimeSplit = [None, None]
        self.timeList = [
            time
            for time in range(
                int(start_time.timestamp()),
                int(end_time.timestamp()) + 1,
                3600,  # The last value is not included in the range
            )  # We only care about the latest whole that has passed. It is very unlikely that you would be uploading an image from
        ]
        # Create the value at which we will split the time list
        findValue = int(
            (
                datetime.now().replace(minute=0, second=0, microsecond=0)
                - timedelta(days=5)
            ).timestamp()
        )
        # Try splitting the list
        try:
            findIndex = self.timeList.index(findValue)
            apiTimeSplit[0] = [
                start_time,
                datetime.fromtimestamp(self.timeList[findIndex-1]),
            ]
            apiTimeSplit[1] = [
                datetime.fromtimestamp(self.timeList[findIndex+1]),
                end_time,
            ]
        except (
            ValueError
        ):  # If the split value is not found, then the date range is entirely in the past api or the forecast api
            if start_time > (
                datetime.now() - timedelta(days=5)
            ):  # Entirely future data
                apiTimeSplit[1] = [start_time, end_time]
            else:  # Entirely past data
                apiTimeSplit[0] = [start_time, end_time]

        apiHourlyData = []
        for index in range(2):
            if apiTimeSplit[index] is None:
                apiHourlyData.append(None)
                continue
            
            params = {
                "latitude": self.coordinates[0],
                "longitude": self.coordinates[1],
                "hourly": [self.weatherAttributes[field] for field in self.fieldsList],
                "start_hour": apiTimeSplit[index][0].strftime("%Y-%m-%dT%H:%M"),
                "end_hour": apiTimeSplit[index][1].strftime("%Y-%m-%dT%H:%M"),
                "timezone": self.timeZone,
            }
            # Change the units if needed
            if self.units == "Imperial":
                params.update(
                    {
                        "temperature_unit": "fahrenheit",
                        "wind_speed_unit": "mph",
                        "precipitation_unit": "inch",
                    }
                )

            if index == 0:
                responses = om.weather_api(
                    "https://archive-api.open-meteo.com/v1/archive", params=params
                )
            else:
                responses = om.weather_api(
                    "https://api.open-meteo.com/v1/forecast", params=params
                )
                
            apiHourlyData.append(responses[0].Hourly())
            # Append the data together (Should rework to add it to the right place right away instead of combining and removing later)
        
        hourlyData = [[] for item in range(len(self.fieldsList))]
        for apiIndex in range(2):  # Go through the split times
            if apiHourlyData[apiIndex] is None:
                continue
            for fieldIndex, fieldData in enumerate(
                [
                    apiHourlyData[apiIndex].Variables(index).ValuesAsNumpy().tolist()
                    for index in range(0, len(self.fieldsList))
                ]
            ):
                hourlyData[fieldIndex].extend(fieldData)

        hourlyData = DataFrame(
            hourlyData,
            columns=[str(datetime.fromtimestamp(time)) for time in self.timeList],
            index=self.fieldsList,
        )
        hourlyData = hourlyData.transpose()
        return hourlyData

    def get_data(self, date_time: datetime, attrib_list: list):
        """
        Goes to the meteostat website to pull data from it

        :param date_time: The date and time that you want the weather for
        :type date_time: datetime.datetime
        :param attrib_list: The list of attributes you want (i.e temperature, wind speed, rainfall, etc)
        :type attrib_list: list[str]

        :returns: All the data requested for the time requested
        :rtype: list[int or float or str]
        """
        data = []
        for item in attrib_list:
            data.append(self.__interpolate_data(date_time, item))
        return (
            data  # Return the filled in list with the same order that it came in with
        )

    def __interpolate_data(self, time: datetime, attrib_type: str):
        """
        Interpolates the input time between data points we have recieved from the meteostat api

        :param time: The time we want to interpolate at. We can get data for every hour, so anything in between needs to be interpolated
        :type time: datetime.datetime
        :param attrib_type: The type of attribute to get. Changes how many decimal points it gets rounded to
        :type attrib_type: str

        :returns: The interpolated value at the given time
        :rtype: float,int,str
        """
        if attrib_type == "Weather Code":
            return self.weatherCodes[
                self.hourlyData[attrib_type][
                    str(datetime(time.year, time.month, time.day, time.hour))
                ]
            ]
        numDecimal = (
            3 if attrib_type == "Precipitation" else 1
        )  # Determine how many decimal points to use
        prevTime = datetime(
            time.year, time.month, time.day, time.hour
        )  # Round down the current time
        nextTime = datetime(time.year, time.month, time.day, time.hour) + timedelta(
            hours=1
        )  # Add one hour to the previous hour for interpolation
        x1x = (nextTime - time).total_seconds()
        xx0 = (time - prevTime).total_seconds()
        y0 = self.hourlyData[attrib_type][str(prevTime)]
        y1 = self.hourlyData[attrib_type][str(nextTime)]
        return round(
            (y0 * x1x + y1 * xx0) / 3600, numDecimal
        )  # 3600 is the difference between x1 and x0 which is an hour

    def save_data(self):
        """
        Saves the returned weather data into a file for later retrieval without internet
        """
        if not ospathexists(resource_path("Weather Data", file_name=__file__)):
            osmkdir(resource_path("Weather Data", file_name=__file__))
        joblibdump(self.hourlyData, open(resource_path("Weather Data\\"+"WeatherData.pkl", file_name=__file__), "wb"))
    
    def load_data(self, oldest_requested_date):
        """
        Loads any previously saved weather data
        
        :param oldest date: The oldest date we are trying to get weather data for
        :type oldest_date: datetime.datetime
        
        :returns: The oldest date that we need to get data for
        :rtype: datetime.datetime
        """
        if ospathexists(resource_path("Weather Data\\"+"WeatherData.pkl", file_name=__file__)):
            self.hourlyData = joblibload(resource_path("Weather Data\\"+"WeatherData.pkl", file_name=__file__))
            earliestSavedDateTime = datetime.strptime(self.hourlyData.index[0],"%Y-%m-%d %H:%M:%S") #Grab first datetime stored in the file 
            latestSavedDatetime = datetime.strptime(self.hourlyData.index[-1],"%Y-%m-%d %H:%M:%S") #Grab the last datetime saved in the file
            if  earliestSavedDateTime <= oldest_requested_date:
                return latestSavedDatetime + timedelta(hours=1)
            else:
                return oldest_requested_date #If the requested oldest date is older than the oldest date we have stored in the datafile
        else:
            return oldest_requested_date