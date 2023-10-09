# Use of 3.9-alpine causes compilation problems (cryptography and uamqp in requirements.txt).
# On this basis 3.9-slim-buster is chosen.

FROM python:3.9-slim-buster
COPY . /skip_validation
WORKDIR /skip_validation
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]