from bootstrap import app, db, statsd_client, celery
from src.fetch_data import CarbonIntensityRecord
import pandas as pd
import time


class CarbonIntensityAnalyzer:
    def __init__(self, from_dt, to_dt):
        self.from_dt = from_dt
        self.to_dt = to_dt

    def load_data_from_db(self):
        with app.app_context():
            # Query the database to retrieve all rows

            results = db.session.query(CarbonIntensityRecord.measurement_time_from,
                                       CarbonIntensityRecord.measurement_time_to,
                                       CarbonIntensityRecord.intensity_actual,
                                       CarbonIntensityRecord.intensity_forecast,
                                       CarbonIntensityRecord.intensity_index) \
                .filter(CarbonIntensityRecord.measurement_time_from.between(self.from_dt, self.to_dt),
                        CarbonIntensityRecord.measurement_time_to.between(self.from_dt, self.to_dt)
                        ) \
                .all()

            # Create a Pandas DataFrame from the query result
        df = pd.DataFrame([{
            'measurement_time_from': entry.measurement_time_from,
            'measurement_time_to': entry.measurement_time_to,
            'intensity_forecast': entry.intensity_forecast,
            'intensity_actual': entry.intensity_actual,
            'intensity_index': entry.intensity_index,
        } for entry in results])

        return df

    def preprocess_data(self, df):
        # Sort the DataFrame by measurement_time_from (optional)
        df = df.sort_values(by='measurement_time_from')

        # Fill NaN values with the last valid value (carry forward)
        df = df.ffill()

        df = df.drop_duplicates(subset=('measurement_time_from',
                                        'measurement_time_to',
                                        'intensity_forecast',
                                        'intensity_actual',
                                        'intensity_index'), keep='first')

        return df


    def calculate_statistics(self, df):
        # Calculate mean, median, variance, and standard deviation
        mean_values = df['intensity_actual'].mean()
        median_values = df['intensity_actual'].median()
        variance_values = df['intensity_actual'].var()
        std_deviation_values = df['intensity_actual'].std()

        # measurement_period_from = df['measurement_time_from'].min()
        # measurement_period_to = df['measurement_time_to'].max()

        return (mean_values,
                median_values,
                variance_values,
                std_deviation_values)

    def analyze(self) -> tuple:
        start = time.time()

        # Load data from the database
        data_df = self.load_data_from_db()

        if data_df is None or 0 == len(data_df):
            return None, None, None, None

        # Preprocess the data (carry forward NaN values)
        data_df = self.preprocess_data(data_df)

        result = self.calculate_statistics(data_df)
        millisecond_duration = int((time.time() - start) * 1000)
        statsd_client.timer("analyze", millisecond_duration)
        return result


@celery.task(retry_kwargs={'max_retries': 3})
def analyze(from_dt, to_dt):
    analyzer = CarbonIntensityAnalyzer(from_dt, to_dt)
    result = analyzer.analyze()
    output = from_dt, to_dt, result
    return output


if __name__ == "__main__":
    worker = celery.Worker()
    worker.start()
