import tkinter as tk


class MainWindow():
    def __init__(self, game, width, height):
        self.root = tk.Tk()
        self.root.title("4000kmlike")
        # Get screen resolution
        self.screen_res = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())

        self.game = game
        self.dimensions = [width, height]
        # Main window appears at the center of the screen
        self.default_pos = [int(self.screen_res[0]/2 - self.dimensions[0]/2), int(self.screen_res[1]/2 - self.dimensions[1]/2)]
        self.root.geometry ="750x750+250+250" # f"{self.dimensions[0]}x{self.dimensions[1]}+{self.default_pos[0]}+{self.default_pos[1]}"
        self.root.resizable(False, False)

        # Internals
        self.managed_subwindows = {}    # TODO add subwindows here

        # Subwindows creation
        self.create_subwindows()

        # Misc
        # create a button to make the "time" window appear
        self.time_button = tk.Button(self.root, text="Time", command=lambda: self.open_subwindow("time"))
        self.time_button.pack(side=tk.TOP)


    def run(self):
        """Open the main window\n
        This should only be called after all subwindows have been created"""
        self.root.mainloop()

    def instanciate_subwindow(self, name, width, height, def_width, def_height):
        """Initialize a new subwindow in the main window's memory"""
        self.managed_subwindows[name] = SubWindow(self, name, width, height, def_width, def_height)
    
    def open_subwindow(self, name):
        """Open an existing subwindow"""
        self.managed_subwindows[name].instanciate()

    def create_subwindows(self):
        """Create all subwindows"""
        # Subwindow with the day & time
        self.instanciate_subwindow("time", 400, 150, 400, 200)
        wtime = self.managed_subwindows["time"]
        wtime.time_button = tk.Button(wtime.wd, text="Exit", command=wtime.wd.destroy)
        wtime.time_button.pack(side=tk.TOP)





class SubWindow():
    def __init__(self, mg, name, width, height, def_width, def_height):
        self.mg = mg
        self.name = name
        self.dimensions = [width, height]
        self.default_pos = [def_width, def_height]
        self.wd = tk.Toplevel()
        
        


    def instanciate(self):
        """Open the window"""
        # Tk initialization
        self.wd = tk.Toplevel()
        self.wd.geometry(f"{self.dimensions[0]}x{self.dimensions[1]}+{self.default_pos[0]}+{self.default_pos[1]}")
        self.wd.resizable(False, False)
        self.wd.mainloop()