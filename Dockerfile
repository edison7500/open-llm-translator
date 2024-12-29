FROM python:3.11.10-slim-bullseye
ENV PYTHONUNBUFFERED 1

COPY ./requirements /tmp/requirements
RUN pip install -U pip
RUN pip install -r /tmp/requirements/base.tx

COPY . /opt/open-llm-transaltor
WORKDIR /opt/open-llm-transaltor

RUN touch .env
# cleanup
RUN pip cache purge

# add user
RUN useradd -s /sbin/nologin -u 1001 -d /opt/open-llm-transaltor transaltor

EXPOSE 8000