#References
#https://open-meteo.com/en/docs
#https://dev.meteostat.net/python/hourly.html#example

from datetime import datetime
from datetime import timedelta
import openmeteo_requests
from pandas import DataFrame

"""Class to handle getting the future forecast of the weather"""
class WeatherForecast():
    weatherAttributes = {"Temperature":"temperature_2m",
                         "Dewpoint":"dew_point_2m",
                         "Humidity":"relative_humidity_2m",
                         "Precipitation":"precipitation",
                         "Snowfall":"snowfall",
                         "Wind Direction":"wind_direction_10m",
                         "Wind Speed":"wind_speed_10m",
                         "Peak Wind Gust":"wind_gusts_10m",
                         "Pressure":"pressure_msl"}
    """
    Initialize the future forecast object
    
    :param coordinates: The GPS coordinates to get the weather at
    :type coordinates: tuple(lat, long)
    :param timestep: The timestep to get the data in (This is set by the openmeteo api)
    :type timestep: str
    :param units: The type of units to use (metric or imperial)
    :type units: str
    """
    def __init__(self, coordinates : tuple, timestep : str, units : str ="imperial"):
        self.coordinates = coordinates
        self.timestep = timestep
        self.units=units

    """
    Get the forecast for the times requested

    :param start_time: The time to start getting data at
    :type start_time: datetime.datetime
    :param end_time: The time to stop getting data at (Default is 5 days after the start time unless you get a license)
    :type end_time: datetime.datetime
    :fields: The list of weather fields to get
    :type fields: list[str]
    """
    def get_forecast(self, start_time: datetime, end_time: datetime, fields: list):
        self.forecastStart = start_time
        self.forecastEnd = end_time
        self.fieldsList = fields
        
        om = openmeteo_requests.Client()
        params = { "latitude": self.coordinates[0],
                   "longitude": self.coordinates[1],
                   "hourly": [self.weatherAttributes[field] for field in self.fieldsList],
                   "start_hour": self.forecastStart.strftime("%Y-%m-%dT%H:%M"),
                   "end_hour": self.forecastEnd.strftime("%Y-%m-%dT%H:%M"),
                   "temperature_unit": "fahrenheit",
                   "wind_speed_unit": "mph",
                   "precipitation_unit": "inch"}

        responses = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        response = responses[0]
        hourly = response.Hourly()
        self.hourlyData = [] 

        for list in [hourly.Variables(index).ValuesAsNumpy().tolist() for index in range(0, len(self.fieldsList))]:
            self.hourlyData.append(list)
        self.hourlyData = DataFrame(self.hourlyData, columns=[str(datetime.utcfromtimestamp(time)) for time in range(hourly.Time(), hourly.TimeEnd(), 3600)], index=self.fieldsList)
        self.hourlyData = self.hourlyData.transpose()

    """
    Goes to the meteostat website to pull data from it
    
    :param date_time: The date and time that you want the weather for
    :type date_time: datetime.datetime
    :param attrib_list: The list of attributes you want (i.e temperature, wind speed, rainfall, etc)
    :type attrib_list: list[str]
    
    :returns: All the data requested for the time requested
    :rtype: list[int or float or str]
    """
    def get_data(self, date_time: datetime, attrib_list: list):
        data = []
        for item in attrib_list:
            data.append(self.__interpolate_data(date_time, item))
        return data #Return the filled in list with the same order that it came in with
 
    """
    Interpolates the input time between data points we have recieved from the meteostat api
    
    :param time: The time we want to interpolate at. We can get data for every hour, so anything in between needs to be interpolated
    :type time: datetime.datetime
    :param attrib_type: The type of attribute to get. Changes how many decimal points it gets rounded to
    :type attrib_type: str
    
    :returns: The interpolated value at the given time
    :rtype: float,int,str
    """
    def __interpolate_data(self, time: datetime, attrib_type: str):
        numDecimal = 3 if attrib_type == "Precipitation" else 1 #Determine how many decimal points to use
        prevTime = datetime(time.year, time.month, time.day, time.hour) #Round down the current time
        nextTime = datetime(time.year, time.month, time.day, time.hour) + timedelta(hours=1) #Add one hour to the previous hour for interpolation
        timeDifference = (time - prevTime).total_seconds()
        x1x = (nextTime-time).total_seconds()
        xx0 = (time-prevTime).total_seconds()
        y0 = self.hourlyData[attrib_type][str(prevTime)]
        y1 = self.hourlyData[attrib_type][str(nextTime)]
        return round((y0*x1x+y1*xx0)/3600, numDecimal)