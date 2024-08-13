#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

import os
import boto3
import subprocess
import json

config = {
    "AWS_ACCESS_KEY_ID": "your-access-key-id",
    "AWS_SECRET_ACCESS_KEY": "your-secret-access-key",
    "STAGE_1_BUCKET": "your-stage-bucket",
}

session = boto3.Session(
    region_name="us-east-1",
    aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"]
)
s3 = session.client("s3")
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    bucket_id_input = event['Records'][0]['s3']['bucket']['name']
    video_file_obj = event['Records'][0]['s3']['object']['key']
    video_file_name = '/tmp/' + os.path.basename(video_file_obj)

    s3.download_file(bucket_id_input, video_file_obj, video_file_name)
    local_out_file = video_splitting_cmdline(video_file_name)

    s3.upload_file('/tmp/' + local_out_file, config["STAGE_1_BUCKET"], local_out_file)
    subprocess.run(['rm', '-rf', local_out_file])

    invoke_face_recognition(local_out_file)

def video_splitting_cmdline(video_filename):
    filename = os.path.basename(video_filename)
    outfile = os.path.splitext(filename)[0] + ".jpg"

    split_cmd = 'ffmpeg -i ' + video_filename + ' -vframes 1 ' + '/tmp/' + outfile
    try:
        subprocess.check_call(split_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)

    fps_cmd = 'ffmpeg -i ' + video_filename + ' 2>&1 | sed -n "s/.*, \\(.*\\) fp.*/\\1/p"'
    fps = subprocess.check_output(fps_cmd, shell=True).decode("utf-8").rstrip("\n")
    return outfile

def invoke_face_recognition(image_file_name):
    payload = {'Records': [{'s3': {'bucket': {'name': config["STAGE_1_BUCKET"]}, 'object': {'key': image_file_name}}}]}
    
    response = lambda_client.invoke(
        FunctionName='face-recognition',
        InvocationType='Event',
        Payload=json.dumps(payload)
    )

    if response['StatusCode'] != 202:
        print("Failed to invoke face recognition function.")