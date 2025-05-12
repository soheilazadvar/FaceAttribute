import grpc
import image_processing_pb2
import image_processing_pb2_grpc
from concurrent import futures
import redis
import hashlib
import random
import time
import logging
import json
import cv2
# import insightface
from insightface.app import FaceAnalysis
import numpy as np



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgeGenderEstimationService(image_processing_pb2_grpc.AgeGenderEstimationServicer):
    def __init__(self, redis_client, storage_address):
        self.redis_client = redis_client
        self.storage_channel = grpc.insecure_channel(storage_address)
        self.storage_stub = image_processing_pb2_grpc.DataStorageStub(self.storage_channel)
        logger.info("Initialized Age Gender Estimation Service with Redis and Data Storage stub")

    def AgeGender(self , image_data):
        print('in agegender')
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Initialize FaceAnalysis with buffalo_l model (includes age and gender)
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))        

        # Detect faces and predict age/gender
        faces = app.get(img)
        # print(faces)
        results ={'age':[] , 'gender':[]}
        for face in faces:
            bbox = face.bbox.astype(int)
            # print(bbox)
            gender = 'Male' if face.gender == 1 else 'Female'
            age = face.age
            results['age'].append(age)
            results['gender'].append(gender)
            # print(f"Gender: {gender}, Age: {age}")
        return results

    def EstimateAgeGender(self, request, context):
        start_time = time.time()
        results_json = self.AgeGender(request.image_data)
        try:
            # Calculate hash (Redis key) from image data
            redis_key = hashlib.sha256(request.image_data).hexdigest()
            logger.info(f"Processing image with Redis key: {redis_key}")

            # Check if Service 2 output exists in Redis
            service2_data = self.redis_client.get(f"{redis_key}")
            data = json.loads(service2_data) if service2_data else {}
            name = redis_key  # Default to redis_key as name

            # Save to Redis
            data['agegender_service'] = results_json
            self.redis_client.set(redis_key, json.dumps(data))
            logger.info(f"Saved age and gender to Redis for key: {redis_key}")

            if 'landmark_service' in data:
                logger.info("Face Landmark found in Redis")

                # Send to Service 4
                storage_request = image_processing_pb2.StorageRequest(
                    image_data=request.image_data,
                    redis_key=redis_key
                )
                storage_response = self.storage_stub.StoreData(storage_request)
                logger.info(f"Data Storage responded: {storage_response.status}")
            else:
                logger.info("Face Landmark not found in Redis")

            return image_processing_pb2.AgeGenderResponse(
                status="Success",
                runtime=time.time() - start_time,
                redis_key=redis_key
            )
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            return image_processing_pb2.AgeGenderResponse(status=f"Failed: {str(e)}")

def serve():
    with open('config.json', 'r') as f:
        config = json.load(f)

    redis_client = redis.Redis(
        host=config['redis_host'],
        port=config['redis_port'],
        decode_responses=True
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_processing_pb2_grpc.add_AgeGenderEstimationServicer_to_server(
        AgeGenderEstimationService(redis_client, config['service4_address']), server
    )
    server.add_insecure_port(config['service3_address'])
    server.start()
    logger.info(f"Age Gender Estimation Service running on {config['service3_address']}...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()