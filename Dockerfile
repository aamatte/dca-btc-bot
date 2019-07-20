FROM python:3.6

WORKDIR /usr/src/app/dca-btc-bot

RUN git clone https://github.com/aamatte/dca-btc-bot.git .

RUN pip install pipenv
RUN pipenv install

COPY settings.yml .
COPY secrets.yml .

CMD [ "pipenv", "run", "./bots.py", "loop", "buda", "--interval", "5"]
