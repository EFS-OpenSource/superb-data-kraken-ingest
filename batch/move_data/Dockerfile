FROM python:3.9-slim-buster
COPY . /move_data
WORKDIR /move_data
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]