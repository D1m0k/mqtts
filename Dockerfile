FROM docker.io/bitnami/pytorch:latest
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN ["chmod", "+x", "mqtts.py"]
CMD ["./mqtts.py"]