# gui/theme.py
import tkinter as tk
from tkinter import ttk
import config


def apply_theme(window: tk.Tk):
    """Apply styling maps to Tkinter global configuration."""
    window.configure(background=config.BG_COLOR_MAIN)
    window.option_add('*Text.font', config.FONT_MAIN)

    style = ttk.Style(master=window)
    style.theme_use('clam')

    layers = ['*Text', '*Label', '*Entry']
    for layer in layers:
        window.option_add(f'{layer}.foreground', config.TEXT_COLOR)
        window.option_add(f'{layer}.background', config.BUTTON_BG_COLOR)

    style.configure('Treeview',
                    foreground=config.FG_COLOR,
                    background=config.BG_COLOR_MAIN,
                    fieldbackground=config.BG_COLOR_MAIN,
                    font=config.FONT_MAIN)

    style.configure('Treeview.Heading',
                    foreground=config.FG_COLOR,
                    background=config.BG_COLOR_MAIN,
                    fieldbackground=config.BG_COLOR_MAIN)

    style.configure('TButton', foreground=config.FG_COLOR, background=config.BG_COLOR_MAIN, width=0)

    style.configure('Vertical.TScrollbar',
                    foreground=config.FG_COLOR,
                    background=config.BG_COLOR_MAIN,
                    troughcolor=config.BG_COLOR_MAIN,
                    arrowcolor=config.FG_COLOR,
                    bordercolor=config.BG_COLOR_MAIN)

    active_bg = (('pressed', config.ACCENT_COLOR), ('active', config.ACCENT_COLOR))
    style.map('Treeview',
              background=(('selected', config.ACCENT_COLOR),),
              foreground=(('pressed', config.FG_COLOR), ('active', config.FG_COLOR)))
    style.map('Treeview.Heading',
              background=(('pressed', '!disabled', config.ACCENT_COLOR), ('active', config.ACCENT_COLOR)),
              foreground=(('pressed', config.FG_COLOR), ('active', config.FG_COLOR)))
    style.map('TButton', background=active_bg)
    style.map('Vertical.TScrollbar', background=active_bg)