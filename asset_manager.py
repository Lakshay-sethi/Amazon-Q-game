import boto3
import os
from botocore.exceptions import ClientError

class AssetManager:
    def __init__(self):
        self.s3 = boto3.client('s3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket_name = os.environ.get('S3_BUCKET_NAME')
        
    def upload_asset(self, file_path, s3_path):
        try:
            self.s3.upload_file(file_path, self.bucket_name, s3_path)
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False
            
    def download_asset(self, s3_path, local_path):
        try:
            self.s3.download_file(self.bucket_name, s3_path, local_path)
            return True
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return False