#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

import os
import boto3
import subprocess
import cv2
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

config = {
    "AWS_ACCESS_KEY_ID": "your-access-key-id",
    "AWS_SECRET_ACCESS_KEY": "your-secret-access-key",
    "DATA_BUCKET": "your-data-bucket",
    "OUTPUT_BUCKET": "your-output-bucket",
}

session = boto3.Session(
    region_name="us-east-1",
    aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"]
)
s3 = session.client("s3")
lambda_client = boto3.client('lambda')

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def handler(event, context):
    bucket_id_input = event['Records'][0]['s3']['bucket']['name']
    video_file_obj = event['Records'][0]['s3']['object']['key']
    video_file_name = '/tmp/' + os.path.basename(video_file_obj)
    try:
        s3.download_file(bucket_id_input, video_file_obj, video_file_name)
    except Exception as e:
        print(f"Error downloading image from S3: {e}")
        return

    output_face_recognition = face_recognition_function(video_file_name)
    s3.upload_file('/tmp/' + output_face_recognition + ".txt", config["OUTPUT_BUCKET"], output_face_recognition + ".txt")
    subprocess.run(['rm', '-rf', output_face_recognition])
    return

def face_recognition_function(key_path):
    # Face extraction
    img = cv2.imread(key_path, cv2.IMREAD_COLOR)
    boxes, _ = mtcnn.detect(img)

    # Face recognition
    key = os.path.splitext(os.path.basename(key_path))[0].split(".")[0]
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    face, prob = mtcnn(img, return_prob=True, save_path=None)

    try:
        s3.download_file(config["DATA_BUCKET"], 'data.pt', '/tmp/data.pt')
    except Exception as e:
        print(f"Error downloading image from S3: {e}")
        return

    saved_data = torch.load('/tmp/data.pt')  # loading data.pt file
    if face != None:
        emb = resnet(face.unsqueeze(0)).detach()  # detech is to make required gradient false
        embedding_list = saved_data[0]  # getting embedding data
        name_list = saved_data[1]  # getting list of names
        dist_list = []  # list of matched distances, minimum distance is used to identify the person
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
        idx_min = dist_list.index(min(dist_list))

        # Save the result name in a file
        with open("/tmp/" + key + ".txt", 'w+') as f:
            f.write(name_list[idx_min])
        return key
    else:
        print(f"No face is detected")
    return