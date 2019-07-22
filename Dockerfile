FROM python:3.7

WORKDIR /usr/src/app/dca-btc-bot

COPY Pipfile* ./

RUN pip install pipenv
RUN pipenv install

COPY bots.py .
COPY ./buda ./buda
COPY *.yml ./
COPY run.sh .

ENV PIPENV_DONT_LOAD_ENV 1

CMD ["./run.sh"]
