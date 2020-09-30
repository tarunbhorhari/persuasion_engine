From python:3.7-slim

ARG CODE_PATH=/usr/local/src/persuasion_engine/
RUN mkdir -p $CODE_PATH
WORKDIR $CODE_PATH

copy . $CODE_PATH
RUN pip3 install -r requirements.txt