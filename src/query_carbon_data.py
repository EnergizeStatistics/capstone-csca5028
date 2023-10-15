import os

from src.bootstrap import app, statsd_client, db
from flask import render_template, request
from datetime import datetime
from src.time_series_analysis import CarbonIntensityAnalyzer, analyze

@app.route('/')
def index():
    statsd_client.incr('index_page_visits')
    return render_template('index.html')


@app.route('/summary', methods=['POST'])
def get_input():
    statsd_client.incr('summary_page_visits')
    from_datetime_str = request.form['from_datetime']
    to_datetime_str = request.form['to_datetime']

    # Convert the form input strings to datetime objects
    from_dt = datetime.strptime(from_datetime_str, '%Y-%m-%dT%H:%M')
    to_dt = datetime.strptime(to_datetime_str, '%Y-%m-%dT%H:%M')

    # respond_sync(from_dt, to_dt, from_datetime_str, to_datetime_str)
    return respond_async(from_dt, to_dt)


def respond_async(from_dt, to_dt):
    task = analyze.apply_async(args=[from_dt, to_dt])
    return render_template('waiting_for_results.html', task_id=task.id)


def respond_sync(from_dt, to_dt, from_datetime_str, to_datetime_str):
    # Create an instance of the CarbonIntensityAnalyzer class
    analyzer = CarbonIntensityAnalyzer(from_dt, to_dt)
    # Call the function to compute summary statistics
    results = analyzer.analyze()
    return render_results(results, from_datetime_str, to_datetime_str)


@app.route('/results/<task_id>')
def get_results(task_id):
    task = analyze.AsyncResult(task_id)
    if task.state == 'PENDING':
        return render_template('waiting_for_results.html', task_id=task_id)
    elif task.state == 'SUCCESS':
        results = task.get()
        from_dt, to_dt, results = results
        return render_results(
            results,
            from_dt.strftime('%Y-%m-%dT%H:%M:%S'),
            to_dt.strftime('%Y-%m-%dT%H:%M:%S')
        )
    elif task.state == 'FAILURE':
        return render_template('error.html', task_id=task_id)
    else:
        return render_template('waiting_for_results.html', task_id=task_id)


def render_results(results, from_datetime_str, to_datetime_str):
    mean_values, median_values, variance_values, std_deviation_values = results
    return render_template(
        'results.html',
        from_datetime=from_datetime_str,
        to_datetime=to_datetime_str,
        mean_values=mean_values,
        median_values=median_values,
        variance_values=variance_values,
        std_deviation_values=std_deviation_values
    )


if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 5000))
