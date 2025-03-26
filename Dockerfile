FROM python:3.9-alpine

WORKDIR /app
COPY s3-backup.py .
COPY .rclone.conf .

RUN apk --update add \
    python3 \
    py3-pip \
    curl \
    && pip3 install --upgrade pip \
    && pip3 install awscli \
    && pip3 install python-rclone

RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip rclone-current-linux-amd64.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && chmod +x /usr/bin/rclone \
    && cd .. \
    && rm -rf rclone-*

CMD ["python", "s3-backup.py"]
