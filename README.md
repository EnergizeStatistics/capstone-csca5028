# Carbon Intensity Data Reporting System
![Build status](https://github.com/EnergizeStatistics/capstone-csca5028/actions/workflows/python-app.yml/badge.svg)

This project is the capstone assignment of the Application course. This application: 

1. pulls carbon intensity data from a public API,
1. stores the data in a database,
1. provides a web front end where a user can request a report of the data,
1. performs said analysis asynchronously,
1. presents the results to the user.

The end result looks like this:

![app demo](documentation/assets/App%20demo.png)

## Table of Contents
- [Rubric coverage](#rubric-coverage)
- [Setup](#setup)
 - [Installation](#installation)
 - [Building](#building)
 - [Testing](#testing)
- [Metrics](#metrics)
- [Usage](#usage)
- [Internal API documentation](#internal-api-documentation)
- [File explanations](#file-explanations)
- [Data source](#data-source)

## Rubric coverage
- **Web application basic form, reporting**: The web application provides a form where the user can enter a time period and request a statistical analysis of the data collected during that time period. The web application also provides a page where the user can view the results of the analysis.
- **Data collection**: The web application collects data from a public API that provides carbon intensity measurements.
- **Data analyzer**: Per user request, the web application provides summary statistics of the data collected.
- **Unit tests**: Unit tests are included in the `tests/test_fetch_data.py` file.
- **Data persistence, any data store**: The web application stores the data collected in a MySQL database.
- **Rest collaboration internal or API endpoint**: The web application uses an internal REST API to request and retrieve reports. Additionally, the data collection component of the system pulls carbon intensity measurements from a public REST API.
- **Product environment**: The web application is deployed on Heroku.
- **Integration tests**: Integration tests are also included in the `tests/test_fetch_data.py` file. Refer to the `test_collect_integrated` function.
- **Using mock objects or any test doubles**: The `test_collect_and_store_fake_data` function in the `tests/test_fetch_data.py` script contains a canned answer to the calls made to the public API. There are various kinds of test doubles; according to this [blog entry of Martin Fowler's](https://martinfowler.com/bliki/TestDouble.html), this type of test double is called a "stub".
- **Continuous integration**: The project uses GitHub Actions for continuous integration. The workflow is defined in the `.github/workflows/python-app.yml` file.
- **Production monitoring instrumenting**: The project is instrumented with StatsD and uses Graphite to monitor the application. Refer to the Metrics section in this README for details. 
- **Event collaboration messaging**: The web application uses RabbitMQ and Celery to exchange messages with the data analysis component of the system.
- **Continuous delivery**: The project uses Heroku for continuous delivery.

## Setup 

### Installation

This project was gradually developed - deployment was first local, and later deployment to Heroku was added. The instructions below are for the Heroku deployment. However, some files and dependencies that are only required for local deployment are still present in the repository.

1. Fork [this repository](https://github.com/EnergizeStatistics/capstone-csca5028) to your own GitHub account.
1. Configure your main branch as shown in the image below:
![branch setup](documentation/assets/Github%20Branch%20Setup.png)
1. Link your fork to your own Heroku account. There are many guides available online. I used https://medium.com/featurepreneur/how-to-connect-github-to-heroku-be6ff27419d3
1. Under the Resources tab in Heroku dashboard, add these 3 add-ons:
![heroku resources](documentation/assets/heroku%20resources.png)
1. For the hosted Graphite add-on, enter its management interface and find the StatsD add-on for it. Add that as well. Take note of the URL and API key.
![its add-ons all the way down](documentation/assets/Hosted%20StatsD%20addon.png)
1. Configure the configuration variables of StatsD in Heroku's settings page -> config vars. Most of these config vars will be automatically populated by the addons, but you need to add the StatsD configuration variables.
![heroku config vars](documentation/assets/heroku%20config%20vars.png)
1. Under the Deploy tab in Heroku dashboard, we can see what these settings are at this point. Come back to these settings after you have succeeded with a manual deployment.
![heroku deploy](documentation/assets/heroku%20deploy.png)

### Building

We have a build process that depends on GitHub Actions. If you make a pull request against the main branch, it will run. To test that our process is building in your setup before you make any further changes, you can manually run the build process like so:

![manual build](documentation/assets/Run%20github%20workflow.png)

Incidentally, the results of the unit and integration tests are included in the results of a build.

![Github build output](documentation/assets/Github%20build%20output.png)

If the build finishes successfully on GitHub, we move forward to trying it out on Heroku.

From the Deploy tab, manually deploy using the main branch.

From the Resources tab, verify that all Heroku dynos are enabled.

At this point, even if the steps above are successful, I still personally find it worthwhile to check the log for all 3 Heroku dynos, in order to make sure there are no obvious problems at startup. 

### Testing

The first step is to check the log for the `api_polling_worker` dyno. There ought to be no data, till that has written at least once.

Note that the pulling worker only pulls the most recently available data, so you won't have much history to query.

Once you have accumulated a reasonable amount of data, click `Open App` and enter a time period to analyze. Time periods need to be on the half-hour for the form to validate (as this is the granularity of the carbon intensity measurements). And obviously you need to include your time window during which data was collected.

## Metrics

We provide custom StatsD metrics for [the responsiveness of the carbon intensity API we're polling](https://github.com/EnergizeStatistics/capstone-csca5028/blob/854bbe43f44c258028d5d52373fbc57077d33fcc/src/fetch_data.py#L60-L63), for [our own statistical calculations](https://github.com/EnergizeStatistics/capstone-csca5028/blob/cbb64f58b7ce0262a1917f48981da6491ace58ec/src/time_series_analysis.py#L79-L81), as well as general usage statistics. Flask also provides some standard StatsD metrics. Each of the add-on services has its own built-in metrics. This section aims to help you find all of these.

JawsDB provides just basic service health information:

![jawsdb](documentation/assets/jawsdb%20mysql%20dashboard.png)

The RabbitMQ add-on has a management interface that shows metrics. The most informative stats about our Celery queue can be found under Queues and Streams:

![Rabbit MQ dashboard](documentation/assets/Rabbit%20MQ%20dashboard.png)

Graphite is where you can find our custom metrics, our standard StatsD metrics, and also Graphite's own metrics.

Since some of these are custom metrics, they won't be on any dashboard by default, and you'll need to drag them from the tree to create a graph. To help make the data more apparent, I suggest zooming into a small window of time (2h or so) and perhaps choosing area charts since the dots are so scarce that they can be easy to overlook otherwise.

![Graphite metrics](documentation/assets/Graphite%20metrics.png)

## Usage

From the end user's perspective, the app presents as a single page web application. The user can enter a time period and request a statistical analysis of the data pertaining to that time period. The results are presented to the user when the report is ready.

## Design documentation

The below sequence diagram depicts our four applications as *controls*. Three of those are our heroku dynos, with the fourth being a javascript application running on the user's browser.

The user and the four controls exchange data through a series of barriers. In some cases, the data exchange is through RESTful APIs.

![Sequence Diagram](documentation/assets/cs5028%20capstone%20sequence.png)

Please forgive the few omitted activation windows -- we were hitting the limits of the free plan for the UML generaton tool.

## Internal API documentation

The only resource is the `/report` resource.

`GET /report/<id>`
- returns a json object of the form:
```
"report": {
    "attr": {
        "id": string,
        "from_dt": string,
        "to_dt": string,
        "state": "PENDING"|"SUCCESS"|"FAILURE",
        "mean_values": 'NaN' | number,
        "median_values": 'NaN' | number,
        "variance_values": 'NaN' | number,
        "std_deviation_values": 'NaN' | number,
    },
    "rel": {
        "self": string (url)
    }
}
```

Note that some fields may be omitted depending on the state of the report.

`POST /report` 
- expects `from_datetime_str` and `to_datetime_str`, both in `%Y-%m-%dT%H:%M` format.
- returns a json object of the same form as the GET request.


## File explanations

### `database/`

- This directory holds the database used by the project when run locally. It is not used when deployed on heroku. 

### `release/`

- This directory stores the scripts used to build a local release of the project. It is not used when deployed on heroku. `release-local.sh` simply invokes these scripts in a suitable sequence.

### `src/`

- This directory stores the source code of the project. These scripts below are of particular interest.
- `src/fetch_data.py`
- - This script contains the main function that pulls data from the carbon intensity public API and stores it in the database. It is regularly invoked by the `src/scheduler.py` script.
- `src/query_carbon_data.py`
- - This script runs a web server that provides the front end for the user to request statistical analysis of the data.
- `src/time_series_analysis.py`
- - This script contains the main function that performs statistical analysis on the data. It is invoked by the celery worker.

### `src/templates/`

- This directory stores the html templates required by the front end. `index.html` is the only file typically used, as further communication between the browser and the web server happens through an REST api.

### `src/assets/`

- This directory stores the css and javascript files which power the front end.

### `venv/`

- This directory stores the virtual python environment used by the project.

### `tests/`

- This directory stores pytest unit and integration tests for the project.

### `config.json`

- This file stores project configuration settings, such as how often to poll the carbon intensity API.

### `Procfile`

- This file is used by Heroku to start the web server and other dynos.

### `release.sh`

- This file is used by Heroku to build a release of the project.

### `runtime.txt`

- We specify the python interpreter version that we want Heroku to use.

### `requirements.txt`

- We specify the python dependencies of the project. Heroku installs these libraries.

### `build_apt-get.sh`, `build_requirements.sh`, `build_runtime.sh`

- These files are used to generate lists of dependencies of the project. For example, `build_requirements.sh` generates a list of python dependencies.

## Data source
Carbon intensity data is provided by https://carbon-intensity.github.io/api-definitions/#get-intensity


