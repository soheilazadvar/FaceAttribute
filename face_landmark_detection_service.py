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
from insightface.app import FaceAnalysis
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FaceLandmarkDetectionService(image_processing_pb2_grpc.FaceLandmarkDetectionServicer):
    def __init__(self, redis_client, storage_address):
        self.redis_client = redis_client
        self.storage_channel = grpc.insecure_channel(storage_address)
        self.storage_stub = image_processing_pb2_grpc.DataStorageStub(self.storage_channel)
        logger.info("Initialized Face Landmark Detection Service with Redis and Data Storage stub")
    
    def Landmark(self , image_data):
        print('in landmark')
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))        

        # Detect faces and predict age/gender
        faces = app.get(img)
        results ={'landmarks':[]}
        for face in faces:
            bbox = face.bbox
            results['landmarks'].append(list(bbox))
        results = {'landmarks': [[int(x) for x in pair] for pair in results['landmarks']]}
        return results
    
    def DetectLandmarks(self, request, context):
        start_time = time.time()
        results_json = self.Landmark(request.image_data)
        print(results_json)
        try:
            # Calculate hash (Redis key) from image data
            redis_key = hashlib.sha256(request.image_data).hexdigest()
            logger.info(f"Processing image with Redis key: {redis_key}")

            # Check if Service 3 output exists in Redis
            service3_data = self.redis_client.get(f"{redis_key}")
            data = json.loads(service3_data) if service3_data else {}
            name = redis_key  # Default to redis_key as name

            # Save to Redis
            data['landmark_service']  = results_json
            self.redis_client.set(redis_key, json.dumps(data))
            logger.info(f"Saved landmarks to Redis for key: {redis_key}")

            if 'agegender_service' in data:
                logger.info("Age Gender found in Redis")

                # Send to Service 4
                storage_request = image_processing_pb2.StorageRequest(
                    image_data=request.image_data,
                    redis_key=redis_key
                )
                storage_response = self.storage_stub.StoreData(storage_request)
                logger.info(f"Data Storage responded: {storage_response.status}")
            else:
                logger.info("Age Gender not found in Redis")
            return image_processing_pb2.LandmarkResponse(
                status="Success",
                runtime=time.time() - start_time,
                redis_key=redis_key
            )
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            return image_processing_pb2.LandmarkResponse(status=f"Failed: {str(e)}")

def serve():
    with open('config.json', 'r') as f:
        config = json.load(f)

    redis_client = redis.Redis(
        host=config['redis_host'],
        port=config['redis_port'],
        decode_responses=True
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_processing_pb2_grpc.add_FaceLandmarkDetectionServicer_to_server(
        FaceLandmarkDetectionService(redis_client, config['service4_address']), server
    )
    server.add_insecure_port(config['service2_address'])
    server.start()
    logger.info(f"Face Landmark Detection Service running on {config['service2_address']}...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()