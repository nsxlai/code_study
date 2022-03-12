# first stage
FROM python:3.9 AS builder
COPY requirements.txt .

# install dependencies to the local user directory (e.g., /root/.local)
RUN pip install --user -r requirements.txt

# second unamed stage
FROM python:3.8-slim
WORKDIR /code

# copy only the dependencies that are needed  for our application and the source files
COPY --from=builder . /root/.local
COPY ./src .

# update PATH
ENV PATH=/root/.local:$PATH
# ENV PYTHONPATH=/src

# make sure you include the -u flag to have our stdout logged
CMD ["python", "-u", "./main.py"]

# To build the image:
# sudo docker build -t directory-monitor
#
# To run the image:
# sudo docker run -d --restart=always -e DIRECTORY='/tmp/test' -v /tmp/:/tmp/ directory-monitor
#
# To check the docker image running:
# sudo docker ps