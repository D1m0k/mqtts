FROM python:3.8-bullseye
WORKDIR /app
RUN mkdir sounds
COPY . .
RUN pip install -r requirements.txt
CMD ["python","./mqtts.py"]