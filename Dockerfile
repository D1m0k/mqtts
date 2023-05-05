FROM docker.io/bitnami/pytorch:latest
RUN pip install -r requirements.txt
WORKDIR /app
COPY . .
CMD ["./mqtt_tts.py"]