import pandas as pd
import sys
import ctypes
import pathlib as pl
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Treeview
from tkinter import ttk

app_id = 'Strava Viewer'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id) # noqa

class StravaData():
    """Read Strava CSV file and overwrite non-intuitive conventions to the metric system."""
    def __init__(self, path):
        self.assign_path(path)
        self.ms_to_km('average speed')
        self.ms_to_km('max speed')
        self.secs_to_hour('moving time')
        self.condition=None
        self.sort_column = None
        self.sort_ascending = True

    def assign_path(self, path: str):
        """Assign path to user selected directory."""
        path = pl.Path(path)
        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise IOError(f"Failed to read CSV: {e}") from e
        df.columns = [c.lower() for c in df.columns]
        df['activity date'] = pd.to_datetime(df['activity date'], format="%b %d, %Y, %I:%M:%S %p") #Activity date column to datetime format for accurate sorting
        self.data = df.copy()   # noqa keep copy
        return self

    def sort_values(self, column):
        """Sort columns when clicked."""
        if self.sort_column==column:
            self.sort_ascending=not self.sort_ascending
        else:
            self.sort_ascending=True
        self.sort_column=column

    def set_condition(self, condition):
        """Set condition property for filterization."""
        if condition is None:
            self.condition=None
        else:
            self.condition=condition

    def filter_results(self, column: str, operator: str, value: float, reset: bool):
        """Filter results based on column, operator, and value."""
        try:value=float(value)
        except ValueError:
            print('Value error, please enter valid characters.')
            return False

        if reset:
            condition=None
            pass

        elif operator == ">":
            condition=self.data[column]>value
        elif operator == "<":
            condition=self.data[column]<value
        elif operator == "<=":
            condition=self.data[column]<=value
        elif operator == ">=":
            condition=self.data[column]>=value
        elif operator == "==":
            condition=self.data[column]==value
        else:
            print('Invalid operation.')
            return False

        #Feedback to CLI/GUI
        if condition is None:print('Filter is removed, insert table for default view.')
        else:print('Filtering is complete!')
        self.set_condition(condition)
        return True

    def extract_column(self, column:str):
        """Return a specific column and mutate the self.data object."""
        column=column.lower()
        if column in self.data.columns:
            return self.data[f"{column}"]
        else:
            raise KeyError("Column not found.")

    def extract_multi_columns(self, column:list):
        """Extract multiple columns based on a list of column string names."""
        return self.data[column]

    def ms_to_km(self, column:str):
        """Convert speed from meters per second to kilometers per hour."""
        col = column.lower()
        if col not in self.data.columns:
            raise KeyError(col)
        self.data = self.data.assign(**{f"{col} kmh": (self.data[col].astype(float) * 3.6).round(2)}) # noqa

    def secs_to_hour(self, column):
        """Convert speed format to kmh."""
        if column in self.data.columns:
            meter=self.extract_column(column)
            meter=meter/3600
            meter=round(meter, 3)
            self.data[f"{column}/h"]=meter

class TextRedirector():
    """Display cmd line on GUI via sys.stdout calling write functions."""
    def __init__(self, text_widget:tk.Text, delay=40):
        self.text_widget = text_widget
        self.delay = delay
        self.text = ""
        self.index = 0

    def write(self,text):
        """Insert a character and make a next character call."""
        if self.index == 0:
            self.text_widget.configure(state='normal')
            self.text_widget.delete("1.0", "end")
            self.text_widget.configure(state='disabled')
            self.text = text
            self.insert_next_char()

    def insert_next_char(self):
        """Insert a character and recursively call itself until self.text is exhausted."""
        if self.index < len(self.text):
            char = self.text[self.index]
            self.text_widget.configure(state='normal')
            self.text_widget.insert("end", char)
            self.text_widget.see("end")
            self.text_widget.configure(state='disabled')
            self.index += 1
            self.text_widget.after(self.delay, self.insert_next_char) # noqa
        else:
            self.index = 0

    def flush(self):
        """Flush the stream."""
        pass

class EntryField():
    """Provide a systematic approach to the tk fields by encapsulating Frame, Entry and Label."""
    def __init__(self, parent:tk.Tk, text:str):
        self.frame=tk.Frame(parent)
        self.entry=tk.Entry(self.frame)
        self.text=text
        self.label=tk.Label(self.frame, text=self.text)

    def pack_button_helper(self):
        """Pack the called entry."""
        self.entry.pack(side=tk.RIGHT) # noqa
        self.label.pack(side=tk.LEFT) # noqa
        self.frame.pack(side="top")

