from rclone_python import rclone
import os
import shutil
from datetime import datetime


def main():

    path = "/tmp/backup"

    shutil.rmtree(path)

    bucket="s3:pelican-staging/media-assets"

    backup_filename = "s3-backup_2025.04.16.09-51-01UTC.backup.zip"

    if(os.path.exists(path)):
        if(not os.listdir(path)):
            shutil.unpack_archive(backup_filename, "/tmp/backup")
            rclone.copy("/tmp/backup", bucket)
            shutil.rmtree(path)
    else:
        os.mkdir(path)
        shutil.unpack_archive(backup_filename, "/tmp/backup")
        rclone.copy("/tmp/backup", bucket)
        shutil.rmtree(path)



if __name__ == '__main__':

    main()