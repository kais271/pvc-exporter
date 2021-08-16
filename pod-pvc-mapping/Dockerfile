FROM python:3.9.6-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY pod-pvc-mapping.py ./

CMD [ "python", "./pod-pvc-mapping.py" ]
