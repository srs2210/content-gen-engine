"""
 Copyright 2024 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

import datetime
from google.cloud import storage
from google.cloud.storage.bucket import STANDARD_STORAGE_CLASS
from utils.constants import PROJECT_ID, SERVICE_ACCOUNT_FOR_SIGNING_URLS
from google.auth import impersonated_credentials


class CloudStorageService:
    def __init__(self):
        self.client = storage.Client(project=PROJECT_ID)

    def download_blob(self, bucket, file):
        bucket = self.client.get_bucket(self.bucket)
        blob = bucket.blob(file)
        data = blob.download_as_string(client=None)
        return data

    def download_blob_as_bytes(self, bucket, file):
        bucket = self.client.get_bucket(bucket)
        blob = bucket.blob(file)
        data = blob.download_as_bytes(client=None)
        return data

    def create_bucket(self):
        bucket = self.client.bucket(self.bucket)
        bucket.storage_class = STANDARD_STORAGE_CLASS

        buckets = self.client.list_buckets()
        bucket_list = [b.name for b in buckets]
        if self.bucket in bucket_list:
            print("bucket exists")
            return self.bucket
        else:
            new_bucket = self.client.create_bucket(bucket, location="us")
            print("bucket created")
            return new_bucket

    def upload_image_from_string(self, source, destination_blob_name):
        bucket = self.client.bucket(self.bucket)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(source, content_type="image/jpeg")
        print("uploaded")

    def upload_blob_from_file(self, source, destination_blob_name):
        try:
            bucket = self.client.bucket(self.bucket)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(source)
            if source.split("/")[-1] in self.list_bucket_blobs():
                print("uploaded")
            else:
                raise RuntimeError("Unable to find file in bucket")
        except Exception as e:
            raise e

    def list_bucket_blobs(self):
        bucket = self.client.bucket(self.bucket)
        blobs = bucket.list_blobs()
        blob_list = [b.name for b in blobs]
        return blob_list
    
    def generate_signed_url(self, gs_url):
        """Generates a signed URL for downloading a blob from a gs:// URL."""
        # Extract bucket name and blob name from the gs:// URL
        if not gs_url.startswith("gs://"):
            raise ValueError("Invalid gs:// URL")
        
        path_parts = gs_url[5:].split("/", 1)  # Remove 'gs://' and split
        bucket_name = path_parts[0]
        blob_name = path_parts[1] if len(path_parts) > 1 else ""

        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="GET",
        )

        print("Generated GET signed URL:")
        print(url)
        return url
    
    def generate_signed_url_with_impersonation(self, gs_url, target_service_account_email=SERVICE_ACCOUNT_FOR_SIGNING_URLS):
        """Generates a signed URL for downloading a blob from a gs:// URL using impersonation."""
        # Extract bucket name and blob name from the gs:// URL
        if not gs_url.startswith("gs://"):
            raise ValueError("Invalid gs:// URL")
        
        path_parts = gs_url[5:].split("/", 1)  # Remove 'gs://' and split
        bucket_name = path_parts[0]
        blob_name = path_parts[1] if len(path_parts) > 1 else ""

        # Create a credentials object that impersonates the target service account
        target_credentials = impersonated_credentials.Credentials(
            source_credentials=self.client._credentials,  # Your current credentials
            target_principal=target_service_account_email,
            target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Create a storage client with the impersonated credentials
        storage_client = storage.Client(credentials=target_credentials)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="GET",
        )

        print(f"Generated GET signed URL for {blob_name}")
        return url


cs_service = CloudStorageService()
