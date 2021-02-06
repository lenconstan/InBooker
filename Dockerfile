FROM python:3.7-alpine

WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0




RUN apk add --no-cache && apk add postgresql-dev gcc python3-dev musl-dev\
    build-base cairo-dev cairo cairo-tools \
    # pillow dependencies
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

RUN pip3 install "flask==1.0.1" "CairoSVG==2.1.3"

RUN python3 -m venv /opt/venv
COPY requirements.txt requirements.txt
RUN pip3 install wheel

RUN pip3 install -r requirements.txt


EXPOSE 5000
COPY . .
CMD ["flask", "run"]