class ButtonField():
    """Provide an object similar to EntryField, designed for the Text version with 2 tk objects."""
    def __init__(self, parent:tk.Tk, text:str):
        self.frame=tk.Frame(parent)
        self.entry=ttk.Button(self.frame, text=text)

    def pack_button_helper(self):
        """Pack the called button."""
        self.entry.pack()
        self.frame.pack(side="top")

def load_file(strava_data):
    """Open a .csv file and append items as valid columns."""
    items=['activity id', 'activity date', 'moving time/h', 'distance', 'max heart rate', 'average heart rate', 'average speed kmh', 'max speed kmh', 'average watts', 'calories']
    path=filedialog.askopenfilename()
    if path:
        strava_data=strava_data(path)
        strava_data.data=strava_data.data[items]
    else:
        raise ValueError('Failed to open user given path.')
    return strava_data

def calculate_summable_columns(display_data:pd.DataFrame):
    """Take a dataframe to assign columns to be used as a summary at the end of the treeview object."""
    select=['distance', 'calories', 'average watts']
    raw_value=None
    sum_dictionary={}
    columns=display_data.columns
    dt_columns=display_data.select_dtypes('number').columns
    for i in [column for column in dt_columns if column in select]: #Iterate over
        if i == 'average watts':
            available_watts=display_data[display_data[i].notna()]
            precise_watts=(available_watts[i] * available_watts['moving time/h'] / 1000).sum()
            approx_rides=display_data[display_data[i].isna()]
            approx_watts=(140 * approx_rides['moving time/h'] / 1000).sum()
            kwh=precise_watts+approx_watts
            raw_value=f"{round(kwh ,3)} kWh"
        elif i == 'calories':
            raw_value=f"{round(display_data[i].sum(skipna=True),3)} Kcal"
        elif i == 'distance':
            raw_value=f"{round(display_data[i].sum(skipna=True),3)} KMs"
        sum_dictionary[i]=raw_value
    for j in columns:
        if j not in sum_dictionary and j == 'activity id':
            sum_dictionary[j]='TOTAL:\t'
        elif j not in sum_dictionary:
            sum_dictionary[j]='**'
    return sum_dictionary

def apply_summable_columns(display_data:pd.DataFrame):
    """Apply the summable columns, add them to display data, and orchestrate the calculation call."""
    sum_dictionary=calculate_summable_columns(display_data)
    sum_df=pd.DataFrame([sum_dictionary])
    display_data=pd.concat([display_data,sum_df])
    return display_data

def get_display_data(strava_data:StravaData):
    """Copy current data and return filtered data if filtering has taken place."""
    if strava_data.condition is not None and strava_data.sort_column is not None: #Data filtered and sorted.
        display_data:pd.DataFrame=strava_data.data[strava_data.condition].sort_values(by=strava_data.sort_column, ascending= strava_data.sort_ascending)
    elif strava_data.condition is not None: #Filtered not sorted
        display_data:pd.DataFrame=strava_data.data[strava_data.condition]
    elif strava_data.sort_column is not None: #Sorted not filtered
        display_data:pd.DataFrame=strava_data.data.sort_values(by=strava_data.sort_column, ascending= strava_data.sort_ascending)
    else: #Unfiltered, raw data copy.
        display_data:pd.DataFrame=strava_data.data #iterate dataframe records and get Series
    display_data=apply_summable_columns(display_data)
    return display_data

def display_help():
    """Display text in the status bar to guide the user."""
    text="To filter results; add a valid column, operator (>,<,>=,<=,==), and a value.\nTo remove the filter, click X button."
    print(text)

def update_status_bar(status_bar:tk.Text):
    """Reroute sys print statements to the TextRedirector object."""
    sys.stdout=TextRedirector(status_bar)

def treeview_init(tree_view:Treeview, scroll_bar:ttk.Scrollbar, display_data, pandas_generator, strava_data:StravaData):
    """Initialize treeview. Remove children, format treeview size, and insert data values."""
    for t in tree_view.get_children(): tree_view.delete(t)
    treeview_adjust_table(display_data, tree_view, scroll_bar, strava_data)
    treeview_insert_values(tree_view, pandas_generator)
    init_scroll_bar_onto_treeview(tree_view, scroll_bar)
    treeview_copy_feature(tree_view)
    return strava_data

def treeview_adjust_table(display_data:pd.DataFrame, tree_view:Treeview, scroll_bar:ttk.Scrollbar, strava_data:StravaData):
    """Adjust treeview properties like column width and heading click functionality."""
    for i in list(display_data.columns):
        tree_view.heading(i, text=i, command=lambda col=i: (strava_data.sort_values(col), insertTable(tree_view, scroll_bar, strava_data)))
        tree_view.column(i, width=180) #column sorting

