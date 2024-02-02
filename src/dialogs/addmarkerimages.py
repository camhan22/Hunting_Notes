from tkinter.filedialog import askopenfilenames
from shutil import copy as shutilcopy
from exif import Image as exifimage
from os.path import join as ospathjoin
from tkinter import messagebox

class AddMarkerImagesDialog():
    """
    Class to handle adding images to a marker
    
    :param marker: The marker we want to add images to
    :type marker: markers.Marker
    """
    def __init__(self, marker):
        self.files = askopenfilenames()
        if not self.files: #If the list is empty, happens when the user presses the cancel button
            self.top.destroy()
            return
        try:
            convertedLat = self.dd2dms(marker.lat)
            convertedLong = self.dd2dms(marker.long, False)
            for file in self.files:
                shutilcopy(file, marker.imagesPath)
                #Update exif data
                image = exifimage(ospathjoin(marker.imagesPath, file))
                image.datetime_original = image.datetime
                image.gps_latitude = convertedLat[0:3]
                image.gps_latitude_ref = convertedLat[3]
                image.gps_longitude = convertedLong[0:3]
                image.gps_longitude_ref = convertedLong[3]
                with open(ospathjoin(marker.imagesPath, file), "wb") as outfile:
                    outfile.write(image.get_file())     
        except Exception as e:
            print(e)
            messagebox.showerror("Failed", "Failed to copy over pictures")
            self.top.destroy()
            return
        messagebox.showinfo("Success", "Successfully copied over the images")
        self.top.destroy()

    def dd2dms(self, dd, is_lat=True):
        """
        :param dd: The decimal degree to be converted
        :type dd: float
        :param is_lat: Flag to tell if this is a latitude or a longitude (True is for latitude, False for longitude)
        :type is_lat: bool
    
        :returns: The degree, minute, second representation of the input
        :rtype: list[float]
        """
        negative = dd < 0
        dd = abs(dd)
        minutes,seconds = divmod(dd*3600,60)
        degrees,minutes = divmod(minutes,60)
        if is_lat and negative:
            return (degrees,minutes,seconds, "S")
        elif is_lat and not negative:
            return (degrees,minutes,seconds, "N")
        elif not is_lat and negative:
            return (degrees,minutes,seconds, "W")
        elif not is_lat and not negative:
            return (degrees,minutes,seconds, "E")



