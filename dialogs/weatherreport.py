from dialogs.templatedialog import DialogTemplate

"""Class to handle showing the weather report for the selected times to the user"""
class WeatherReportDialog(DialogTemplate):
    """
    Initialize the weather report dialog
    
    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    """
    def __init__(self, main_window):
        super().__init__(main_window, False, True)




