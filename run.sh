#!/bin/bash
# Function to wait for a port to be open
wait_for_port() {
  local host=$1
  local port=$2

  echo "Waiting for $host:$port to be available..."
  while ! nc -z $host $port; do
    sleep 1
  done
  echo "$host:$port is now open."
}

# Start gnome-terminal with Service 4 in the first tab
gnome-terminal --tab --title="Storage" -- bash -c "python3 data_storage_service.py; echo 'data_storage_service stopped. Press Enter to close.'; read"

# Wait for Service 4 to start
wait_for_port 127.0.0.1 50054
# Add Service 2 in a new tab
gnome-terminal --tab --title="Landmark" -- bash -c "python3 face_landmark_detection_service.py; echo 'face_landmark_detection_service stopped. Press Enter to close.'; read"

# Wait for Service 2 to start
wait_for_port 127.0.0.1 50054
# Add Service 3 in a new tab
gnome-terminal --tab --title="Age_Gender" -- bash -c "python3 age_gender_estimation_service.py; echo 'age_gender_estimation_service stopped. Press Enter to close.'; read"

# Wait for Service 3 and 2 to start

wait_for_port 127.0.0.1 50053
wait_for_port 127.0.0.1 50052
# Add Service 1 in a new tab
gnome-terminal --tab --title="Image" -- bash -c "python3 image_input_service.py; echo 'image_input_service stopped. Press Enter to close.'; read"


echo "All services started in separate tabs in a single gnome-terminal window."