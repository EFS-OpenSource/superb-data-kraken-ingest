# Use of 3.9-alpine causes compilation problems (cryptography and uamqp in requirements.txt).
# On this basis 3.9-slim-buster is chosen.

FROM python:3.9-slim-buster
COPY . /metadata_index
WORKDIR /metadata_index
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]