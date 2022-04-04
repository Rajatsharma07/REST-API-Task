import logging
from pathlib import Path

try:
    from flask import Flask
    from flask_cors import CORS
    import redis
    from rq import Queue
    import os
    import docker
except Exception as ex:
    logging.critical("Error: %s", ex)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname:<8} {message}",
    style="{",
    filename="%slog" % __file__[:-2],
    filemode="a",
)

""" Setting the global variables via ./run.sh """
USERNAME = os.environ.get("USERNAME")  # DockerHub username
PASSWORD = os.environ.get("PASSWORD")  # DockerHub password
image_name = os.environ.get("IMAGE_NAME")  # username/repository name
image_tag = os.environ.get("IMAGE_TAG")  # Image versioning
no_cache = os.environ.get("NO_CACHE")  # to build image from scratch

"""Setting the global variables directly """
# USERNAME = "yyyyyyyyy"
# PASSWORD = "xxxxxxx"
# image_name = "rajatsharma07/data_scientists_builds"
# image_tag = "V1.1"
# no_cache = True

logging.info(
    "Parameters: img_name: %s, img_tag: %s, no_cache: %s",
    image_name,
    image_tag,
    no_cache,
)
try:
    docker_client = docker.from_env()  # Initializing the Docker Client

except docker.errors.DockerException as ex:
    error_message = str(ex).lower()
    if ("connection refused" or "connection aborted") in str(error_message).lower():
        logging.critical("Docker is not running.... exiting the program")
        exit(0)

try:
    app = Flask(__name__)  # Initializing  the flask app
    cors = CORS(app, resources={r"*": {"origins": "*"}})
    redis_conn = redis.Redis()  # creates our Redis connection
    main_queue = Queue(connection=redis_conn)  # creates our task queue
    from app import routes, tasks  # import routes and tasks

    app.config["Dockefiles_Path"] = Path(
        "Dockefiles_Path"
    )  # Default folder to store Dockerfiles
except Exception as ex:
    logging.critical("Error: %s", ex)
    exit(0)
