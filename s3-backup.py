import boto3
import os
import shutil
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]: %(message)s",
    datefmt="%Y-%m-%dT%H-%M-%S",
)

def main():
    temp_directory_for_files_from_source = "/tmp/backup"
    bucket_subfolder_name = os.getenv('SOURCE_S3_AWS_BUCKET_SUBFOLDER_NAME')

    archive_name = os.getenv('S3_BACKUPS_FILENAME_PREFIX') + '-' + datetime.strftime(datetime.utcnow(), "%Y-%m-%dT%H-%M-%S") + '.backup'
    
    source_s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('SOURCE_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SOURCE_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('SOURCE_S3_AWS_ENDPOINT'),
    )
    
    destination_s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('DESTINATION_S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('DESTINATION_S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('DESTINATION_S3_AWS_ENDPOINT'),
    )

    source_bucket_name = os.getenv('SOURCE_S3_AWS_BUCKET_NAME')
    destination_bucket_name = os.getenv('DESTINATION_S3_AWS_BUCKET_NAME')

    if not os.path.exists(temp_directory_for_files_from_source):
        os.mkdir(temp_directory_for_files_from_source)

    download_dir(temp_directory_for_files_from_source, source_bucket_name, source_s3, bucket_subfolder_name)

    if not len(os.listdir(temp_directory_for_files_from_source)) == 0:
        shutil.make_archive(archive_name, 'zip', temp_directory_for_files_from_source + "/" + bucket_subfolder_name)

        upload_to_s3(archive_name + ".zip", destination_s3, destination_bucket_name)

    else:
        logging.info(f"Bucket {source_bucket_name} is empty. Backup will not be created.")
    

# Reference: https://stackoverflow.com/a/56267603
def download_dir(local, bucket, client, bucket_subfolder_name):
    """
    params:
    - local: local path to folder in which to place files
    - bucket: s3 bucket with target contents
    - bucket_subfolder_name: s3 bucket subfolder (if exists)
    - client: initialized s3 client object
    """
    keys = []

    base_kwargs = {
        'Bucket': bucket,
        'Prefix': bucket_subfolder_name
    }

    kwargs = base_kwargs.copy()
    paginator = client.get_paginator('list_objects_v2')

    for page in paginator.paginate(**kwargs):
        contents = page.get('Contents')
        for obj in contents:
            key = obj.get('Key')
            if not key.endswith('/'):
                keys.append(key)

    for key in keys:
        dest_pathname = os.path.join(local, key)      
        os.makedirs(os.path.dirname(dest_pathname), exist_ok=True)

        logging.info(f'Downloading {key}')
        client.download_file(bucket, key, dest_pathname)
        if not os.path.exists(dest_pathname):
            logging.info(f'File not found after download: {dest_pathname}')
            raise
        logging.info(f'Downloaded {key}')

    logging.info(f'Successfully downloaded {len(keys)} files')
    

def upload_to_s3(path, s3, bucket):
    logging.info(f'Uploading {path}')

    try:
        with open(path, "rb") as data:
            s3.upload_fileobj(data, bucket, path)

        logging.info(f'Backup is successfully uploaded {path}')

    except Exception as e:
        logging.info(f'Failed to upload {path}: {e}')
        raise

    
if __name__ == '__main__':

    main()