# Carbon Intensity Data Collection

This project is the Week 3 assignment of the Application course. This application pulls weather temperature data from the National Weather Service's public API, stores the data, and provides a web front end where a user can query weather records. 

![Build status](https://github.com/EnergizeStatistics/capstone-csca5028/actions/workflows/python-app.yml/badge.svg)

## Table of Contents

- [Setting up](#setting-up)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [File explanations](#file-explanations)
- [Usage](#usage)
  - [Data collection and storage](#data-collection-and-storage)
  - [Data analysis](#data-analysis)
- [Data source](#data-source)
- [Side note](#side-note)

## Setting up 

### Prerequisites
- Python 3.10.12
- `python3-venv` 3.10.6-1~22.04
- `python3-pip` 22.0.2

### Installation

#### Virtual environment
To create the virtual environment, at the project root folder,
```bash
# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Dependencies
Still, at the project root folder,
```bash
pip install -r requirements.txt
```
## File explanations

### `src/fetch_store_data.py`

- **Description:** This file contains the core logic for fetching weather data and storing such data into a local database.

### `src/schedule_fetching.py`

- **Description:** The data source publishes new weather data periodically. Accordingly, this file makes data retrieval and storage a recurring task. 

### `src/define_application.py`

- **Description:** This file sets up the web application.

### `src/query_analyze_data.py`

- **Description:** This file contains the core logic that analyzes the data per user request, and then publishes the results to the front end. 

### `src/utils.py`

- **Description:** The file houses helper functions used throughout the project.

### `config.json`

- **Description:** This file stores project configuration settings, such as the city for which we are pulling weather data, and the API endpoints of the data source.

### `database/`

- **Description:** This directory holds the database used by the project. The weather data is stored into a file called "Weather.sqlite3" in this folder. 

### `templates/`

- **Description:** This directory stores the html templates required by the front end. 

### `requirements.txt`

- **Description:** The `requirements.txt` file lists all the project dependencies required to run the code.

### `.project_root_marker`

- **Description:** This file is used by one of the helper functions to locate the project root. 

## Usage
### Data collection and storage
We need to first accumulate some data before an analysis can be done to the data. 

Activate the virtual environment. Then, at the project root folder,
```bash
export FLASK_APP=src/schedule_fetching.py
flask run
```
The data source publishes new temperature data every once in a while - their interval seems to vary even within the same weather observation station. I also expect their update interval to vary by weather stations. On our end, I have set the data pulling interval to be 20 minutes. If we desire to accumulate a reasonable amount of data, we need to let this process run for a while. 

For a quick test, when the commands above are invoked, the data retrieval and storage job is immediately executed once. You will see one new record in the Weather.sqlite3 database. 

I share this codebase with existing data in the Weather database, so you will see new records appended to the end of the database when running this task. If you delete the existing Weather.sqlite3 file before you run this task, the database will be created at this point, and you will see one record in it. 

### Data analysis
Also with the virtual environment activated,
```bash
export FLASK_APP=src/query_analyze_data.py
flask run
```
After the commands above are launched, you can open http://127.0.0.1:5000 in your browser. On the index page, you can set your condition to filter for weather records. For example, you can select "Greater than (>)" in the dropdown menu and then enter an integer "5" (without the quotes) in the next box. After clicking the "Query" button, the next page will display the date and time in the database at which the temperature meets your condition - strictly higher than 5 degrees Celsius in this example. 

## Data source
The National Weather Service (NWS) provides the API endpoints that offer the data. A detailed documentation can be found at https://www.weather.gov/documentation/services-web-api.

## Side note
I have not built extensive error handling into this assignment. Please test it only with decent data.    
