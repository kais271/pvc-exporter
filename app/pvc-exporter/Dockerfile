FROM python:3.9.12-alpine
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY pvc-exporter.py ./
ENV PYTHONUNBUFFERED=1
CMD [ "python", "./pvc-exporter.py" ]
