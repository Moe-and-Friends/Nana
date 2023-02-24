FROM python:3.8-slim

# Basic setup
LABEL maintainer="Kyrielight"
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt && rm /opt/requirements.txt

COPY src /opt/nana/
ENTRYPOINT ["python3", "/opt/nana/main.py"]