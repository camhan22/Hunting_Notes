from os.path import join as ospathjoin

class Marker():
    """
    Class to hold the data for each marker and operate on it
    
    :param map_widget: The tkintermapview widget the marker should be attached to
    :type map_widget: tkintermapview.map_widget
    :param lat: The latittude to put the marker at
    :type lat: float
    :param long: The longitude to put the marker at
    :type long: float
    :param name: The name of the marker
    :type name: str
    :param marker_type: The type of marker it should be (Camera, Stand, Point of Interest)
    :type marker_type: str
    :param data_directory: The directory where the data for the marker should go
    :type data_directory: str
    :param database: The name of the database we are using (The property name)
    :type database: str
    """
    def __init__(self, map_widget, lat, long, name, marker_type, data_directory, database):
        self.lat = lat
        self.long = long
        self.name = name
        self.type = marker_type
        self.mapper = map_widget
        #Set the correct color based on the type
        if(self.type == "Point of Interest"):
            self.outsideColor = "#C5542D"
            self.insideColor = "#9B261E"
        elif(self.type == "Stand"):
            self.outsideColor = "#3dfc03"
            self.insideColor  = "#259c02"
        elif(self.type == "Camera"):
            self.outsideColor = "#2803ff"
            self.insideColor  = "#1b02ad"
            
        self.highlightOutsideColor = "#f5d742"
        self.highlightInsideColor = "#eb9b34"
        self.justHighlighted = False
        self.isHighlighted = False
            
        self.notesPath = ospathjoin(data_directory,database,"notes", name)
        self.imagesPath = ospathjoin(data_directory, database,"pictures", name)
        self.marker = None
        self.make_marker()
     
    def make_marker(self, **kwargs):
        """
        Creates the marker on the map
    
        :param **kwargs: Any kwarsg to pass to the tkintermapview marker system
        :type: **kwargs: dict
        """
        if self.marker is not None:
            self.marker.delete()
            
        if "text_color" in kwargs and kwargs["text_color"] == "default":
            kwargs.pop("text_color")
        if not "marker_color_circle" in kwargs:
            kwargs.update({"marker_color_circle":self.insideColor})
        if not "marker_color_outside" in kwargs:
            kwargs.update({"marker_color_outside":self.outsideColor})
        self.marker = self.mapper.set_marker(self.lat, self.long, self.name, command=self.highlight, **kwargs)
 
    def highlight(self, highlighted_marker=None):
        """
        Highlights the marker that is clicked on
    
        :param highlighted_marker: The marker to be highlighted
        :type highlighted_marker: markers.Marker
        """
        if highlighted_marker is not None:
            self.make_marker(marker_color_outside=self.highlightOutsideColor,
                             marker_color_circle=self.highlightInsideColor)
            self.justHighlighted = True
       
    def unhighlight(self, force=False):
        """
        Returns a marker to its regular color
    
        :param force: Whether to force the marker to unhighlight or not. Left click events call this but also when a marker is highlighted since a left click happens
        :type force: Bool
        """
        if self.justHighlighted:
            self.justHighlighted = False
            self.isHighlighted = True
            return
        if self.isHighlighted or force:
            if force:
                self.justHighlighted = False
            self.make_marker()
            self.isHighlighted = False

    def change_color(self, **kwargs):
        """
        Changes the color of the marker to whatever the user wants
        :param **kwargs: Any keyword arguments to pass to the tkintermapview marker
        :type **kwargs: dict
        """
        self.make_marker(**kwargs)
         
    def destroy(self):
        """
        Deletes the tkintermapview marker from the map
        """
        self.marker.delete()


