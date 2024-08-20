import os
import glob
from tkinter import filedialog
import tkinter as tk
from PIL import ImageTk, Image


class ImageViewer(object):
    def __init__(self):

        self.root = tk.Tk()
        self.root.state('zoomed')
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.images = None

        img, wh, ht = self.open_file()
        self.canvas = tk.Canvas(self.root, width=wh, height=ht, bg='black')
        self.canvas.pack(expand=tk.YES)
        self.image_on_canvas = self.canvas.create_image(self.width/2, self.height/2, anchor=tk.CENTER, image=img)

        b = tk.Button(self.root, text='next', command=self.next_image)
        b.place(x=50, y=50)

        self.root.mainloop()

    def open_file(self):
        openfile = filedialog.askopenfilename(initialdir='/', title='Select image', filetypes=(('jpeg files', '*.jpg'), ('all files', '*.*')))
        self.images = glob.glob(os.path.dirname(openfile) + '/*.jpg')
        self.root.title(openfile)

        img = Image.open(openfile)
        img.thumbnail((self.width, self.height), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)

        return img, self.width, self.height

    def next_image(self):

        if not self.images:
            img, wh, ht = self.open_file()
        else:
            image = self.images.pop(0)
            self.root.title(image)
            img = Image.open(image)
            img.thumbnail((self.width, self.height), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)

        self.canvas.itemconfigure(self.image_on_canvas, image=img)
        self.canvas.config(width=self.width, height=self.height)
        try:
            self.canvas.wait_visibility()
        except tk.TclError:
            pass


ImageViewer()