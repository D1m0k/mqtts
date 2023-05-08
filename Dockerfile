FROM ghcr.io/d1m0k/pytorch_centos:main
RUN mkdir sounds
WORKDIR /app
COPY . .
CMD ["python3","./mqtts.py"]