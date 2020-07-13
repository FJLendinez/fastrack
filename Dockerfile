FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt
CMD gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app