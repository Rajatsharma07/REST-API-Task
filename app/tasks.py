import time, logging
from rq.decorators import job

try:
    from app import USERNAME, PASSWORD, docker_client
except Exception as ex:
    logging.critical("Error: %s", ex)


def login_docker_registry(username, password):
    """Method to login into Dockerhub account.

    Args:
        username (string): username
        password (string): password

    Returns:
        docker client: returns a docker client object.
    """
    docker_client.login(username, password)
    return docker_client


def remove_docker_image(image_name, image_tag):
    """Removes the docker image from the Docker registry.

    Args:
        image_name (string): name of the image
        image_tag (string): tag of the image

    Returns:
        docker image: Returns the corresponding docker image.
    """
    docker_client.images.remove(image_name + ":" + image_tag)
    return docker_client.images.get(image_name + ":" + image_tag)


def docker_image_exists(image_name, image_tag):
    """Method to check if the docker image with the same name & tag exists or not.

    Args:
        image_name (string): name of the image
        image_tag (string): tag of the image

      Returns:
        docker image: Returns the corresponding docker image.
    """
    return docker_client.images.get(image_name + ":" + image_tag)


# @job(main_queue, connection=redis_conn)
def build_docker_image(image_name, image_tag, dockerfile_path, nocache=True):
    """Builds the docker image from the Dockerfile in the specified path.

    Args:
        image_name (string): name of the image
        image_tag (string): tag of the image
        dockerfile_path (string): base directory where dockerfile is placed
        nocache (bool, optional): force build the new image, Defaults to True.

    Returns:
        docker image: Returns the corresponding docker image.
    """
    logging.info("Running docker image build task...")
    # time.sleep(10)
    docker_client.images.build(
        dockerfile=dockerfile_path,  # "Dockefiles_Path/fileupload_name.Dockerfile",
        path=".",  # Directory path, default is the current directory
        tag=image_name + ":" + image_tag,
        nocache=nocache,
    )
    logging.info(
        f"Docker image build task completed successfully - {image_name + ':' + image_tag}"
    )
    return docker_client.images.get(image_name + ":" + image_tag)


# @job(main_queue, connection=redis_conn)
def push_docker_image(image_name, image_tag):
    """Pushes the docker image to the Docker registry.

    Args:
        image_name (string): name of the image
        image_tag (string): tag of the image

    Returns:
        docker image: Returns the corresponding docker image.
    """
    client = login_docker_registry(USERNAME, PASSWORD)
    logging.info("Running docker image push task...")
    client.images.push(image_name + ":" + image_tag)
    logging.info(
        f"Docker image pushed successfully to the DockerHub - {image_name + ':' + image_tag}"
    )
    return client.images.get(image_name + ":" + image_tag)
