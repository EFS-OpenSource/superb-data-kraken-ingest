FROM python:3.9-slim-buster
COPY . /metadata_index
WORKDIR /metadata_index
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]