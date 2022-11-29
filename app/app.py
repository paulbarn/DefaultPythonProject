import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
import re, sys, json

root = tk.Tk()
root.title('PDF Reader - v1.0')
#root.iconbitmap(Path(Path.cwd(), 'app.ico'))
root.geometry('1630x900+100+70')

# globals

# functions
def quit_btn():
    root.destroy()

#
# GUI Frames & Widgets
#


#
# Run application
#
root.mainloop()
