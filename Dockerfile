FROM python:3.8-bullseye
RUN mkdir sounds
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python","./mqtts.py"]