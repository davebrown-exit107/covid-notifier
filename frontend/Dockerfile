FROM python:3.8
LABEL maintainer="dave.brown@exit107.com"

EXPOSE 5000

COPY ./pyproject.toml ./
COPY ./poetry.lock ./

RUN apt-get install libpq-dev

RUN pip install poetry
RUN poetry install

COPY . .

# Prevent bytecode files from being written out
ENV PYTHONDONTWRITEBYTECODE 1

# Don't buffer STDOUT or STDERR
ENV PYTHONUNBUFFERED 1

ENV FLASK_APP covid_notifier.app:notifier_app

RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
