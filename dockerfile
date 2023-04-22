FROM ubuntu:latest
RUN apt update
RUN apt install python3 -y

WORKDIR /app
COPY requirements.txt requirements.txt
COPY . .

RUN python3 -m pip install -r requirements.txt

CMD [ "uvicorn", "main:app", "--reload"]