from datetime import datetime
from datetime import timedelta
from meteostat import Point, Hourly, units

class HistoricalWeather():
    """
    Assumes that the area is small enough that the variation in temperature is small across the property, we could divide it up by a grid onto the property

    """
    weatherAttributes = {"Temperature":"temp",
                         "Dewpoint":"dwpt",
                         "Humidity":"rhum",
                         "Precipitation":"prcp",
                         "Snowfall":"snow",
                         "Wind Direction":"wdir",
                         "Wind Speed":"wspd",
                         "Peak Wind Gust":"wpgt",
                         "Pressure":"pres"}
    """
    Class to hold all data and functions that get historical weather data
    
    :param start_date: The starting date to get data from
    :type start_date: datetime.datetime
    :param end_date: The date to stop getting getting at
    :type end_date: datetime.datetime
    :param location: The gps coordinates to get the weather at
    :type location: tuple(lat, long)
    """
    def __init__(self, start_date : datetime, end_date: datetime, location: tuple):
        self.startDate = start_date
        self.endDate = end_date
        self.location = Point(*location)
        self.hourlyData = Hourly(self.location, self.startDate, self.endDate)
        self.hourlyData = self.hourlyData.convert(units.imperial) #Convert everything to imperial units instead of metric
        self.hourlyData.interpolate() #Interpolate between missing data during the fetch
        self.hourlyData = self.hourlyData.fetch() #Fetch the data and store it

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
        return data #Return the filled in list with the same order that it came in with

    def __interpolate_data(self, time: datetime, attrib_type: str):
        """
        Interpolates the input time between data points we have recieved from the meteostat api
    
        :param time: The time we want to interpolate at. We can get data for every hour, so anything in between needs to be interpolated
        :type time: datetime.datetime
        :param attrib_type: The type of attribute to get. Changes how many decimal points it gets rounded to
        :type attrib_type: str
    
        :returns: The interpolated value at the given time
        :rtype: float or int or str
        """
        #if attrib_type == "weatherCode":
        #    return meteo_data[self.weatherAttributes[attrib_type]][str(time.replace(microsecond=0, second=0, minute=0))]
        numDecimal = 3 if attrib_type == "Precipitation" else 1 #Determine how many decimal points to use
        prevTime = datetime(time.year, time.month, time.day, time.hour) #Round down the current time
        nextTime = datetime(time.year, time.month, time.day, time.hour)+timedelta(hours=1) #Add one hour to the previous hour for interpolation
        #timeDifference = (time - prevTime).total_seconds()
        x1x = (nextTime-time).total_seconds()
        xx0 = (time-prevTime).total_seconds()
        y0 = self.hourlyData[self.weatherAttributes[attrib_type]][str(prevTime)]
        y1 = self.hourlyData[self.weatherAttributes[attrib_type]][str(nextTime)]
        return round((y0*x1x+y1*xx0)/3600, numDecimal) #3600 is the difference between x1 and x0 which is an hour

