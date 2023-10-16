# Carbon Intensity Data Collection
![Build status](https://github.com/EnergizeStatistics/capstone-csca5028/actions/workflows/python-app.yml/badge.svg)

This project is the capstone assignment of csca5028. This application: 

1. pulls carbon impact data from a public API,
1. stores the data in a database,
1. provides a web front end where a user can request statsitical analysis of subsets of the data,
1. performs said analysis asyncronously, and
1. presents the results to the user.

The end result looks like this:

![app demo](/documentation/assets/App%20demo.png)


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

The setup for this project is rather involved. It can be installed locally or it can be deployed to heroku. Depending on which you choose, how you setup the dependent services will change quite a bit.

### Local Installation

This project was locally developed on a virtual machine running Ubuntu 22.04.3 LTS.  Supposing your environment is similar,

#### Bring in dependencies

1. clone this repository.
1. install bash or a bash-compatible shell if you don't have one already.
1. in that shell, change directory to the root directory of this repository.
1. from there, run `sudo ./release/apt-get.sh` to install various packages.
1. then, run `sudo ./release/docker.sh' to get docker
1. then, run `sudo ./release/python.sh` to get python (3.10.12)
1. then, run `sudo ./release/rabbitmq.sh` to get and start a rabbit mq docker container. If your container stops (say, after a reboot), you may rerun this command to restart your container.
1. enter the python virtual environment with `python3 -m venv venv && source venv/bin/activate`
1. install python requirments with `pip install -r requirements.txt`

#### Start the services

1. Optionally, open a terminal tab and attach to your rabbitmq server if you'd like to monitor it.
1. document setup of our local statsd / graphite docker container.
1. open a terminal tab and enter the python virtual environment.  Start the service which pulls data from the public carbon insights API with this command: `PYTHONPATH="${PYTHONPATH}:$(pwd)" venv/bin/python src/scheduler.py`
1. open another terminal tab and again enter the python virtual environment.  Start the service which performs statistical analysis of carbon data with this command: `PYTHONPATH="${PYTHONPATH}:$(pwd)" venv/bin/python src/time_series_analysis.py`
1. open a third terminal tab and enter the python virtual environment. Start the web server with the following command: `PYTHONPATH="${PYTHONPATH}:$(pwd)" venv/bin/python src/query_carbon_data.py` By default, it will listen on port 5000, though you can specify another port with the PORT environment variable.

Note that although the heroku-hosted installation instructions include setting up a mysql component, we don't have an analogous step here.  Instead, when running locally we use sqlite.

### Heroku & hosted services installation

This project has requirements for a product environment, monitoring, CI, etc. To demonstrate these, a local setup won't cut it. Let's get to it:

1. clone this repository to your own github account.
1. configure your branches thus:
![branch setup](/documentation/assets/Github%20Branch%20Setup.png)
1. link it to your own heroku account TODO: document this process.
1. under the resources tab in heroku, add the 3 add-ons you see here:
![heroku resources](/documentation/assets/heroku%20resources.png)
1. For the hosted graphite add-on, enter its management interface and find the StatsD add-on for it.  Yes, we're grabbing an add-on for an add-on.
![its add-ons all the way down](/documentation/assets/Hosted%20StatsD%20addon.png)
1. While you're there, take note of the URL and API key shown to you on that page.
1. head to the settings page on heroku and display the config vars. Most of these will be populated for you by the addons, but you'll need to add the statsd configuration variables.
![heroku config vars](/documentation/assets/heroku%20config%20vars.png)
1. the last piece of heroku configuration we do is the heroku deployment page. You can see what these settings will be now, but probably you don't want to set these up until you've succeeded with a manual deployment.
![heroku deploy](/documentation/assets/heroku%20deploy.png)

### Build

During branch setup, you saw that we have a build process setup in github actions. If you make a pull request against main, you'll see that run. However, it'd be good to test that it's building for you before you make any changes. You can manually run the build process like so:

![manual build](/documentation/assets/Run%20github%20workflow.png)

Incidentally, you can find included in the output of that build the results of the unit and integration tests.

![Github build output](/documentation/assets/Github%20build%20output.png)

Supposing that works well, it's worth trying it out on heroku.  From the deployment tab, manually deploy main.

From the resources tab, verify that all of the dynos are enabled.

Even supposing that succeeds, it's worth glancing at the logs for all 3 heroku dynos to make sure there are no obvious problems at startup.

### Test

To start with, peek at the logs for the api_polling_worker dyno. There will be no data to look at until that's written at least once.

Note that the polling worker is only pulling the most recently available data, so you won't have much history to query.  Also note that "most recently available" will be recent, but it may not be completely current.

Once you have a bit of data, click `Open App` and enter a time period to analyze. Time periods need to be on the half-hour for the form to validate (as this is the granularity of the measurements that were taken) and obviously you need to include the time during which data was collected.

## Metrics

We push custom statsd metrics for the responsiveness of the carbon intensity api we're polling, for our own statistical calculations, as well as general usage statistics. Flask also pushes some standard statsd metrics. Each of the add-on services of course have their own built-in metrics. This section aims to help you find all of these. (Heroku and Github provide metrics as well, but I assume you already know how to find those at this point in the course.)

JawsDB provides just basic service health information:

![jawsdb](/documentation/assets/jawsdb%20mysql%20dashboard.png)

The RabbitMQ add-on has a management interface showing metrics including (most interestingly for our project) stats about our celery queue:

![Rabbit MQ dashboard](/documentation/assets/Rabbit%20MQ%20dashboard.png)

For locally run Rabbit MQ, stats are kept in the docker container. You'd need to expose the port, login, and view the metrics.  

Graphite is where you can find our custom metrics, our standard stats d metrics, and also graphite's own metrics.

Since some of these are custom metrics, they won't be on a dashboard by default and you'll need to drag them from the tree to create a graph. To help make the data more apparent, I suggest zooming into a small window of time (2h or so) and perhaps choosing area charts since the dots are so scarce that they can be easy to overlook otherwise.

![Graphite metrics](/documentation/assets/Graphite%20metrics.png)

Graphite's dashboard is pretty much the same for the local environment as it is with the hosted deployment, though of course you'll access it at a local url and at a port mapped to the docker container.

## Internal API documentation

## File explanations

### todo!

### `config.json`

- **Description:** This file stores project configuration settings, such as how often to poll the carbon intensity API.

### `database/`

- **Description:** This directory holds the database used by the project when run locally. It is not used when deployed on heroku. 

### `templates/`

- **Description:** This directory stores the html templates required by the front end. index.html is the only file typically used, as further communication between the browser and the web server happen through an REST api. However, should javascript be unavailable, the project degrades to using the other html template files.

### `requirements.txt`

- **Description:** The `requirements.txt` file lists all the project dependencies required to run the code.

### `.project_root_marker`

- **Description:** This file is used by one of the helper functions to locate the project root. 


## Data source
Carbon intensity data is provided by https://carbon-intensity.github.io/api-definitions/#get-intensity

## Side note
Please remember that you're likely testing on mostly free-tier resources, so don't spam requests to aggressively.
