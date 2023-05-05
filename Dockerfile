FROM docker.io/bitnami/pytorch:latest
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python","./mqtts.py"]