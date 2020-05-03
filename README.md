# 500

A 5 player version of the classic card game 500.

### Deployment

Push code to the master branch and Heroku will automatically deploy the code.

Alternatively;

1. `pip install -r requirements.txt`
2. Run `gunicorn --worker-class eventlet -w 1 app:app`

### Testing

1. Open CLI in repo root
2. `pip install pytest`
3. `export PYTHONPATH=$(pwd)`
4. `pytest`
