import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta

PRIVATE_API_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='


class CurrencyApi:
    async def fetch_currency(self, session, url):
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"Invalid response status: {response.status}")
            return await response.json()

    async def get_currency(self, date: datetime):
        url = f"{PRIVATE_API_URL}{date.strftime('%d.%m.%Y')}"
        async with aiohttp.ClientSession() as session:
            return await self.fetch_currency(session, url)


class CurrencyRates:
    def __init__(self, days: int):
        self.days = days
        self.currency_api = CurrencyApi()

    async def get_rates(self):
        rates = []
        today = datetime.today()
        for i in range(self.days):
            date = today - timedelta(days=i)
            currency_data = await self.currency_api.get_currency(date)
            exchange_rates = currency_data.get('exchangeRate', [])
            rate = {}
            for e_rate in exchange_rates:
                if e_rate.get('currency') == 'USD':
                    rate['USD'] = {
                        'sale': e_rate.get('saleRate'),
                        'purchase': e_rate.get('purchaseRate')
                    }
                elif e_rate.get('currency') == 'EUR':
                    rate['EUR'] = {
                        'sale': e_rate.get('saleRate'),
                        'purchase': e_rate.get('purchaseRate')
                    }
            rates.append({date.strftime('%d.%m.%Y'): rate})
        return rates


async def main(days: int):
    currency_rates = CurrencyRates(days)
    rates = await currency_rates.get_rates()
    print(rates)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('days', type=int)
    args = parser.parse_args()

    asyncio.run(main(args.days))
