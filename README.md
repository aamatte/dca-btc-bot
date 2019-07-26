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
    key: 'do not share your keys'
    secret: 'do not share your keys'
  Currencyconverter:
    key: 'do not share your keys'
  OpenExchangeRates:
    app_id: 'do not share your keys'
```

Adjust your settings in `settings.yml`. You have to edit:

```
...

investment:
  market: 'BTCCLP'  # Market this bot will be buying at buda.com
  ref_exchange: 'Bitstamp'  # Exchange used for reference price
  ref_market: 'BTCUSD' # Market used at reference exchange for price
  interval_hours: 2  # Hour interval when the bot tries to buy
  monthly_amount: 300000  # Monthly investment in quote amount
  overprice_limit: 0.03  # Max overprice allowed in percentage where 0.03 means 3%
currency_converter: 'OpenExchangeRates'  # Name of currency converter to use
withdrawal:
  enabled: False  # Enable or disable feature, boolean
  address: '1soveryfakeaddressreplacemepleace'  # Address where funds will be withdrawn
  min_amount: 30000  # Minimum amount to withdraw
  amount_currency: 'CLP'  # Currency defined for amount calculations

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

You need to have installed `python3.7` and `pipenv`.

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