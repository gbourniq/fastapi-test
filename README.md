# fastapi-test

Dummy project to test the FastAPI REST framework, with no database

### Prerequisites

Anaconda / Miniconda to manage the virtual environment

In the terminal, run `make env` to create the virtual environment and install the dependencies (managed by poetry).

Activate conda environment
```
conda activate fastapitest
```

Source environment variables
```
source .env
```

### Start the webserver

Run `python run.py`

### Routes overview

This simple project creates 3 routes 
- "/" to serve the materialize css html page (GET)
- "/tutorial" which is a simple POST
- "/task/run/{name}/{task_id}" to trigger an async task which simply sleeps 3 seconds and writes to a log file (simulate heavy I/O operation)


### Async task demo

To demonstrate that FastAPI can handle a large number of incoming requests:

Modify the settings in `.env`:
- `RELOAD` from `True` to `False`
- `DEBUG` from `True` to `False`
- `WORKERS_COUNT` from `1` to `30`

Source `.env` and restart webserver:
```
source .env
python run.py
```

Run `ps -ef | grep python` to see the running workers

In 3 seperate terminal windows, run concurrently the following commands

`for i in {1..1000}; do curl -X POST "http://0.0.0.0:5700/task/run/GUILLAUME/$i" -H "accept: application/json"; done`

`for i in {1..1000}; do curl -X POST "http://0.0.0.0:5700/task/run/CHMIE/$i" -H "accept: application/json"; done`

`for i in {1..1000}; do curl -X POST "http://0.0.0.0:5700/task/run/MOYNE/$i" -H "accept: application/json"; done`

The webserver handles the 3000 requests within seconds!