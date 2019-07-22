# DCA Bitcoin Bot

Simple bot that buys bitcoin in [Buda.com](https://www.buda.com/chile) following the Dollar Cost Averaging (DCA) strategy.

## Getting Started

To get the bot working, first, you need to clone this repo.

```
git clone https://github.com/aamatte/dca-btc-bot.git
```

Edit the `.env` file with desired configuration. For example

```
# BUDA API
BUDA_KEY=MyBudaKey
BUDA_SECRET=MyBudaSecret

# CURRENCYCONVERTER API
CURRENCYCONVERTER_KEY=MyCurrencyConverterKey

# BOT SETTINGS
INVESTMENT_INTERVAL_HOURS=2
INVESTMENT_MONTHLY_AMOUNT=50000
INVESTMENT_OVERPRICE_LIMIT=0.03

```

Then you can install dependencies and run the bot:

```
pipenv install
pipenv shell
./run.sh
```

Or run it inside a docker container

```
docker-compose up -d
```


### Prerequisites

You need to have installed `python3.7` and `pipenv`. Or `docker`.

## Deployment

Using the docker container and configuring it via env vars is the recommended way to run this.

## Built With

* [trading-bots](https://github.com/budacom/trading-bots)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on the code of conduct, and the process for submitting pull requests.

## License

[MIT](https://opensource.org/licenses/MIT)