FROM python:3.9.0-slim-buster

WORKDIR /app
ADD requirements.txt ./

RUN pip install -r requirements.txt

ADD *.py ./

ENTRYPOINT ["/bin/bash"]

