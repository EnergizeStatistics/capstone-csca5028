# https://carbon-intensity.github.io/api-definitions/#get-intensity
import time
# Example responses
#
# {
#   "data":[
#     {
#     "from": "2018-01-20T12:00Z",
#     "to": "2018-01-20T12:30Z",
#     "intensity": {
#       "forecast": 266,
#       "actual": 263,
#       "index": "moderate"
#     }
#   }]
# }
# {
#   "error":{
#     "code": "400 Bad Request",
#     "message": "string"
#   }
# }
# {
#   "error":{
#     "code": "500 Internal Server Error",
#     "message": "string"
#   }
# }

from typing import Protocol
import requests
import logging
from datetime import datetime
from src.bootstrap import app, config, db, statsd_client


interval_minutes = config['data_retrieval']['interval_minutes']
INPUT_DATE_FORMAT = "%Y-%m-%dT%H:%MZ"


class CarbonIntensityRecord(db.Model):
    __tablename__ = 'carbon_intensity_records'
    row_id = db.Column(db.Integer, primary_key=True)
    measurement_time_from = db.Column(db.DateTime)
    measurement_time_to = db.Column(db.DateTime)
    intensity_forecast = db.Column(db.Integer)
    intensity_actual = db.Column(db.Integer)
    intensity_index = db.Column(db.String(20))

# convert static functions to member functions of a new class


class ICarbonIntensityApiClient(Protocol):
    def get_carbon_intensity_data(self) -> dict | None:
        ...


class CarbonIntensityApiClient(ICarbonIntensityApiClient):
    def get_carbon_intensity_data(self) -> dict | None:
        start = time.time()
        response = requests.get("https://api.carbonintensity.org.uk/intensity")
        millisecond_duration = int((time.time() - start) * 1000)
        statsd_client.timing("carbon_intensity_api_request", millisecond_duration)
        if response.status_code in {200}:
            data = response.json()
            measurement_time_from = datetime.strptime(data['data'][0]['from'], INPUT_DATE_FORMAT)
            measurement_time_to = datetime.strptime(data['data'][0]['to'], INPUT_DATE_FORMAT)
            intensity_forecast = data['data'][0]["intensity"]["forecast"]
            intensity_actual = data['data'][0]["intensity"]["actual"]
            intensity_index = data['data'][0]["intensity"]["index"]

            carbon_intensity_data = {
                "measurement_time_from": measurement_time_from,
                "measurement_time_to": measurement_time_to,
                "intensity_forecast": intensity_forecast,
                "intensity_actual": intensity_actual,
                "intensity_index": intensity_index
            }

            return carbon_intensity_data

        else:
            print(f"Request failed with status code {response.status_code}")
            return None


class CarbonIntensityCollector:
    def __init__(self, api_client: ICarbonIntensityApiClient = None):
        if api_client is None:
            api_client = CarbonIntensityApiClient()
        self.api_client = api_client

    def collect_and_store(self):
        with app.app_context():
            # Create the database table if it doesn't exist
            db.create_all()
            # Get carbon intensity data
            carbon_intensity_data = self.api_client.get_carbon_intensity_data()
            if carbon_intensity_data:
                # Create a new entry in the database
                new_entry = CarbonIntensityRecord(measurement_time_from=carbon_intensity_data["measurement_time_from"],
                                                  measurement_time_to=carbon_intensity_data["measurement_time_to"],
                                                  intensity_forecast=carbon_intensity_data["intensity_forecast"],
                                                  intensity_actual=carbon_intensity_data["intensity_actual"],
                                                  intensity_index=carbon_intensity_data["intensity_index"])
                db.session.add(new_entry)
                db.session.commit()
                logging.info("Carbon intensity data has been stored in the database.")


__instance = CarbonIntensityCollector()


def collect_and_store():
    return __instance.collect_and_store()


if __name__ == "__main__":
    pass
