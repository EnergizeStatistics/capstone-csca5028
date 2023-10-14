import schedule
import time
from src.fetch_data import collect_and_store
import logging
from src.bootstrap import config

# The data source provides a new temperature measurement every 20 minutes.
GET_DATA_INTERVAL = config['data_retrieval']['interval_minutes']

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize a counter
counter = 0


# Function to increment the counter and run the task
def run_task_and_increment_counter():
    global counter
    counter += 1
    logging.info(f"Scheduled task #{counter} started.")
    collect_and_store()
    logging.info(f"Scheduled task #{counter} completed.")


# Run the job once immediately
run_task_and_increment_counter()

# Schedule the function to run every 30 minutes
schedule.every(GET_DATA_INTERVAL).minutes.do(run_task_and_increment_counter)

# Run the scheduled jobs
while True:
    schedule.run_pending()
    time.sleep(1)
