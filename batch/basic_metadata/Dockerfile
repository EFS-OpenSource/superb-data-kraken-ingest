# Use of 3.9-alpine causes compilation problems (cryptography and uamqp in requirements.txt).
# On this basis 3.9-slim-buster is chosen.

FROM python:3.9-slim-buster
COPY . /basic_metadata
WORKDIR /basic_metadata
RUN pip install -r requirements.txt
CMD ["python", "main.py"]