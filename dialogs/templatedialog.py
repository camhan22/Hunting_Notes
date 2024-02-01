from ttkbootstrap import Toplevel, Button, Frame, Style

"""Class that other dialogs inherit to handle basic functions common to most dialogs"""
class DialogTemplate():
    """
    Initialize the template
    
    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param is_modal: Determines if the user is able to close the dialog without pushing one of the given buttons (Defaults to True)
    :type is_modal: bool
    :param no_okay_cancel: Whether or not to automatically include the okay/cancel buttons at the bottom (Defaults to True)
    :type no_okay_cancel: bool
    """
    def __init__(self, main_window, is_modal:bool=True, no_okay_cancel:bool=False):
        self.mainWindow = main_window
        self.top = Toplevel(main_window)
        self.top.resizable(True, True)
        self.top.withdraw()
        self._result = None
        self.relativeButtonHeight = 0.2
        self.buttonFrame = Frame(self.top)
        self.widgetFrame = Frame(self.top)
        
        Style().configure("okcancel.TButton",bordercolor="black")
        if not no_okay_cancel:
            self.okButton = Button(self.buttonFrame, text="Ok", command=self.on_okay, style="okcancel.TButton")
            self.cancelButton = Button(self.buttonFrame, text="Cancel", command=self.on_cancel, style="okcancel.TButton")
            self.cancelButton.place(relwidth=0.5, relheight=1.0)
            self.okButton.place(relwidth=0.5, relx=0.5, relheight=1.0)
        self.bind_button_keys()
        self.top.overrideredirect(is_modal)
        if is_modal:
            self.top.protocol("WM_CLOSE_WINDOW", self.on_cancel)
 
    """
    Called when the user hits the cancel button
    """
    def on_cancel(self, event=None):
        self.close_dialog()

    """
    Called when the user hits the okay button
    """
    def on_okay(self, event=None):
        self.close_dialog()

    """
    Binds "esc" to cancel and "enter" to okay
    """
    def bind_button_keys(self):
        self.top.bind("<Return>", self.on_okay)
        self.top.bind("<Escape>", self.on_cancel)
        
    """
    Unbinds the esc and enter buttons
    """
    def unbind_button_keys(self):
        self.top.unbind("<Return>")
        self.top.unbind("<Escape>")
        
    """
    Packs all the widgets frame to the toplevel window. ex, the buttond and widget frames
    """
    def pack_frames(self, widget_list: dict = {}):
        for item in widget_list:
            item.place(relwidth=widget_list[item][0], relheight=widget_list[item][1], relx=widget_list[item][2], rely=widget_list[item][3])
    
    """
    Shows the dialog to the user and waits for the window to close if the window should wait for an answer from the user
    """
    def show(self, no_wait=False):
        self.top.update_idletasks()
        self.position = "+" + str(int(self.mainWindow.winfo_screenwidth()/2)-int(self.top.winfo_width()/2))+"+"+str(int(self.mainWindow.winfo_screenheight()/2)-int(self.top.winfo_height()/2))
        self.top.geometry(self.position)
        self.top.update_idletasks()
        self.top.deiconify()
        #self.top.transient(self.mainWindow)
        self.top.grab_set()
        #Check if the window can close automatically or if it needs user input
        if not no_wait:
            self.top.wait_window()          

    """
    Closes the dialog window, also unbinds the esc and enter keys
    """
    def close_dialog(self):
        self.unbind_button_keys()
        self.top.destroy()
        self.mainWindow.focus_set()

    """
    Property to store any return information
    """
    @property
    def result(self):
        return self._result
    
    """
    Setter for the result property
    """
    @result.setter
    def result(self, value):
        self._result = value
          




        
        
        
        


