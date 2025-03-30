import os
import requests
import zipfile
import io
import pandas as pd
from datetime import datetime
from tqdm import tqdm

class DataLoader:
    def __init__(self, symbols, interval='1m', year=2025, month='02', save_path='data/btc_1m_feb25.parquet'):
        """
        Initialize the DataLoader.

        :param symbols: List of trading pairs to download.
        :param interval: Timeframe for OHLCV data (e.g., '1m').
        :param year: Year for the data.
        :param month: Month for the data.
        :param save_path: Path to save the resulting parquet file.
        """
        self.symbols = symbols
        self.interval = interval
        self.year = year
        self.month = month
        self.month_str = str(month).zfill(2)
        self.base_url = "https://data.binance.vision/data/spot/monthly/klines"
        self.save_path = save_path

    def load_or_get_data(self):
        """
        Load cached data if available, otherwise download and save new data.

        :return: Combined DataFrame with OHLCV data for all symbols.
        """
        if os.path.exists(self.save_path):
            print("📦 File already exists — loading from cached .parquet")
            df = pd.read_parquet(self.save_path)
            print(f"Index name: {df.index.name}, type: {df.index.dtype}")
            return df

        print("📡 Downloading data from Binance Data Vision...")
        df = self.download_all_symbols()

        if df.empty:
            raise Exception("❌ All trading pairs are invalid or failed to download")

        self.save_to_parquet(df)
        return df

    def download_all_symbols(self):
        """
        Download OHLCV data for all specified trading pairs.

        :return: Combined DataFrame with data from all symbols.
        """
        all_data = []
        for symbol in tqdm(self.symbols, desc="📥 Downloading trading pairs"):
            try:
                df = self.download_symbol_data(symbol)
                all_data.append(df)
            except Exception as e:
                print(f"❌ Skipped {symbol}: {e}")

        if not all_data:
            raise Exception("❌ No data could be downloaded for any symbol")

        return pd.concat(all_data, axis=0)

    def download_symbol_data(self, symbol: str) -> pd.DataFrame:
        """
        Download and preprocess OHLCV data for a single trading pair.

        :param symbol: Trading pair symbol (e.g., 'ETHBTC').
        :return: Cleaned and formatted DataFrame.
        """
        file_name = f"{symbol}-{self.interval}-{self.year}-{self.month_str}.zip"
        url = f"{self.base_url}/{symbol}/{self.interval}/{file_name}"

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code} — File not found: {url}")

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_file = z.namelist()[0]
            with z.open(csv_file) as f:
                df = pd.read_csv(f, header=None)

        if df.empty or df.shape[1] < 7:
            raise Exception(f"⛔ CSV for {symbol} is empty or malformed")

        df = df.iloc[:, :12]  # keep only the first 12 columns

        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                      'close_time', 'quote_volume', 'num_trades',
                      'taker_base_vol', 'taker_quote_vol', 'ignore']

        ts = df['timestamp'].astype("int64")

        if ts.max() > 1e17:
            print(f"⚠️ Fixing timestamp for {symbol}: nanoseconds → ms")
            ts = ts // 1_000_000
        elif ts.max() > 1e14:
            print(f"⚠️ Fixing timestamp for {symbol}: microseconds → ms")
            ts = ts // 1_000
        elif ts.max() < 1e12:
            print(f"⚠️ Fixing timestamp for {symbol}: seconds → ms")
            ts = ts * 1000

        df['timestamp'] = pd.to_datetime(ts, unit='ms')
        df.set_index('timestamp', inplace=True)
        df['symbol'] = symbol

        return df[['open', 'high', 'low', 'close', 'volume', 'symbol']]

    def save_to_parquet(self, df: pd.DataFrame):
        """
        Save the DataFrame to a .parquet file with gzip compression.

        :param df: The DataFrame to be saved.
        """
        print("💾 Saving data to .parquet file")

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)

        if df.index.name != 'timestamp':
            raise Exception("❌ 'timestamp' is not set as index")

        print(f"✅ Index before saving: {df.index.name}, type: {df.index.dtype}")
        df.to_parquet(self.save_path, compression='gzip', index=True)
        print(f"📁 File saved to {self.save_path}")
