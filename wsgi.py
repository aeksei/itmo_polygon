import sys

# add your project directory to the sys.path
project_home = u'/home/aeksei/games_dash'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# need to pass the flask app as "application" for WSGI to work
# for a dash app, that is at app.server
# see https://plot.ly/dash/deployment
from main import app
application = app.server
