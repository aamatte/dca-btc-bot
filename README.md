# DCA Bitcoin Bot

Simple bot that buys bitcoin in [Buda.com](https://www.buda.com/chile) following the Dollar Cost Averaging (DCA) strategy.

## Getting Started

To get the bot working, first, you need to clone the repo.

```
git clone https://github.com/aamatte/dca-btc-bot.git
```

Create a `secrets.yml` file.

```
credentials:
  Buda:
    key: YOUR-KEY-HERE
    secret: YOUR-SECRET-HERE

```

Adjust your settings in `settings.yml`. You have to edit:

```
...

investment:
  # Every how many hours the bot tries to buy
  interval_hours: 2 # Every 2 hours

  # Monthly investment
  monthly: 10000 # 10,000 CLP every month

  # Max overprice
  overprice_limit: 0.03 # 3% max overprice

...
```

Finally, if you want to run the bot.

```
pipenv install
pipenv shell
python bots.py run buda
```

### Prerequisites

You need to have installed `python3.6` and `pipenv`.

## Deployment

You can run the bot every 2-5 minutes with a cron job.

## Built With

* [trading-bots](https://github.com/budacom/trading-bots)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on the code of conduct, and the process for submitting pull requests.

## License

[MIT](https://opensource.org/licenses/MIT)