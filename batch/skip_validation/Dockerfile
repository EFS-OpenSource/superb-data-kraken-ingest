FROM python:3.9-slim-buster
COPY . /skip_validation
WORKDIR /skip_validation
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]