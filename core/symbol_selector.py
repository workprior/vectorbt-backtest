import requests
from datetime import datetime
from tqdm import tqdm


class SymbolSelector:
    def __init__(self, interval="1d", year=2025, month="02", market_type="spot", quote_asset="BTC"):
        """
        Initialize SymbolSelector instance.
        """
        self.interval = interval
        self.year = year
        self.month = str(month).zfill(2)
        self.market_type = market_type
        self.quote_asset = quote_asset
        self.symbols = []
        self.base_url = self._get_base_url()
        self.exchange_info_url = self._get_exchange_info_url()

    def _get_exchange_info_url(self):
        if self.market_type == "spot":
            return "https://api.binance.com/api/v3/exchangeInfo"
        elif self.market_type == "futures":
            return "https://fapi.binance.com/fapi/v1/exchangeInfo"
        else:
            raise ValueError("market_type must be either 'spot' or 'futures'")

    def _get_base_url(self):
        if self.market_type == "spot":
            return "https://api.binance.com/api/v3/klines"
        elif self.market_type == "futures":
            return "https://fapi.binance.com/fapi/v1/klines"
        else:
            raise ValueError("market_type must be either 'spot' or 'futures'")

    def _get_all_symbols(self):
        """
        Get all trading symbols with given quote asset from Binance.
        """
        response = requests.get(self.exchange_info_url)
        response.raise_for_status()
        exchange_info = response.json()

        return [
            s['symbol'] for s in exchange_info['symbols']
            if s['quoteAsset'] == self.quote_asset and s['status'] == 'TRADING'
        ]

    def _get_time_range(self):
        """
        Calculate start and end timestamp in ms for the selected month.
        """
        start_str = f"{self.year}-{self.month}-01"
        start_ts = int(datetime.strptime(start_str, "%Y-%m-%d").timestamp() * 1000)

        next_month = int(self.month) + 1
        if next_month > 12:
            end_str = f"{self.year + 1}-01-01"
        else:
            end_str = f"{self.year}-{str(next_month).zfill(2)}-01"
        end_ts = int(datetime.strptime(end_str, "%Y-%m-%d").timestamp() * 1000)

        return start_ts, end_ts

    def get_top_symbols(self, top_n=100, reverse=False):
        """
        Get top (or bottom) N symbols sorted by total monthly volume.
        """
        symbols = self._get_all_symbols()
        start_ts, end_ts = self._get_time_range()
        volume_map = {}

        print(f"📊 Fetching volume for {len(symbols)} pairs...")

        for symbol in tqdm(symbols):
            try:
                params = {
                    "symbol": symbol,
                    "interval": self.interval,
                    "startTime": start_ts,
                    "endTime": end_ts,
                    "limit": 1000
                }
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    volume_sum = sum(float(entry[5]) for entry in data)  # volume at index 5
                    volume_map[symbol] = volume_sum
            except Exception as e:
                print(f"⚠️ Failed to fetch data for {symbol}: {e}")

        sorted_symbols = sorted(volume_map.items(), key=lambda x: x[1], reverse=not reverse)
        self.symbols = [s[0] for s in sorted_symbols[:top_n]]

        print(f"✅ Selected top {top_n} symbols based on volume")
        return self.symbols
