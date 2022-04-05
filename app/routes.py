import logging

try:
    from pathlib import Path
    from rq.registry import FailedJobRegistry
    from flask import request, render_template

    from app import app
    from app import (
        no_cache,
        image_name,
        image_tag,
        main_queue,
        redis_conn,
    )
    from app.tasks import build_docker_image, push_docker_image, docker_image_exists
    import rq
except Exception as ex:
    logging.critical("Error: %s", ex)


# Defining Routes
@app.route("/")
def index():
    return (
        {"message": "Welcome to the Docker Build, Push & Check Status API."},
        200,
        {"Content-Type": "application/json"},
    )


@app.route("/build_push_image", methods=["GET", "POST"])
def build_push_image():
    """[GET & POST apis to upload a Dockerfile, Build & Push the Docker Image.]

    Returns:
        [HTML templates]: [File upload & task HTML templates.]
    """
    if request.method == "POST":
        try:
            if request.files:
                uploaded_file = request.files[
                    "dockerfile"
                ]  # Fetching the filestream object
                if uploaded_file:
                    dockefiles_folder = app.config[
                        "Dockefiles_Path"
                    ]  # Default folder to store Dockerfiles
                    Path(dockefiles_folder).mkdir(parents=True, exist_ok=True)
                    uploaded_file.save(dockefiles_folder / uploaded_file.filename)
                    build_no_cache = no_cache  # Fetching the no_cache flag

                    # Intializing the queue variables
                    build_job, push_job, build_job_msg, push_job_msg, jobs_count = (
                        None,
                        None,
                        None,
                        None,
                        None,
                    )

                    if (
                        not build_no_cache
                    ):  # to use the old docker image (if exists) to push to dockerhub
                        try:
                            docker_image_exists(
                                image_name, image_tag
                            )  # to check if the image already exists

                            push_job = main_queue.enqueue(
                                push_docker_image,
                                args=(image_name, image_tag),
                            )  # Send a docker push job to the task queue
                        except:
                            logging.info(
                                "Docker image does not exist. Building a new image...."
                            )
                            build_no_cache = True

                    if build_no_cache:
                        build_job = main_queue.enqueue(
                            build_docker_image,
                            args=(
                                image_name,
                                image_tag,
                                str(Path(dockefiles_folder / uploaded_file.filename)),
                                build_no_cache,
                            ),
                        )  # Send a job to the task queue to build the image

                        push_job = main_queue.enqueue(
                            push_docker_image,
                            args=(image_name, image_tag),
                            depends_on=build_job,
                        )  # Send a docker push job to the task queue

                    jobs = main_queue.jobs  # Get a list of jobs in the queue

                    if build_job:
                        logging.info("Build job id: %s", build_job.id)
                        build_job_msg = f"Build job with {build_job.id} is queued at {build_job.enqueued_at.strftime('%a, %d %b %Y %H:%M:%S')}"

                    if push_job:
                        logging.info("Push job id: %s", push_job.id)
                        push_job_msg = f"Push Job with {push_job.id} is queued."

                    count_queued_jobs = f"{len(main_queue)} job(s) in the queue."

                    return (
                        render_template(
                            "task_template.html",
                            build_job_msg=build_job_msg,
                            push_job_msg=push_job_msg,
                            jobs_count=count_queued_jobs,
                            jobs=jobs,
                        ),
                        201,
                    )
                return (
                    {"success": False, "message": "no Dockerfile uploaded"},
                    400,
                    {
                        "ContentType": "application/json"
                    },  # message displayed to the client when file was not uploaded sucessfully)
                )
        except Exception as ex:
            logging.critical("Error: %s", ex)
            return (
                {
                    "success": False,
                    "message": "an error occured, kindly check the logs",
                },
                400,
                {"Content-Type": "application/json"},
            )
    return (
        render_template("upload_template.html"),
        200,
    )  # File upload template to upload the Dockerfile


# Flask API to get the status of the job
@app.route("/job_status", methods=["GET"])
def job_status():
    """API to retrieve the status of successful or failed jobs.

    Returns:
        object: JSON objects having success flag, exceptions if any or messages.
    """
    if request.args.get("id"):
        try:
            job = rq.job.Job.fetch(request.args.get("id"), connection=redis_conn)
            failed_jobs = FailedJobRegistry(queue=main_queue).get_job_ids()
            if request.args.get("id") in failed_jobs:
                return (
                    {
                        "success": False,
                        "message": f"Job is in {job.get_status(refresh=True)} status",
                        "error": str(job.exc_info),
                    },
                    200,
                    {"ContentType": "application/json"},
                )
            success = job.is_finished
            return (
                {
                    "success": success,
                    "message": f"Job is in {job.get_status(refresh=True)} status",
                },
                200,
                {"Content-Type": "application/json"},
            )
        except rq.exceptions.NoSuchJobError as ex:
            logging.critical("Error: %s", ex)
            return (
                {
                    "success": False,
                    "message": "No job found with the given id",
                },
                200,
                {"Content-Type": "application/json"},
            )
        except Exception as ex:
            logging.critical("Error: %s", ex)
            return (
                {
                    "success": False,
                    "message": "an error occured, kindly check the logs",
                },
                400,
                {"Content-Type": "application/json"},
            )
    return (
        {"success": False, "message": "No job id is provided"},
        400,
        {"ContentType": "application/json"},
    )