def treeview_insert_values(tree_view:Treeview, pandas_generator):
    """Insert values to treeview, utilized by the main treeview function."""
    for index, value in pandas_generator: #Iterating through panda rows
        raw_values=value.values #Series obj (bool T/F) to raw values
        tree_view.insert('','end',values=raw_values.tolist()) #''(start) to end insertion of columns not records

def treeview_copy_feature(tree_view:Treeview):
    """Add a copy feature via Ctrl+C to treeview rows."""
    tree_view.bind("<Control-c>", lambda event:treeview_copy_helper(event, tree_view))

def treeview_copy_helper(_event:tk.Event, tree_view:Treeview):
    """Help extract and process the selected row when a copy event is triggered."""
    action=tree_view.selection()
    if len(action)==0:pass
    else:
        row_dictionary=tree_view.item(action[0])
        row_tuple=row_dictionary['values']
        row_tuple=list(map(str, row_tuple)) #Map returns iterable map object, turn it into list
        row=', '.join(row_tuple)
        treeview_extract_copy_helper(row, tree_view)

def treeview_extract_copy_helper(row, tree_view:Treeview):
    """Append the extracted row and columns into the clipboard."""
    window=tree_view.winfo_toplevel()
    window.clipboard_clear()
    columns_tuple=tree_view.cget('columns')
    columns=', '.join(columns_tuple)
    line=columns+'\n'+row
    window.clipboard_append(line)

def insertTable(tree_view, scroll_bar, strava_data:StravaData):
    '''Insert table with filtered or unfiltered results packed, and initialize treeView.'''
    display_data:pd.DataFrame=get_display_data(strava_data)
    tree_view['columns']=list(display_data.columns) #update tree_view obj
    tree_view.column('#0', width=0, stretch=False)
    pandas_generator=display_data.iterrows() #iterate dataframe records and get Series
    treeview_init(tree_view, scroll_bar, display_data, pandas_generator, strava_data)

def init_scroll_bar_onto_treeview(tree_view:Treeview, scroll_bar:ttk.Scrollbar):
    """Adjust scroll bar and Treeview via configuration and packing."""
    tree_view.pack_forget() #   Unpack both widgets
    scroll_bar.pack_forget()
    scroll_bar.pack(side='right', fill='y') #   Repack in correct order (scrollbar FIRST, then treeview)
    tree_view.pack(side='left', fill='both', expand=True)
    tree_view.configure(yscrollcommand=scroll_bar.set) # Connect
    scroll_bar.configure(command=tree_view.yview)

def retrieve_entry(column_name:tk.Entry, operator:tk.Entry, value_entry:tk.Entry, strava_data:StravaData, reset=False):
    """Return the input of the text boxes to trigger filtering."""
    column_name=column_name.get()
    operator=operator.get()
    value=value_entry.get()
    strava_data.filter_results(column_name, operator, value, reset)

def pack_text_button_helper(window):
    """Pack the user status bar."""
    status_bar_frame=tk.Frame(window)
    status_bar=tk.Text(status_bar_frame, state='disabled', height=3, width=57)
    return status_bar, status_bar_frame

def icon_adder(window:tk.Tk):
    """Add icon to the tk object."""
    try:
        if getattr(sys, 'frozen', False):
            script_dir=pl.Path(sys._MEIPASS) # noqa
        else:
            script_dir=pl.Path(__file__).parent
        icon_path=script_dir / "imgs" / "helmet.ico"

        if icon_path.exists():
            window.iconbitmap(str(icon_path))
        else:
            print(f"Icon not found at: {icon_path}.")

    except Exception as e:
        print(f"Error setting exception {e}")
        pass

def init_entry_boxes(window, label_names:list):
    """Create entry buttons mapping to label_names and return a list of all entry buttons."""
    items=[]
    for i in label_names:
        entry_field=EntryField(window,i)
        items.append(entry_field)
    return items

def init_status_bar(window):
    """Adjust and pack the user status bar."""
    status_bar_tuple=pack_text_button_helper(window)
    update_status_bar(status_bar_tuple[0])
    display_help()
    return status_bar_tuple

def init_buttons_config(tree_scroll:list, input_boxes:list, window, cycling_container:list):
    """Return a dictionary style button configuration for the main window."""
    column_field, operator_field, value_field=input_boxes
    tree_view,scroll_bar=tree_scroll
    button_config=[
        {
            "parent": window,
            "type": "single",
            "text": "Load CSV File",
            "command": lambda: cycling_container.__setitem__(0, load_file(StravaData)) #CHECK Later
        },
        {
            "parent": window,
            "type": "single",
            "text": "Insert Table",
            "command": lambda:insertTable(tree_view, scroll_bar, cycling_container[0])
        },
        {
            "parent": window,
            "type": "group",
            "buttons":[
                {
                    "text": "Filter", "command": lambda:retrieve_entry(column_field.entry, operator_field.entry, value_field.entry, cycling_container[0], reset=False)},
                {
                    "text": "X", "command": lambda:retrieve_entry(column_field.entry, operator_field.entry, value_field.entry, cycling_container[0], reset=True)}]
        }
    ]
    return button_config

