


# REST API to Build & Push the docker image from input Dockerfile
This project takes **Dockerfile** as input through the File Upload web page, builds the image from the Dockerfile, and pushes this image to the DockerHub registry. It is composed of two background jobs, namely **build_job** and **push_job**. The push_job depends on the successful completion of the build_job and is only triggered afterwards.

The APIs are created using Python Flask framework. It uses Redis Queue (RQ) which is a Python library for queueing jobs and processing them in the background with workers. 
## API Endpoints

 - http://127.0.0.1:5000/  [**GET** Request] Base URL: It just displays the welcome message.
 - http://127.0.0.1:5000/build_push_image  [**GET/POST** Request] HTML webpage to upload the Dockerfile. 
 - http://127.0.0.1:5000/job_status?id=  [**GET** Request] - It checks the current status of the triggered jobs by providing the job **id** as input via querystring.

**NOTE:** The port number may change depending on the execution method - from the terminal or via the IDE itself.

## Dependencies

 - RQ requires Redis >= 3.0.0 and we have to make sure Redis server is
   installed and running successfully.
   
 - **Environment creation (apienv):** Create a conda/python environment with Python version 3.8.10 and higher and install all required dependencies specified in the **requirements.txt** file with **pip**.
 - Make sure Docker is installed and running successfully.
 
**NOTE:** Tested on MAC OS, there may be problems while running Redis Server on Windows.

## Script Parameters

 - **USERNAME**="rajatsharma07" (**DockerHub username**)
 - **PASSWORD**="xxxxxx" (**DockerHub password**)
 - **image_name**="rajatsharma07/data_scientists_builds" (**username/repository name**)
 - **image_tag**="V1.1" (**Image versioning**)
 -  **no_cache**="True" (build image from scratch)

## Steps to execute the code

 1. Activate **apienv** environment by running: ***conda activate apienv***.
 2. Start the RQ worker: In a separate terminal, follow the step-1 and then run the command ***rq worker*** from the root directory of the project.
 3. Unit tests can be run before the main services are executed. They are located in the **test.py** module.
 4. Start the services by executing **./run.sh** script by providing the appropriate script parameters mentioned above.

**NOTE:** Services can also be started by running the Python module **run.py** - but this requires commenting the os.environment parameters and uncommenting the input parameters defined in the **__ init __.py** module.
 
## Logging
The logs are created in the root directory with the file name: **__ init __.log**.

## Todos and Improvements
1. Dockerize Server
2. Adding script parameters to the file upload webpage
3. Add Swagger documentation
4. Use NGINX for deployment in production environment
