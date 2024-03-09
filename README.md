# PWP SPRING 2024
# MökkiWahti
# Group information
* Risto Korhonen, risto.korhonen@student.oulu.fi
* Veli-Matti Veijola, veveijol@student.oulu.fi
* Aarni Ylitalo, aarni.ylitalo@student.oulu.fi
* Jeremias Körkkö, joona.korkko@student.oulu.fi

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


## Database

Database used in this project is SQLite.

## Deploying the API

The deploying instructions are made for linux based operating system, but the project can be deployed also to windows environment. Python installation is required.

Make a python virtual environment for the project and activate it:
```
python -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
```

Install the requirements:
```
pip install -r requirements.txt
```

Set FLASK_APP enviroment variable, initialize the database and run the api:
```
export FLASK_APP=mokkiwahti
flask init-db
flask run
```

## Tests

Run tests with the following command: 
```
python -m pytest
```

To see the test coverage:
```
python -m pytest --cov=mokkiwahti tests/
```