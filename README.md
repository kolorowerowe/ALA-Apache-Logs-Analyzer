# ALA-APACHE-LOGS-ANALYZER

Szymon Borowy, Dominik Kołodziej, Jakub Semczyszyn

Bespieczeństwo Systemów Informatycznych
2021

## Installation

1. Open project directory
2. Install requirements (optional):
`pip install -r requirements.txt` or `python -m pip install -r requirements.txt`
`pip install libgraphviz-dev`
`pip install pygraphviz`
3. Place log file in data folder
4. Set app parameters in config.yml file:

filenames:
- logs - name of log file in *data* folder
- model - name of machine learning model files in *models* folder
- mldf_csv - desired name of output file containing logs parsed for machine learning, located in *results* folder
- logscounter_csv - desired name of output file containing logs parsed for visualization, located in *results* folder
- bad_users - name of file containing suspicious user agents list in *data* folder
- bad_referers - name of file containing suspicious referers list in *data* folder

email:
- address - email address used to send report via SMTP package
- password - password to the aforementioned email account
- recipients (list) - a list of email addresses to which the message will be sent

other:
- extensionsToRemove (list) - a list of file extensions that will be omitted in visualization
- flow_max - the maximal value of graph edges
- event_max - the maximal value of graph vertices
- verbosity - logging level: 0-3 - level 0 means, that only program start and finish messages will be displayed, level 1 allows for displaying current execution phase, level 2 displays time measurements, level 3 logs prediction results to the terminal

5. Run app:
`python ./ala/main.py`
