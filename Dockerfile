FROM python:3.8

COPY . /app

WORKDIR /app

RUN pip install pipenv && pipenv sync

CMD pipenv run python /app/src/trier-bot.py -f /config.ini