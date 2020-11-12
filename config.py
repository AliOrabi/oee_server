import logging
import os


class Config(object):

    # Run the server in a demo mode, with fake data and an intro screen
    DEMO_MODE = False

    # PostgreSQL database
    DATABASE_USER = os.environ.get('DATABASE_USER') or "postgres"
    DATABASE_ADDRESS = os.environ.get('DATABASE_ADDRESS') or "192.168.0.200"
    DATABASE_PORT = os.environ.get('DATABASE_PORT') or "5432"
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD') or "Pendle#"
    if DEMO_MODE:
        DATABASE_NAME = "oee_webapp_demo"
    else:
        DATABASE_NAME = os.environ.get('DATABASE_NAME') or "oee_webapp"
    SQLALCHEMY_DATABASE_URI = "postgres://{user}:{password}@{address}:{port}/{database}".format(
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        address=DATABASE_ADDRESS,
        port=DATABASE_PORT,
        database=DATABASE_NAME)

    # SQLite database
    # package_dir = os.path.abspath(os.path.dirname(__file__))
    # db_path = os.path.join(package_dir, 'app', 'prod.db')
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_ECHO = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or "yS7o773kuQ"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.realpath(os.path.join('app', 'static', 'uploads'))

    if not os.path.exists('logs'):
        os.mkdir('logs')

    STREAM_LOGGING_LEVEL = logging.DEBUG
    FILE_LOGGING_LEVEL = logging.DEBUG
    FLASK_LOG_FILE = 'logs/oee_app.log'
    ROTATING_LOG_FILE_MAX_BYTES = 1024000
    ROTATING_LOG_FILE_COUNT = 10
    LOG_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # The database IDs for activity codes
    NO_USER_CODE_ID = 1
    UNEXPLAINED_DOWNTIME_CODE_ID = 2
    UPTIME_CODE_ID = 3  # Preferably 0 to keep it on the bottom of the graph
    SETTING_CODE_ID = 4

    MACHINE_STATE_OFF = 0
    MACHINE_STATE_RUNNING = 1
