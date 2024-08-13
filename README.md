# Face Recognition System with Video Processing

## Overview

The project demonstrates a face recognition system integrated with AWS Lambda and Docker. The system processes videos to extract frames, performs face recognition, and uploads the results to S3. The project includes Docker configurations for creating a containerized environment and AWS Lambda functions for handling video and image processing.

## Project Structure

- **`face-recognition-docker/`**: Contains Docker-related files for setting up the face recognition environment.
  - **`Dockerfile`**: Defines the Docker image used for the face recognition Lambda function.
  - **`entry.sh`**: Script to manage Lambda runtime execution.
  - **`handler.py`**: Main handler script for processing images and performing face recognition.
  - **`requirements.txt`**: Contains the required Python packages (currently empty).

- **`video-splitting/`**: Contains Lambda function for video processing.
  - **`lambda_function.py`**: Script to split videos into frames and invoke the face recognition function.

## Setup and Deployment

### Prerequisites

- Docker
- AWS CLI
- AWS Lambda account
- AWS S3 buckets for storing video and image data

### Docker Setup

1. **Build Docker Image**

   Navigate to the `face-recognition-docker` directory and build the Docker image:

   ```
   docker build -t face-recognition-image .
   ```
2. **Push Docker Image to AWS ECR**

  Tag and push the Docker image to Amazon Elastic Container Registry (ECR):
  ```
  docker tag face-recognition-image:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/face-recognition-image:latest
  docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/face-recognition-image:latest
  ```

### AWS Lambda Setup
1. **Create Lambda Functions**
  - Face Recognition Function: Use the Docker image pushed to ECR for creating a Lambda function.
  - Video Splitting Function: Deploy the lambda_function.py as another Lambda function.

2. **Configure S3 Triggers**
  - Set up S3 event triggers to invoke the video splitting function when a video is uploaded, and configure the splitting function to invoke the face recognition function.

### Local Development
1. **Install Dependencies**
  If running locally, ensure the following Python packages are installed:
  ```pip install boto3 torch torchvision facenet-pytorch opencv-python```
2. **Run the Handler Locally**
  Test the handler.py script locally by providing the necessary environment variables and input.

### Usage
1. **Upload Video to S3**
  - Upload a video file to the S3 bucket configured for video processing.
2. **Processing**
  - The video splitting Lambda function will automatically split the video into frames and upload them to S3. The face recognition Lambda function will then process these frames, perform face recognition, and upload results to the specified output S3 bucket.

### Additional Information
  - Ensure that your AWS Lambda functions have the necessary permissions to access S3 buckets.
  - For Docker and AWS CLI commands, replace placeholders with your actual AWS account details and region.
