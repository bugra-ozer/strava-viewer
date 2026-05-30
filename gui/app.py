# gui/app.py
import sys
import pathlib as pl
import tkinter as tk
from tkinter import ttk

import config
from gui.theme import apply_theme
from gui.widgets import TextRedirector, EntryField
from gui.treeview import TreeviewController
from data.loader import load_csv_data
from data.processing import apply_filter


class StravaApp:
    """Main Application orchestrator."""

    def __init__(self):
        self.strava_data = None
        self.window = tk.Tk(className=f" {config.APP_NAME}")
        self.window.geometry(config.WINDOW_GEOMETRY)

        self._set_icon()
        apply_theme(self.window)
        self._build_ui()
        self._setup_status_bar()

    def _set_icon(self):
        try:
            if getattr(sys, 'frozen', False):
                script_dir = pl.Path(sys._MEIPASS)
            else:
                script_dir = pl.Path(__file__).parent.parent
            icon_path = script_dir / "imgs" / "helmet.ico"

            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception:
            pass

    def _build_ui(self):
        # Data View
        self.tree_controller = TreeviewController(self.window, self._on_sort)
        self.tree_controller.frame.pack()

        # Inputs
        self.col_field = EntryField(self.window, "column:")
        self.op_field = EntryField(self.window, "operator:")
        self.val_field = EntryField(self.window, "value:")

        # Action Buttons
        ttk.Button(self.window, text="Load CSV File", command=self._on_load).pack()
        ttk.Button(self.window, text="Insert Table", command=self._refresh_table).pack()

        # Filter Group
        filter_frame = tk.Frame(self.window)
        ttk.Button(filter_frame, text="Filter", command=lambda: self._on_filter(False)).pack(side='left')
        ttk.Button(filter_frame, text="X", command=lambda: self._on_filter(True)).pack(side='left')
        filter_frame.pack()

        # Pack Entry Fields
        for field in [self.col_field, self.op_field, self.val_field]:
            field.pack_layout()

        # Status Bar
        self.status_frame = tk.Frame(self.window)
        self.status_bar = tk.Text(self.status_frame, state='disabled', height=3, width=57)
        self.status_frame.pack()
        self.status_bar.pack()

    def _setup_status_bar(self):
        sys.stdout = TextRedirector(self.status_bar)
        print("To filter results; add a valid column, operator (>,<,>=,<=,==), and a value.\n"
              "To remove the filter, click X button.")

    def _on_load(self):
        loaded_data = load_csv_data()
        if loaded_data:
            self.strava_data = loaded_data
            self._refresh_table()

    def _on_sort(self, column: str):
        if self.strava_data:
            self.strava_data.set_sort(column)
            self._refresh_table()

    def _on_filter(self, reset: bool):
        if not self.strava_data: return

        col = self.col_field.entry.get()
        op = self.op_field.entry.get()
        val = self.val_field.entry.get()

        success = apply_filter(self.strava_data, col, op, val, reset)
        if success:
            self._refresh_table()

    def _refresh_table(self):
        if self.strava_data:
            self.tree_controller.update_data(self.strava_data)

    def run(self):
        self.window.mainloop()