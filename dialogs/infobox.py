from ttkbootstrap import Toplevel, Label

class InfoBox():
    def __init__(self, main_window, title: str = "", message: str = ""):
        self.messageBox = Toplevel(main_window)
        self.messageBox.geometry("250x25")
        self.messageBox.title(title)
        infoLabel = Label(self.messageBox, text=message, anchor="center")
        infoLabel.pack(fill="both", expand=True)
        self.messageBox.withdraw()
        self.messageBox.update() #Make sure you do this after packing everything in to make sure the heights and widths are correct
        position = "+" + str(int(main_window.winfo_width()/2)-int(self.messageBox.winfo_width()/2)+main_window.winfo_x())+"+"+str(int(main_window.winfo_height()/2)-int(self.messageBox.winfo_height()/2)+main_window.winfo_y())
        self.messageBox.geometry(position)
        self.messageBox.deiconify()
        self.messageBox.update()

    def close_info_box(self):
        self.messageBox.destroy()



