import os

import pandas as pd

from src.bootstrap import app, statsd_client
from flask import render_template, request, send_from_directory, jsonify
from datetime import datetime
from src.time_series_analysis import CarbonIntensityAnalyzer, analyze


@app.route('/')
def index():
    statsd_client.incr('index_page_visits')
    return render_template('index.html')


@app.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('assets', path)


@app.route('/report', methods=['POST'])
def create_report():
    statsd_client.incr('summary_page_visits')
    from_datetime_str = request.form['from_datetime']
    to_datetime_str = request.form['to_datetime']

    # Convert the form input strings to datetime objects
    from_dt = datetime.strptime(from_datetime_str, '%Y-%m-%dT%H:%M')
    to_dt = datetime.strptime(to_datetime_str, '%Y-%m-%dT%H:%M')

    # create_report_synchronously(from_dt, to_dt, from_datetime_str, to_datetime_str)
    return create_report_asynchronously(from_dt, to_dt)


def create_report_asynchronously(from_dt, to_dt):
    task = analyze.apply_async(args=[from_dt, to_dt])
    return jsonify({
        "report": {
            "attr": {
                "id": task.id,
                "from_dt": from_dt,
                "to_dt": to_dt,
                "state": "PENDING"
            },
            "rel": {
                "self": "/report/{}".format(task.id)
            }
        }
    }), 200


def create_report_synchronously(from_dt, to_dt, from_datetime_str, to_datetime_str):
    # Not used in the current implementation.
    # Create an instance of the CarbonIntensityAnalyzer class
    analyzer = CarbonIntensityAnalyzer(from_dt, to_dt)
    # Call the function to compute summary statistics
    results = analyzer.analyze()
    return render_results(results, from_datetime_str, to_datetime_str)


@app.route('/report/<report_id>')
def get_results(report_id):
    task = analyze.AsyncResult(report_id)
    return render_report_asynchronously(task, report_id)


def render_report_asynchronously(task, report_id):
    if task.state != 'SUCCESS':
        return jsonify({
            "report": {
                "attr": {
                    "id": task.id,
                    "state": task.state
                },
                "rel": {
                    "self": "/report/{}".format(task.id)
                }
            }
        }), 200
    from_dt, to_dt, results = task.get()
    mean_values, median_values, variance_values, std_deviation_values = results
    return jsonify({
        "report": {
            "attr": {
                "id": task.id,
                "from_dt": from_dt,
                "to_dt": to_dt,
                "state": "SUCCESS",
                "mean_values": 'NaN' if pd.isna(mean_values) else mean_values,
                "median_values": 'NaN' if pd.isna(median_values) else median_values,
                "variance_values": 'NaN' if pd.isna(variance_values) else variance_values,
                "std_deviation_values": 'NaN' if pd.isna(std_deviation_values) else std_deviation_values
            },
            "rel": {
                "self": "/report/{}".format(task.id)
            }
        }
    }), 200


def render_report_synchronously(task, report_id):
    # An option for non-js clients. Not used in the current implementation.
    if task.state == 'PENDING':
        return render_template('waiting_for_results.html', task_id=report_id)
    elif task.state == 'SUCCESS':
        results = task.get()
        from_dt, to_dt, results = results
        return render_results(
            results,
            from_dt.strftime('%Y-%m-%dT%H:%M:%S'),
            to_dt.strftime('%Y-%m-%dT%H:%M:%S')
        )
    elif task.state == 'FAILURE':
        return render_template('error.html', task_id=report_id)
    else:
        return render_template('waiting_for_results.html', task_id=report_id)


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
    app.run(debug=True, port=os.environ.get('PORT') or 5000, host=os.environ.get('HOST') or '0.0.0.0')
