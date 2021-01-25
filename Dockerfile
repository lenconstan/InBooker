FROM python:3.7-alpine

WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0


RUN apk add --no-cache gcc musl-dev linux-headers

RUN python3 -m venv /opt/venv
COPY requirements.txt requirements.txt
RUN pip3 install wheel
RUN . /opt/venv/bin/activate && pip install -r requirements.txt


EXPOSE 5000
COPY . .
CMD ["flask", "run"]
