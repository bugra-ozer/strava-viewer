# Strava Viewer

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

Strava Viewer is a desktop application designed to load, view, and analyze your Strava activity exports. Built with a clean Tkinter GUI and powered by Pandas under the hood, it allows you to filter through your ride data, sort metrics, and view total aggregate stats at a glance.

## Features

* **Metric Conversions:** Automatically converts non-intuitive CSV values (like meters per second) to kilometers per hour and seconds to hours.
* **Interactive Data Table:** Click on any column header to sort your data ascending or descending.
* **Advanced Filtering:** Use operators (`>`, `<`, `>=`, `<=`, `==`) to filter specific metrics, like finding all rides over a certain distance or average speed.
* **Summary Aggregates:** Automatically calculates and appends a summary row for total distance, total calories, and estimated Kilowatt-hours (kWh) at the bottom of your data view.
* **Quick Copy:** Select any row and use `Ctrl+C` to copy the data directly to your clipboard.

## Project Structure

The project utilizes a modular architecture, separating the graphical user interface from the underlying data processing logic.

* `main.py`: The entry point that initializes the application.
* `config.py`: Centralized configuration for themes, colors, and layout geometry.
* `data/`: Handles all data processing.
  * `loader.py`: Manages the file dialog and initial CSV parsing.
  * `model.py`: Holds the `StravaData` class, managing the DataFrame and sorting states.
  * `processing.py`: Handles filtering logic and summation calculations.
  * `transforms.py`: Executes metric conversions (e.g., m/s to km/h).
* `gui/`: Manages the Tkinter interface.
  * `app.py`: The main orchestrator that glues the UI components together.
  * `theme.py`: Configures the global visual styling and widget mapping.
  * `treeview.py`: Manages the interactive data table.
  * `widgets.py`: Encapsulates individual custom UI components (like entry fields and the status bar).

## Installation

Ensure you have Python 3.8 or higher installed on your system. 

1. Clone this repository to your local machine:
   ```bash
   git clone [https://github.com/yourusername/strava-viewer.git](https://github.com/yourusername/strava-viewer.git)
   cd strava-viewer
   
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
   
3. Install the required dependencies:
   ```bash
    pip install -r requirements.txt

4. Run the app
   ```bash
   python main.py
   
    Click Load CSV File and select your exported Strava data file.

    Click Insert Table to view your records.
    
    Use the input fields at the top (column:, operator:, value:) and click Filter to refine your view.
    
    Click the X button next to the filter controls to clear your search and restore the default table.

![Strava app screenshot](imgs/app_ss.png)
