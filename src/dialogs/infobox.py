from ttkbootstrap import Toplevel, Label


class InfoBox:
    """
    Class to handle showing a pop-up dialog to the user. Meant for waiting dialogs

    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param title: The title to put in the titlebar of the pop-up (Defaults to "")
    :type title: str
    :param message: The message to show the user (Defaults to "")
    :type message: str
    """

    def __init__(self, main_window, title: str = "", message: str = ""):
        self.messageBox = Toplevel(main_window)
        self.messageBox.geometry("250x25")
        self.messageBox.title(title)
        infoLabel = Label(self.messageBox, text=message, anchor="center")
        infoLabel.pack(fill="both", expand=True)
        self.messageBox.withdraw()
        self.messageBox.update()  # Make sure you do this after packing everything in to make sure the heights and widths are correct
        position = (
            "+"
            + str(
                int(main_window.winfo_width() / 2)
                - int(self.messageBox.winfo_width() / 2)
                + main_window.winfo_x()
            )
            + "+"
            + str(
                int(main_window.winfo_height() / 2)
                - int(self.messageBox.winfo_height() / 2)
                + main_window.winfo_y()
            )
        )
        self.messageBox.geometry(position)
        self.messageBox.deiconify()
        self.messageBox.update()

    def close_info_box(self):
        """
        Closes the dialog box (You must call this or the info box will never go away)
        """
        self.messageBox.destroy()
