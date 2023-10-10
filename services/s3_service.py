import boto3
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = 'synnote-record-bucket'


s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def download_file_from_s3(filename: str):
    with open(filename, 'wb') as f:
        s3.download_fileobj(BUCKET_NAME, filename, f)

def delete_file_from_s3(filename: str):
    s3.delete_object(Bucket=BUCKET_NAME, Key=filename)

def upload_file_to_s3(filename: str):
    with open(filename, "rb") as f:
        s3.upload_fileobj(f, BUCKET_NAME, os.path.basename(filename))

def get_s3_object_url(filepath: str) -> str:
    return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filepath}"