import rclone
import os
import shutil
from datetime import datetime


def main():

    cfg_path = r'.rclone-test.conf'
    directory_path = "/tmp/s3-backup"

    os.mkdir(directory_path)

    with open(cfg_path) as f:
        cfg = f.read()

    archive_name = "s3-backup" + '_' + datetime.strftime(datetime.utcnow(), "%Y.%m.%d.%H-%M-%S") + 'UTC' + '.backup'
    
    # s3-1:pelican-local-env is source
    rclone.with_config(cfg).copy("s3-1:pelican-local-env", directory_path, flags=["--transfers=256"])

    print(os.listdir(directory_path))

    shutil.make_archive(archive_name, 'zip', directory_path)

    # s3-2:backup is destination
    rclone.with_config(cfg).copy(archive_name + ".zip", "s3-2:backup", flags=["--transfers=256"])


if __name__ == '__main__':

    main()