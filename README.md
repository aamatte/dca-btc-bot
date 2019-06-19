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

apis:
  currencyconverter_key: YOUR currencyconverterapi.com API KEY
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

That will run the bot in `dry_run` mode (it won't place any order). Once you are sure everything is correct, in `settings.yml` set:

```
dry_run: False
```

### Prerequisites

You need to have installed `python3.6` and `pipenv`.

## Deployment

You can run the bot every 2-5 minutes with a cron job.

```
crontab -e
```

At the end of the file put something like this:

```
*/2 * * * * cd ~/dca-btc-bot && /usr/local/bin/pipenv run ~/dca-btc-bot/bots.py run buda >> ~/dca-btc-bot/log.log 2>&1
```

That will run the bot every 2 minutes.

## Built With

* [trading-bots](https://github.com/budacom/trading-bots)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on the code of conduct, and the process for submitting pull requests.

## License

[MIT](https://opensource.org/licenses/MIT)