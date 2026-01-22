FROM ubuntu:latest

RUN apt-get update && apt-get install -y git python3-pip python3-venv
RUN ls
RUN pwd
# create new folder named app
RUN mkdir app

# copy all files from current directory to app folder
COPY . /app

# set working directory to app
WORKDIR /app

RUN pip3 install --break-system-packages -r requirements.txt
CMD ["python3", "main.py"]