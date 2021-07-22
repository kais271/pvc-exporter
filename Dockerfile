FROM python:3.8.7

WORKDIR /usr/src/app

COPY app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app/pvc-exporter.py ./

ENTRYPOINT [ "python", "./pvc-exporter.py" ]
