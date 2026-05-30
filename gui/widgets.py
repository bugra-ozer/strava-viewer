# gui/widgets.py
import tkinter as tk
from tkinter import ttk

class TextRedirector:
    """Display cmd line on GUI via sys.stdout calling write functions."""
    def __init__(self, text_widget: tk.Text, delay=40):
        self.text_widget = text_widget
        self.delay = delay
        self.text = ""
        self.index = 0

    def write(self, text):
        if self.index == 0:
            self.text_widget.configure(state='normal')
            self.text_widget.delete("1.0", "end")
            self.text_widget.configure(state='disabled')
            self.text = text
            self.insert_next_char()

    def insert_next_char(self):
        if self.index < len(self.text):
            char = self.text[self.index]
            self.text_widget.configure(state='normal')
            self.text_widget.insert("end", char)
            self.text_widget.see("end")
            self.text_widget.configure(state='disabled')
            self.index += 1
            self.text_widget.after(self.delay, self.insert_next_char)
        else:
            self.index = 0

    def flush(self):
        pass

class EntryField:
    """Encapsulates Frame, Entry, and Label."""
    def __init__(self, parent: tk.Widget, text: str):
        self.frame = tk.Frame(parent)
        self.label = tk.Label(self.frame, text=text)
        self.entry = tk.Entry(self.frame)

    def pack_layout(self):
        self.entry.pack(side=tk.RIGHT)
        self.label.pack(side=tk.LEFT)
        self.frame.pack(side="top")