FROM python:3.9.9-alpine
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY pod-pvc-mapping.py ./
ENV PYTHONUNBUFFERED=1
CMD [ "python", "./pod-pvc-mapping.py" ]