def init_buttons(button_config):
    """Pack buttons and their frames in applicable groups."""
    for config in button_config:
        if config["type"] == "single":
            button=ttk.Button(config["parent"],
                             text=config["text"],
                             command=config["command"])
            button.pack()
        elif config["type"] == "group":
            frame_filter=tk.Frame(config["parent"])
            for button_cfg in config["buttons"]:
                buttons_filter=ttk.Button(frame_filter,
                                         text=button_cfg["text"],
                                         command=button_cfg["command"]) #text box
                buttons_filter.pack(side='left')
            frame_filter.pack()

def configure_main_fields():
    """Initialize main fields like window and treeview, and apply themes."""
    background_color_main,text_color,button_backg_color='#262624',"#FFFFFF","#302F2E"
    window=tk.Tk(className=" Strava Viewer")
    icon_adder(window)
    tree_frame=tk.Frame(window)
    tree_view=Treeview(tree_frame, height=24)
    scroll_bar=ttk.Scrollbar(tree_frame,orient='vertical')
    window.configure(background=background_color_main)
    window.geometry('1200x800')
    style=ttk.Style(master=window)
    window.option_add('*Text.font', ('Segoe UI', 12))
    style.theme_use('clam')

    layers=['*Text', '*Label', '*Entry']
    for i in layers:
            window.option_add(f'{i}.foreground', text_color)
            window.option_add(f'{i}.background', button_backg_color)

#Applying styles via nested dicts. Clean, sweet, warm... :D
    background='#262624'
    foreground='#E9E9E9'
    fieldbackground="#262524"
    dictionary={
        'Treeview':
        {
            'foreground':foreground,
            'background':background,
            'fieldbackground':fieldbackground,
            'font':('Segoe UI', 12)
        },
        'Treeview.Heading':
        {
            'foreground':foreground,
            'background':background,
            'fieldbackground':fieldbackground
        },
    }
    for widget_names, properties in dictionary.items():
            style.configure(widget_names,**properties) #KWARGS is where magic happens, makes key value pairs form variable. e.g. background='#262624'

    dictionary={
        'TButton':
        {
            'foreground':foreground,
            'background':background,
            'width': 0
        },
        'Vertical.TScrollbar':
        {
            'foreground':foreground,
            'background':background,
            'troughcolor':background,
            'arrowcolor':foreground,
            'bordercolor':background,
        }
    }
    for widget_names, properties in dictionary.items():
            style.configure(widget_names,**properties) #KWARGS is where magic happens, makes key value pairs form variable. e.g. background='#262624'

    background=('pressed', '!disabled', "#D8642E"), ('active', '#D8642E')
    foreground=('pressed', '#E9E9E9'), ('active', '#E9E9E9')
    dictionary={
        'Treeview':
        {
            'foreground':foreground,
            'background':(('selected','#D8642E'),)+background # noqa
        },
        'Treeview.Heading':
        {
            'foreground':foreground,
            'background':background,
        },
        'TButton': {
    'background': (('pressed', '#D8642E'), ('active', '#D8642E'))
        },
        'Vertical.TScrollbar': {
    'background': (('pressed', '#D8642E'), ('active', '#D8642E'))
        }
    }
    for widget_name, properties in dictionary.items():
        style.map(widget_name,**properties)

    return window,tree_view,scroll_bar,tree_frame

def pack_initialize_all(window, tree_frame, tree_view, scroll_bar, cycling_container):
    input_boxes=init_entry_boxes(window, ["column:", "operator:", "value:"]) #input boxes
    button_config=init_buttons_config([tree_view, scroll_bar], input_boxes, window, cycling_container)
    status_bar, status_bar_frame=init_status_bar(window)
    tree_frame.pack()
    tree_view.pack()
    init_buttons(button_config) #packs clickables
    for i in input_boxes:i.packButtonHelper() #Pack all special EntryField objects (object that has frame, label and tk.entry as property).
    for i in status_bar_frame,status_bar: i.pack() #Packing status bar frame and the tk.text field

def program_initialize():
    cycling_container = [None]
    window,tree_view, scroll_bar,tree_frame=configure_main_fields()
    pack_initialize_all(window, tree_frame, tree_view, scroll_bar, cycling_container)
    window.mainloop()

if __name__ == "__main__":
    program_initialize()