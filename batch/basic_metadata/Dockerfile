FROM python:3.9-slim-buster
COPY . /basic_metadata
WORKDIR /basic_metadata
RUN pip install -r requirements.txt
CMD ["python", "main.py"]