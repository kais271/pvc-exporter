FROM python:3.9.6-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY scanner.py ./

CMD [ "python", "./scanner.py" ]
