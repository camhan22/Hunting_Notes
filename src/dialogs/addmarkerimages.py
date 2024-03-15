from tkinter.filedialog import askopenfilenames
from shutil import copy2 as shutilcopy2
from exif import Image as exifimage
from os.path import join as ospathjoin
from os import rename as osrename
from tkinter import messagebox
from PIL import Image
from animal_detector.animal_detector import HuntingAnimalDetector
from dialogs.infobox import InfoBox


class AddMarkerImagesDialog:
    """
    Class to handle adding images to a marker

    :param root: The root window that the app is based on
    :type root: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param marker: The marker we want to add images to
    :type marker: markers.Marker
    """

    def __init__(self, root, marker):
        self.root = root
        self.files = list(
            askopenfilenames(
                filetypes=(("JPEG", ".jpg"), ("PNG", ".png"), ("GIF", ".gif"))
            )
        )  # Returns full path to files
        if (
            not self.files
        ):  # If the list is empty, happens when the user presses the cancel button
            return
        self.remove_blank_images(self.files)
        try:
            convertedLat = self.dd2dms(marker.lat)
            convertedLong = self.dd2dms(marker.long, False)
            for file in self.files:
                shutilcopy2(file, marker.imagesPath)
                imagePath = ospathjoin(marker.imagesPath, file.split("/")[-1])
                self.resize_image(imagePath)
                # Update exif data
                image = exifimage(imagePath)
                image.datetime_original = image.datetime
                image.gps_latitude = convertedLat[0:3]
                image.gps_latitude_ref = convertedLat[3]
                image.gps_longitude = convertedLong[0:3]
                image.gps_longitude_ref = convertedLong[3]
                with open(imagePath, "wb") as outfile:
                    outfile.write(image.get_file())
                extension = imagePath.split(".")[-1]
                osrename(
                    imagePath,
                    str(image.datetime.replace(" ", "_").replace(":", "_"))
                    + "."
                    + extension,
                )

        except Exception as e:
            print(e)
            messagebox.showerror("Failed", "Failed to copy over pictures")
            return
        messagebox.showinfo("Success", "Successfully copied over the images")

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
        minutes, seconds = divmod(dd * 3600, 60)
        degrees, minutes = divmod(minutes, 60)
        if is_lat and negative:
            return (degrees, minutes, seconds, "S")
        elif is_lat and not negative:
            return (degrees, minutes, seconds, "N")
        elif not is_lat and negative:
            return (degrees, minutes, seconds, "W")
        elif not is_lat and not negative:
            return (degrees, minutes, seconds, "E")

    def resize_image(self, file_path):
        """
        Resizes the image down to 640x640 pixels to match the animal detector better since that is what it is expecting

        :param file_path: The path to the file to resize
        :type file_path: str
        """
        image = Image.open(file_path)
        image = image.resize((640, 640), resample=1)
        exif = image.info["exif"]
        image.save(file_path, "JPEG", exif=exif)

    def remove_blank_images(self, file_list):
        """
        Remove images that don't contain any animals
        """
        detector = HuntingAnimalDetector(self.root, wait_while_training=True)
        infoBox = InfoBox(
            self.root,
            "Training Started",
            "Please wait until training has finished and images have been uploaded",
        )
        while detector.isLoading:
            pass
        infoBox.close_info_box()

        # Look through all the images and find any animals, if we don't we don't keep that image
        for index, file in enumerate(file_list):
            if detector.detect_animals(file, 0.4) is []:
                file_list.pop(
                    index
                )  # If there is nothing detected, remove it from the list to import in since it doesn't contain any information we want
