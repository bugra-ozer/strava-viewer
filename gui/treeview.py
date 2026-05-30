# gui/treeview.py
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Treeview
from data.model import StravaData
from data.processing import get_display_data


class TreeviewController:
    """Manages the Treeview UI component and handles copy/sort events."""

    def __init__(self, parent, sort_callback):
        self.frame = tk.Frame(parent)
        self.tree = Treeview(self.frame, height=24)
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical')
        self.sort_callback = sort_callback

        self._init_layout()
        self._bind_events()

    def _init_layout(self):
        self.scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.tree.yview)

    def _bind_events(self):
        self.tree.bind("<Control-c>", self._copy_helper)

    def _copy_helper(self, event):
        action = self.tree.selection()
        if not action: return

        row_dict = self.tree.item(action[0])
        row_tuple = list(map(str, row_dict['values']))
        row_str = ', '.join(row_tuple)

        window = self.tree.winfo_toplevel()
        window.clipboard_clear()
        columns_str = ', '.join(self.tree.cget('columns'))
        window.clipboard_append(columns_str + '\n' + row_str)

    def update_data(self, strava_data: StravaData):
        """Fetch processed data and inject it into the Treeview."""
        if not strava_data: return

        display_data = get_display_data(strava_data)

        # Clear existing
        for t in self.tree.get_children():
            self.tree.delete(t)

        self.tree['columns'] = list(display_data.columns)
        self.tree.column('#0', width=0, stretch=False)

        # Setup columns and headings
        for col in display_data.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_callback(c))
            self.tree.column(col, width=180)

        # Insert rows
        for index, value in display_data.iterrows():
            self.tree.insert('', 'end', values=value.values.tolist())