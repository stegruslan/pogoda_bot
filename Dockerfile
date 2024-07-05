FROM python:3.12-slim-bullseye

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt

COPY ./main.py ./main.py

RUN pip install -r requirements.txt

COPY . .

CMD python main.py