## Project

# Face Attribute Aggregation System

## Overview

A microservice-based(gRPC) system for detecting face landmarks, age/gender and storing attributes in JSON files using gRPC and Redis.

## Architecture

The application is divided to 4 services:

- **`Image Input`**: Reads images, sends to Face Landmark Detection and Age/Gender Estimation services.
- **`Face Landmark Detection`**: It gets image data from the `Image Input` service and detects landmarks of person(s) in the image, and finally saves the results as JSON to Redis.
- **`Age/Gender Estimation`**: It gets image data from the `Image Input` service and detects age(s) and gender(s) of person(s) in the image, and finally saves the results as JSON to Redis.
- **`Data Storage`**: It saves the image as a JPEG file and other combined attributes as JSON.

### Proto file

The service architecture details are in the `image_processing.proto` file.
It has 4 services, and each service has input and output separately. Each input and output has its own structure. For example service `ImageInput` is as below:

```
// Service 1: Image Input Service
service ImageInput {
  rpc ProcessImage(ImageRequest) returns (CombinedResponse) {}
}

// Message to carry image data
message ImageRequest {
  bytes image_data = 1;
}

// Message for Service 1 combined response
message CombinedResponse {
  string status = 1;
  LandmarkResponse landmark_response = 2;
  AgeGenderResponse age_gender_response = 3;
}

```
This is the output of `ImageInput` service:
```
2025-05-13 01:31:13,834 - INFO - Initialized stubs for Face Landmark Detection and Age Gender Estimation
2025-05-13 01:31:13,837 - INFO - Image Input Service running on [::]:50051...
2025-05-13 01:31:13,916 - INFO - Received image data for processing
2025-05-13 01:31:16,721 - INFO - Face Landmark Detection responded: Success
2025-05-13 01:31:20,194 - INFO - Age Gender Estimation responded: Success
2025-05-13 01:31:20,198 - INFO - Processed SingleFace3.jpg: Success
2025-05-13 01:31:20,198 - INFO - Landmark Detection: Success, Runtime: 2.7903292179107666
2025-05-13 01:31:20,198 - INFO - Age Gender Estimation: Success, Runtime: 3.4611012935638428
```
### Detection

For landmark and age/gender detection, I used the [`insightface`](https://github.com/deepinsight/insightface) Python library. However there are other options like [DeepFace](https://github.com/serengil/deepface), [SSR-NET](https://github.com/shamangary/SSR-Net), [FairFace](https://github.com/joojs/fairface), [MiVOLO](https://huggingface.co/Genius-Society/MiVOLO), [ViT](https://huggingface.co/nateraw/vit-age-classifier), and [OpenCV DNN (Caffe model)]()

The final result is like this JSON file:

```
{
    "redis_key": "881ef8f5e8c025c6fbbf04dfdd80b3c144f45b5f4b0773530e67264dae13461e",
    "image_path": "./output/881ef8f5e8c025c6fbbf04dfdd80b3c144f45b5f4b0773530e67264dae13461e.jpg",
    "results": {
        "landmark_service": {
            "landmarks": [
                [
                    105,
                    137,
                    238,
                    339
                ],
                [
                    654,
                    67,
                    797,
                    256
                ],
                [
                    407,
                    300,
                    529,
                    465
                ]
            ]
        },
        "agegender_service": {
            "age": [
                35,
                55,
                29
            ],
            "gender": [
                "Male",
                "Male",
                "Female"
            ]
        }
    }
}
```

## Running Locally

### Setup & Run

1. Prepare a virtual environment for running Python:

- `python3 -m venv myenv`
- `source myenv/bin/activate`
- `pip install -r requirements.txt`

2. Edit `config.json` for directories, service port, and Redis host and port.
3. Copy sample images to `./images`.
4. run `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. image_processing.proto` to create 2 `.py` files.
5. Check that ports `50051-50054`(defined in `config.json`) is free by running and killing process:
- `sudo lsof -i :50051`
- `sudo kill -9 <PID>`
6. Run the `run.sh` script to ensure dependencies and run each service in the correct order.

### Redis

If the redis-server is not ready, the app will raise an error. In order to check the Redis is ready or not, it can be checked by running `sudo netstat -tulnp | grep 6379` or `sudo netstat -tulnp | grep redis-server`. The default port of Redis is `6379`. 


The Redis service might be stopped, which can be started and stopped again by these commands:

- `/etc/init.d/redis-server stop`\
- `/etc/init.d/redis-server start`
## Running on Docker
For making Doker container based on these service we need to define `Dockerfile` and `docker-compose.yaml`

Since services have dependencies to eachother, we need to check these condistions like Redis and other ports(`50051-50054`) by using Docker `healthcheck`. 

In addition, for preventing local Redis to conflicts with Docker Redis, there is `"6380:6379"` in `docker-compose.yaml` which export port 6380 local to 6379 Docker.

For building, running and stoppong containers:
```
Docker Compose build
Docker Compose up -d
Docker Compose down
```
Docker will create 5 containers, including 4 services and Redis. Unfortuantely, Docker raised error when image input want to send image data to other services while locally it did not have problem.


