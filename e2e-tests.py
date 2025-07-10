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

    # Checking that S3 backup file contains test file 
    try:
        with zipfile.ZipFile(latest_backup["Key"], 'r') as zip_ref:
            file_names = zip_ref.namelist()

            if "test.txt" in file_names:
                zip_ref.extract("test.txt")
            else:
                raise Exception("Test file not found")
    except:
        raise Exception("Error while reading zip file")

    try:
        with open("test.txt", "r") as test_file:
            test_file_content = test_file.read()
    except:
        raise Exception("Error while reading test file")

    # Checking that test file contains test data
    if not "test" in test_file_content:
        raise Exception("Test file content error. Test data is missing")

    print(file_names)

if __name__ == '__main__':
    main()