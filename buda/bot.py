# Base class that all Bots must inherit from
from trading_bots.bots import Bot

# The settings module contains all values from settings.yml and secrets.yml
from trading_bots.conf import settings
from trading_bots.contrib.exchanges import buda, bitfinex, bitstamp, kraken
from trading_bots.contrib.models import Market, Side, Money, TxStatus, OrderStatus
from trading_bots.contrib.converters.open_exchange_rates import OpenExchangeRates
from trading_bots.utils import truncate_money

import requests
from datetime import datetime
from time import sleep
from decimal import Decimal

class BudaBot(Bot):
    # The label is a unique identifier you assign to your bot on Trading-Bots
    label = 'buda'

    market_clients = [
        buda.BudaMarket,
        bitfinex.BitfinexMarket,
        bitstamp.BitstampMarket,
        kraken.KrakenMarket,
    ]

    def _setup(self, config):
        # Initialize a Buda.com and reference exchange clients
        self.market = Market.from_code(config['investment']['market'])
        self.ref_market = Market.from_code(config['investment']['ref_market'])
        self.buda = buda.BudaTrading(market=self.market, dry_run=self.dry_run)
        self.reference = self.get_market_client(config['investment']['ref_exchange'], self.ref_market)
        # Initialize Algorithm configs
        self.daily_investment = Money(str(config['investment']['monthly_amount'] / 30), self.market.quote)
        self.interval_hours = config['investment']['interval_hours']
        self.transactions = self.store.get(f'transactions_{self.market}'.lower()) or []
        self.amount_investment = self.calculate_amount_investment()
        self.override_min_order_amount_btc()
        assert self.amount_investment > Money('1', self.market.quote), 'Amount investment too low'
        self.overprice_limit = config['investment']['overprice_limit']
        # Currency converter to use
        self.converter = config['currency_converter']
        self.rate = self.get_converter_rate()
        # Set withdrawal configs
        self.withdrawal_enabled = config['withdrawal']['enabled']
        self.withdrawal_address = config['withdrawal']['address']
        w_amount = str(config['withdrawal']['min_amount'])
        self.minimum_withdrawal_amount = Money(w_amount, config['withdrawal']['amount_currency'])

    def _algorithm(self):
        balance = self.buda.wallets.quote.fetch_balance().free
        international_price = self.reference.fetch_ticker().last
        buy_amount = self.get_amount_to_buy()

        buy_price = truncate_money(Money(self.amount_investment.amount / buy_amount.amount, self.market.quote))
        reference_price = truncate_money(Money(international_price.amount * self.rate.amount, self.rate.currency))

        self.log.info(f'I have {balance}')
        self.log.info(f'I will invest {self.amount_investment}')
        self.log.info(f'{self.ref_market.quote}{self.market.quote}: {self.rate}')
        self.log.info(f'{self.market.base} to buy: {buy_amount}')

        # Log the price
        self.log.info(f'International {self.ref_market} price: {international_price}')
        self.log.info(f'International {self.market} price: {reference_price}')

        self.log.info(f'---------------------------------------')
        self.log.info(f'Buy price: {buy_price}')
        self.log.info(f'Overprice: {(self.get_overprice(buy_price, reference_price)):.2%}')
        self.log.info(f'Should buy? {(self.should_buy(buy_price, reference_price, balance))}')
        self.log.info(f'---------------------------------------')

        if not self.already_transacted():
            if self.should_buy(buy_price, reference_price, balance):
                if self.send_buy_order(buy_amount):
                    self.store_transaction(buy_price, self.amount_investment, buy_amount)
                else:
                    self.log.info(f'Problem with order')
            else:
                self.log.info(f'Not investing')
        else:
            self.log.info(f'Already transacted')

        if self.withdrawal_enabled:
            self.log.info(f'Withdrawal enabled to address {self.withdrawal_address}')
            self.withdraw_to_own_wallet(reference_price)
        else:
            self.log.info(f'Withdrawal not enabled')


    def _abort(self):
        # Abort logic, runs on exception
        self.log.error(f'Something went wrong with bot!')

    def get_converter_rate(self):
        # Set currency converter
        if self.converter == 'OpenExchangeRates':
            app_id = settings.credentials['OpenExchangeRates']['app_id']
            converter = OpenExchangeRates(return_decimal=True, client_params=dict(app_id=app_id))
            return truncate_money(Money(converter.convert(1, self.ref_market.quote, self.market.quote),
                                        self.market.quote))
        elif self.converter == 'Currencyconverterapi':
            api_key = settings.credentials['Currencyconverter']['key']
            code = f'{self.ref_market.quote}_{self.market.quote}'
            rate = requests.get(
                f'https://free.currencyconverterapi.com/api/v6/convert?q={code}&compact=y&apiKey={api_key}'
            ).json()[code]['val']
            return truncate_money(Money(rate, self.market.quote))

    def override_min_order_amount_btc(self):
        buda.BudaTrading.min_order_amount_mapping = {
            'BCH': Decimal('0.0001'),
            'BTC': Decimal('0.00001'),
            'ETH': Decimal('0.001'),
            'LTC': Decimal('0.00001'),
        }

    def get_amount_to_buy(self):
        quotation = self.buda.fetch_order_book().quote(Side.BUY, amount=self.amount_investment)
        return truncate_money(quotation.base_amount)

    def get_overprice(self, buy_price, international_price_clp):
        return buy_price.amount / international_price_clp.amount - Decimal('1')

    def has_enough_balance(self, balance):
        return balance > self.amount_investment

    def should_buy(self, buy_price, international_price_clp, balance):
        overprice = self.get_overprice(buy_price, international_price_clp)
        if overprice < self.overprice_limit and self.has_enough_balance(balance):
            return True
        return False

    def store_transaction(self, buy_price, quote_amount, base_amount):
        self.transactions.append({
            'date': datetime.today().strftime("%b %d %Y %H:%M:%S"),
            'buy_price': float(buy_price.amount),
            'quote_amount': float(quote_amount.amount),
            'base_amount': float(base_amount.amount),
        })
        self.store.set(f'transactions_{self.market}'.lower(), self.transactions)

    def already_transacted(self):
        if len(self.transactions) > 0:
            last_transaction = self.transactions[-1]
            last_transaction_date = datetime.strptime(last_transaction['date'], "%b %d %Y %H:%M:%S")
            if self.intervals_without_investing(last_transaction_date) == 0:
                return True
        return False

    def send_buy_order(self, amount):
        order = self.buda.place_market_order(Side.BUY, amount)
        if order:
            self.log.info(f'Market order placed, waiting for traded state')
            while order.status != OrderStatus.CLOSED:
                order = self.buda.fetch_order(order.id)
                sleep(1)
            return True
        return False

    def intervals_without_investing(self, last_transaction_date):
        if last_transaction_date is None:
            return 1
        last_transaction_date_hour = last_transaction_date.replace(minute=0, second=0, microsecond=0)
        diff_hours = ((datetime.now() - last_transaction_date_hour).total_seconds() // 60) / 60
        return diff_hours // self.interval_hours

    def calculate_amount_investment(self):
        last_transaction = self.transactions[-1] if len(self.transactions) > 0 else None
        last_tx_date = datetime.strptime(last_transaction['date'], "%b %d %Y %H:%M:%S") if last_transaction else None
        interval_investment = self.daily_investment / 24 * self.interval_hours
        if last_tx_date is None:
            return truncate_money(interval_investment)
        intervals_without_investing = self.intervals_without_investing(last_tx_date)
        self.log.info(f'Intervals without investing: {intervals_without_investing}')
        return truncate_money(int(intervals_without_investing) * interval_investment)

    def withdraw_to_own_wallet(self, reference_price):
        if self.minimum_withdrawal_amount.currency == self.market.quote:
            min_amount = truncate_money(Money(self.minimum_withdrawal_amount.amount / reference_price.amount,
                                              self.market.base))
        else:
            min_amount = truncate_money(self.minimum_withdrawal_amount)
        assert min_amount.currency == self.market.base, 'Something is wrong with withdrawal currency'
        balance = self.buda.wallets.base.fetch_balance().free
        if balance >= min_amount:
            self.log.info(f'Requesting withdrawals of {balance} to {self.withdrawal_address}')
            self.buda.wallets.base.request_withdrawal(balance, self.withdrawal_address, substract_fee=True)
        else:
            self.log.info(f'Not enough balance: {balance} < {min_amount}')

    def get_market_client(self, name, market):
        for client in self.market_clients:
            if client.name == name:
                return client(market, client=None, dry_run=self.dry_run,
                              timeout=self.timeout, logger=self.log, store=self.store)
        raise NotImplementedError(f'Client {name} not found!')
