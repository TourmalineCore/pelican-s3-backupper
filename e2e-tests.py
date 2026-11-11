import boto3
import os
import zipfile

def main():
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('S3_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('S3_AWS_SECRET_ACCESS_KEY'),
        endpoint_url=os.getenv('S3_AWS_ENDPOINT')
    )

    objects_list = s3.list_objects_v2(Bucket=os.getenv('S3_AWS_BUCKET_NAME'))

    # Checking that bucket isn't empty
    try:
        contents = objects_list["Contents"]

    except:
        raise Exception("Bucket is empty")

    backups = []

    for content in contents:
        if content["Key"].startswith(os.getenv('S3_BACKUPS_FILENAME_PREFIX')):
            backups.append(content)
    
    # Checking that S3 backups exists in bucket
    if len(backups) == 0:
        raise Exception("No S3 backups found")
    
    latest_backup = backups[-1]

    # Checking that S3 backup file size isn't zero 
    if latest_backup["Size"] == 0:
        raise Exception("Backup size is 0")

    s3.download_file(Bucket=os.getenv('S3_AWS_BUCKET_NAME'), Key=latest_backup['Key'], Filename=latest_backup['Key'])
    file_names = []

    # Checking that S3 backup file contains test files and their count is 1001
    try:
        with zipfile.ZipFile(latest_backup["Key"], 'r') as zip_ref:
            file_names = zip_ref.namelist()
            
            if not len(file_names) == 1001:
                raise Exception("Backup archive doesn't contain all 1001 test files")

            for i in range(1,1002):
                if f"file_{i}.txt" in file_names:
                    zip_ref.extract(f"file_{i}.txt", "/tmp/s3-backupper/extracted-from-archive")
                else:
                    raise Exception(f"Test file 'file_{i}.txt' not found")
    except:
        raise Exception("Error while reading zip file")

    try:
        for i in range(1,1002):
            with open(f"/tmp/s3-backupper/extracted-from-archive/file_{i}.txt", "r") as test_file:
                test_file_content = test_file.read()
                
                # Checking that test file contains test data
                if not "test" in test_file_content:
                    raise Exception(f"Test file 'file_{i}.txt' content error. Test data is missing")
    except:
        raise Exception("Error while reading test file")




if __name__ == '__main__':
    main()