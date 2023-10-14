from unittest import TestCase

from datetime import datetime
from src.fetch_data import CarbonIntensityCollector, INPUT_DATE_FORMAT, CarbonIntensityRecord, \
    ICarbonIntensityApiClient, CarbonIntensityApiClient


class TestCarbonIntensityCollector(TestCase):
    def setUp(self):
        from src.bootstrap import app, db
        app.app_context().push()
        db.create_all()

    class StubApiClient(ICarbonIntensityApiClient):
        def __init__(self, data: dict | None):
            self.data = data

        def get_carbon_intensity_data(self) -> dict:
            return self.data

    def test_collect_and_store_fake_data(self):
        fake_carbon_intensity_data = {
            "measurement_time_from": datetime.strptime("2018-01-20T12:00Z", INPUT_DATE_FORMAT),
            "measurement_time_to": datetime.strptime("2018-01-20T12:30Z", INPUT_DATE_FORMAT),
            "intensity_forecast": 266,
            "intensity_actual": 263,
            "intensity_index": "moderate"
        }
        carbon_intensity_collector = CarbonIntensityCollector(self.StubApiClient(fake_carbon_intensity_data))
        carbon_intensity_collector.collect_and_store()
        CarbonIntensityRecord.query.filter(
            CarbonIntensityRecord.measurement_time_from == datetime.strptime("2018-01-20T12:00Z", INPUT_DATE_FORMAT)
        ).first()

    def test_collect_and_store_no_data(self):
        carbon_intensity_collector = CarbonIntensityCollector(self.StubApiClient(None))
        carbon_intensity_collector.collect_and_store()

    # verify that collect and store works with the real API client
    def test_collect_integrated(self):
        prev_count = CarbonIntensityRecord.query.count()
        carbon_intensity_collector = CarbonIntensityCollector(CarbonIntensityApiClient())
        carbon_intensity_collector.collect_and_store()
        new_count = CarbonIntensityRecord.query.count()
        self.assertEqual(prev_count + 1, new_count)
