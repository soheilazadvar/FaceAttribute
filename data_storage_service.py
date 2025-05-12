import grpc
import image_processing_pb2
import image_processing_pb2_grpc
from concurrent import futures
import cv2
import numpy as np
import redis
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataStorageService(image_processing_pb2_grpc.DataStorageServicer):
    def __init__(self, redis_client, output_dir):
        self.redis_client = redis_client
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Initialized Data Storage Service with output directory: {self.output_dir}")

    def StoreData(self, request, context):
        try:
            logger.info(f"Storing data for Redis key: {request.redis_key}")
            # Decode image data
            nparr = np.frombuffer(request.image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode image")

            # Save image as JPEG
            image_path = os.path.join(self.output_dir, f"{request.redis_key}.jpg")
            cv2.imwrite(image_path, img)
            services_data = self.redis_client.get(f"{request.redis_key}")
            data = json.loads(services_data) if services_data else {}
            # Save results as JSON in Redis
            result = {
                "redis_key": request.redis_key,
                "image_path": image_path,
                "results" : data
            }
            out_path = os.path.join(self.output_dir, f"{request.redis_key}.json")
            with open(out_path, 'w') as f:
                json.dump(result, f, indent=4)   
            logger.info(f"Saved JSON to file {out_path}")
            return image_processing_pb2.StorageResponse(status="Success")
        
        except Exception as e:
            logger.error(f"Error storing data for {request.redis_key}: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            return image_processing_pb2.StorageResponse(status=f"Failed: {str(e)}")

def serve():
    with open('config.json', 'r') as f:
        config = json.load(f)

    redis_client = redis.Redis(
        host=config['redis_host'],
        port=config['redis_port'],
        decode_responses=True
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_processing_pb2_grpc.add_DataStorageServicer_to_server(
        DataStorageService(redis_client, config['output_directory']), server
    )
    server.add_insecure_port(config['service4_address'])
    server.start()
    logger.info(f"Data Storage Service running on {config['service4_address']}...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()