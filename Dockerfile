FROM python:3.9-alpine

WORKDIR /app
COPY s3-backup.py .
COPY .rclone-test.conf .

RUN apk --update add \
    python3 \
    py3-pip \
    curl \
    && pip3 install --upgrade pip \
    && pip3 install awscli \
    && pip3 install python-rclone

CMD ["python", "s3-backup.py"]
