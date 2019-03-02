# Base class that all Bots must inherit from
from trading_bots.bots import Bot

# The settings module contains all values from settings.yml and secrets.yml
from trading_bots.conf import settings

from trading_api_wrappers import Bitstamp, Buda

from trading_bots.contrib.clients import buda
from trading_bots.contrib.clients import Market, Side


import requests
import datetime
import json
from time import sleep
import time

class BudaBot(Bot):
    # The label is a unique identifier you assign to your bot on Trading-Bots
    label = 'buda'

    def _setup(self, config):
        # Get API_KEY and API_SECRET from credentials
        credentials = settings.credentials['Buda']
        key = credentials['key']
        secret = credentials['secret']

        # Initialize a Buda Auth client
        self.buda_basic = Buda.Auth(key, secret)
        self.buda_auth = buda.BudaAuth(key, secret)
        self.buda_trading = buda.BudaTrading(
            'btcclp', dry_run=self.dry_run, timeout=self.timeout, logger=self.log, store=self.store)
        self.buda_wallets = self.buda_trading.wallet_client('CLP')
        self.bitstamp = Bitstamp.Public()

        self.daily_investment = settings.investment['monthly'] / 30
        self.transactions = json.loads(self.store.get('transactions') or '[]')
        now = datetime.datetime.now()
        last_transaction = self.transactions[-1] if len(self.transactions) > 0 else None
        last_transaction_date = datetime.datetime.strptime(last_transaction['date'], "%b %d %Y %H:%M:%S") if last_transaction else None
        self.amount_investment = self.calculate_amount_investment(now, last_transaction_date)

    def _algorithm(self):
        if self.amount_investment <= 1:
            self.log.info(f'Amount investment too low')
            return

        balance = self.buda_trading.wallet_client('CLP').get_available()
        international_price = self.bitstamp.ticker('BTCUSD')['last']
        btc_change = self.get_btc_to_buy(self.amount_investment)

        usd_clp = self.get_usd_clp()
        buy_price = int(float(self.amount_investment) / float(btc_change))
        international_price_clp = int(float(international_price) * float(usd_clp))

        self.log.info(f'I have {balance} CLP')
        self.log.info(f'I will invest {self.amount_investment} CLP')
        self.log.info(f'USDCLP: {usd_clp} CLP')
        self.log.info(f'BTC to buy: {btc_change} BTC')

        # Log the Bitcoin price
        self.log.info(f'International BTCUSD price: {international_price} USD')
        self.log.info(f'International BTCLP price: {international_price_clp} CLP')

        self.log.info(f'---------------------------------------')
        self.log.info(f'Buy price: {buy_price} CLP')
        self.log.info(f'Overprice: {(self.get_overprice(buy_price, international_price_clp)):.2%}')
        self.log.info(f'Should buy? {(self.should_buy(buy_price, international_price_clp, balance))}')
        self.log.info(f'---------------------------------------')

        if not self.already_transacted():
            if self.should_buy(buy_price, international_price_clp, balance):
                if self.buy_btc(btc_change):
                    self.store_transaction(buy_price, self.amount_investment, btc_change)
                else:
                    self.log.info(f'Problem with order')
            else:
                self.log.info(f'Not investing')
        else:
            self.log.info(f'Already transacted')



    def _abort(self):
        # Abort logic, runs on exception
        self.log.error(f'Something went wrong with bot!')

    def get_usd_clp(self):
        api_key = settings.apis['currencyconverter_key']
        return requests.get(
            f'https://free.currencyconverterapi.com/api/v6/convert?q=USD_CLP&compact=y&apiKey={api_key}'
        ).json()['USD_CLP']['val']

    def get_btc_to_buy(self, balance):
        quotation = self.buda_basic.quotation_market('btc-clp', 'bid_given_value', self.amount_investment).json
        return quotation['base_balance_change'][0]

    def get_overprice(self, buy_price, international_price_clp):
        return float(buy_price) / float(international_price_clp) - 1

    def has_enough_balance(self, balance):
        return balance > self.amount_investment

    def should_buy(self, buy_price, international_price_clp, balance):
        if (
            self.get_overprice(buy_price, international_price_clp) < settings.investment['overprice_limit'] and
            self.has_enough_balance(balance)
        ):
            return True
        return False

    def store_transaction(self, buy_price, amount_clp, amount_btc):
        transactions = json.loads(self.store.get('transactions') or '[]')
        transactions.append({
            'date': datetime.datetime.today().strftime("%b %d %Y %H:%M:%S"),
            'buy_price': buy_price,
            'amount_clp': amount_clp,
            'amount_btc': amount_btc
        })
        self.store.set('transactions', json.dumps(transactions))

    def already_transacted(self):
        transactions = json.loads(self.store.get('transactions') or '[]')
        if len(transactions) > 0:
            last_transaction = transactions[-1]
            last_transaction_date = datetime.datetime.strptime(last_transaction['date'], "%b %d %Y %H:%M:%S")
            if self.intervals_without_investing(last_transaction_date) == 0:
                return True
        return False

    def buy_btc(self, amount):
        order = self.buda_trading.place_market_order(Side.BUY, amount)
        if order:
            self.log.info(f'Market order placed, waiting for traded state')
            while order.state != 'traded':
                order = self.buda_trading.order_details(order.id)
                sleep(1)
            return True
        return False

    def intervals_without_investing(self, last_transaction_date):
        if last_transaction_date == None:
            return 1
        now_hour = datetime.datetime.now().hour
        last_transaction_date_hour = last_transaction_date.replace(minute=0, second=0, microsecond=0)
        current_interval = now_hour // settings.investment['interval_hours']
        last_transaction_interval = last_transaction_date_hour.hour // settings.investment['interval_hours']
        intervals_without_investing = current_interval - last_transaction_interval
        return intervals_without_investing

    def calculate_amount_investment(self, now, last_transaction_date):
        interval_investment = self.daily_investment / 24 * settings.investment['interval_hours']
        if last_transaction_date == None:
            return interval_investment
        intervals_without_investing = self.intervals_without_investing(last_transaction_date)
        self.log.info(f'Intervals without investing: {intervals_without_investing}')
        return intervals_without_investing * interval_investment
