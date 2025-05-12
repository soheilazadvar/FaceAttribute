import grpc
import image_processing_pb2
import image_processing_pb2_grpc
from concurrent import futures
import cv2
import numpy as np
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageInputService(image_processing_pb2_grpc.ImageInputServicer):
    def __init__(self, landmark_address, age_gender_address):
        self.landmark_channel = grpc.insecure_channel(landmark_address)
        self.age_gender_channel = grpc.insecure_channel(age_gender_address)
        self.landmark_stub = image_processing_pb2_grpc.FaceLandmarkDetectionStub(self.landmark_channel)
        self.age_gender_stub = image_processing_pb2_grpc.AgeGenderEstimationStub(self.age_gender_channel)
        logger.info("Initialized stubs for Face Landmark Detection and Age Gender Estimation")

    def ProcessImage(self, request, context):
        try:
            logger.info("Received image data for processing")
            # Send to Service 2 (Face Landmark Detection)
            landmark_response = self.landmark_stub.DetectLandmarks(request)
            logger.info(f"Face Landmark Detection responded: {landmark_response.status}")

            # Send to Service 3 (Age Gender Estimation)
            age_gender_response = self.age_gender_stub.EstimateAgeGender(request)
            logger.info(f"Age Gender Estimation responded: {age_gender_response.status}")

            return image_processing_pb2.CombinedResponse(
                status="Success",
                landmark_response=landmark_response,
                age_gender_response=age_gender_response
            )
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            return image_processing_pb2.CombinedResponse(status=f"Failed: {str(e)}")

def read_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        _, buffer = cv2.imencode('.png', img)
        return buffer.tobytes()
    except Exception as e:
        logger.error(f"Error reading image {image_path}: {str(e)}")
        raise

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def process_images(image_dir, input_stub):
    for filename in os.listdir(image_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_dir, filename)
            try:
                image_data = read_image(image_path)
                request = image_processing_pb2.ImageRequest(image_data=image_data)
                response = input_stub.ProcessImage(request)
                logger.info(f"Processed {filename}: {response.status}")
                logger.info(f"Landmark Detection: {response.landmark_response.status}, Runtime: {response.landmark_response.runtime}")
                logger.info(f"Age Gender Estimation: {response.age_gender_response.status}, Runtime: {response.age_gender_response.runtime}")
            except Exception as e:
                logger.error(f"Failed to process {filename}: {str(e)}")

def serve():
    config = load_config()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_processing_pb2_grpc.add_ImageInputServicer_to_server(
        ImageInputService(config['service2_address'], config['service3_address']), server
    )
    server.add_insecure_port(config['service1_address'])
    server.start()
    logger.info(f"Image Input Service running on {config['service1_address']}...")

    try:
        with grpc.insecure_channel(config['service1_address']) as channel:
            input_stub = image_processing_pb2_grpc.ImageInputStub(channel)
            process_images(config['image_directory'], input_stub)
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")

    server.wait_for_termination()

if __name__ == '__main__':
    serve()