from dialogs.templatedialog import DialogTemplate
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap import Text, Combobox, Menu
from os.path import join as ospathjoin
from os.path import exists as ospathexists
from os import listdir as oslistdir
from os import mkdir as osmkdir
from tkinter import messagebox
from shutil import move as shutilmove


class NoteViewer(DialogTemplate):
    """
    Class to view notes from a marker

    :param main_window: The window to show this dialog in front of
    :type main_window: :type root_window: ttkbootstrap.Window, ttkbootstrap.Frame, tkinter.Tk, tkinter.Frame
    :param notes_folder_path: The path to the notes folder to look at
    :type notes_folder_path: str
    """

    def __init__(self, main_window, notes_folder_path):
        super().__init__(main_window, False, True)
        self.top.title("Notes Viewer")
        self.notesFolderPath = notes_folder_path
        self.textFrame = ScrolledFrame(self.top)
        self.textBoxes = []
        self.top.minsize(525, 325)
        self.rightClickMenu = Menu(self.textFrame, tearoff=False)
        self.rightClickMenu.add_command(label="Delete Note", command=self.delete_note)
        self.expandedNote = [None, None]
        # Widgets
        self.locationComboBox = Combobox(self.top, justify="center", state="readonly")
        self.locationComboBox.bind("<<ComboboxSelected>>", self.load_notes)
        # Frame packing
        self.loadLocationOptions()
        self.load_notes()
        self.pack_frames(
            {self.locationComboBox: [1, 0.1, 0, 0], self.textFrame: [1, 0.9, 0, 0.1]}
        )
        self.show(True)

    def loadLocationOptions(self):
        """
        Loads all the notes that could be displayed
        """
        locations = oslistdir(self.notesFolderPath)
        locations = [
            f.title() for f in locations
        ]  # Titleize the string (Every character after a space is capital)
        locations = [f for f in locations if not f == "Abandoned"]
        if not locations == []:
            self.locationComboBox.configure(
                values=locations
            )  # Convert the files list to a tuple and store it in the combo box
            self.locationComboBox.current(0)

    def load_notes(self, event=None):
        """
        Load each of the notes text into an entry and display it
        """
        for note in self.textBoxes:
            note.pack_forget()
            self.textBoxes.remove(note)
        self.notes = oslistdir(
            ospathjoin(self.notesFolderPath, self.locationComboBox.get())
        )
        if self.notes == []:
            return
        for index, noteFile in enumerate(self.notes):
            lineCount = 0
            self.textBoxes.append(Text(self.textFrame, wrap="word"))
            self.textBoxes[index].pack()
            self.textBoxes[index].bind("<Button-3>", self.show_right_click_menu)
            # self.textBoxes[index].bind("<<Delete-Note>>", self.delete_note)
            self.textBoxes[index].bind("<Double-Button-1>", self.expand_note)
            with open(
                ospathjoin(self.notesFolderPath, self.locationComboBox.get(), noteFile),
                "r",
            ) as file:
                for line in file.readlines():
                    lineCount += 1
                    self.textBoxes[index].insert("insert", line)
                if lineCount > 5:
                    self.textBoxes[index].configure(height=5, state="disabled")
                else:
                    self.textBoxes[index].configure(height=lineCount, state="disabled")

    def expand_note(self, event=None):
        """
        Expands a note and shows the entire text. Occurs on a double click of the note
        """
        if (
            event.widget == self.expandedNote[1]
        ):  # Reduce the size of already expanded note
            self.expandedNote[0] = self.expandedNote[1]
            self.expandedNote[1] = None
            lineCount = int(event.widget.index("end-1c").split(".")[0]) - 1
            if lineCount > 5:
                height = 5
            else:
                height = lineCount
            event.widget.configure(height=height)
        else:
            self.expandedNote[0] = self.expandedNote[1]
            self.expandedNote[1] = event.widget
            if self.expandedNote[0] is not None:
                lineCount = int(event.widget.index("end-1c").split(".")[0]) - 1
                if lineCount > 5:
                    height = 5
                else:
                    height = lineCount
                self.expandedNote[0].configure(height=height)
            # Expand the new text box
            lineCount = int(event.widget.index("end-1c").split(".")[0]) - 1
            event.widget.configure(height=lineCount)

    def delete_note(self):
        """
        Deletes the currently selected note
        """
        if self.currentNote is not None:
            self.currentNote.delete("1.0", "end")
            self.currentNote.destroy()
        else:
            return
        answer = messagebox.askyesno(
            "Delete Note", "Are you sure you want to delete this note?"
        )
        if answer:
            if not ospathexists(ospathjoin(self.notesFolderPath, "Abandoned")):
                osmkdir(ospathjoin(self.notesFolderPath, "Abandoned"))
            shutilmove(
                ospathjoin(
                    self.notesFolderPath,
                    self.locationComboBox.get(),
                    self.notes[self.textBoxes.index(self.currentNote)],
                ),
                ospathjoin(self.notesFolderPath, "Abandoned"),
            )
            self.currentNote = None

    def show_right_click_menu(self, event=None):
        """
        Shows the right click menu when the user hovers over a note and right clicks the mouse
        """
        try:
            self.currentNote = event.widget
            self.rightClickMenu.tk_popup(event.x_root, event.y_root)

        finally:
            self.rightClickMenu.grab_release()
