release: ./release.sh
analysis_worker: PYTHONPATH="${PYTHONPATH}:$(pwd)" venv/bin/python src/time_series_analysis.py 
api_polling_worker: PYTHONPATH="${PYTHONPATH}:$(pwd)" venv/bin/python src/scheduler.py
web: PYTHONPATH="${PYTHONPATH}:$(pwd)" PORT="$PORT" venv/bin/python src/query_carbon_data.py 
