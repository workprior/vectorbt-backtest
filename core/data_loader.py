import os
import requests
import zipfile
import io
import hashlib
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from core.symbol_selector import SymbolSelector


class DataLoader:
    def __init__(
        self,
        symbols=None,
        interval="1m",
        year=2025,
        month="02",
        market_type="spot",
    ):
        """
        Initialize the DataLoader.

        :param symbols: List of trading pairs to download.
        :param interval: Timeframe for OHLCV data (e.g., '1m').
        :param year: Year for the data.
        :param month: Month for the data.
        :param market_type: Type of market - 'spot' or 'futures'.
        """
        self.symbols = symbols
        self.interval = interval
        self.year = year
        self.month = month
        self.month_str = str(month).zfill(2)
        self.market_type = market_type
        self.save_path = (
            f"data/{market_type}_{interval}_{self.year}_{self.month_str}.parquet"
        )
        self.base_url = self._get_base_url()
        self.symbol_selector = SymbolSelector(
            interval=self.interval,
            year=self.year,
            month=self.month,
            market_type=self.market_type,
        )

    def _get_base_url(self):
        if self.market_type == "futures":
            return "https://data.binance.vision/data/futures/um/monthly/klines"
        return "https://data.binance.vision/data/spot/monthly/klines"

    def get_top_symbols(self, num_symbols, reverse=False):
        self.symbols = self.symbol_selector.get_top_symbols(num_symbols, reverse)

    def load_or_get_data(self, num_symbols=100):
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
        self.get_top_symbols(num_symbols)
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
                if self._validate_data(df):
                    all_data.append(df)
            except Exception as e:
                print(f"❌ Skipped {symbol}: {e}")

        if not all_data:
            raise Exception("❌ No data could be downloaded for any symbol")

        return pd.concat(all_data, axis=0)

    def _validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the structure and content of the DataFrame.

        :param df: DataFrame to validate.
        :return: True if valid, False otherwise.
        """
        return not df.empty and {
            "open",
            "high",
            "low",
            "close",
            "volume",
            "symbol",
        }.issubset(df.columns)

    def get_request_url(self, url: str) -> requests.Response:
        """
        Send GET request to the given URL and return the response object.
        Raise an exception if status code is not 200.

        :param url: URL to fetch.
        :return: Response object.
        """
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code} — File not found: {url}")
        return response

    def checksum_response(
        self,
        checksum_response: requests.Response,
        response: requests.Response,
        symbol: str,
    ):
        """
        Validate the SHA256 checksum of the downloaded .zip file.

        :param checksum_response: Response object containing the checksum text.
        :param response: Original response with .zip binary content.
        :param symbol: Trading pair symbol for logging.
        """
        expected_hash = checksum_response.text.strip().split()[0]
        actual_hash = hashlib.sha256(response.content).hexdigest()
        if expected_hash != actual_hash:
            raise Exception(
                f"❌ Checksum mismatch for {symbol}: expected {expected_hash}, got {actual_hash}"
            )

    def download_symbol_data(self, symbol: str) -> pd.DataFrame:
        """
        Download and preprocess OHLCV data for a single trading pair.

        :param symbol: Trading pair symbol (e.g., 'ETHBTC').
        :return: Cleaned and formatted DataFrame.
        """
        file_name = f"{symbol}-{self.interval}-{self.year}-{self.month_str}.zip"
        url = f"{self.base_url}/{symbol}/{self.interval}/{file_name}"
        checksum_url = f"{url}.CHECKSUM"

        response = self.get_request_url(url)

        try:
            checksum_resp = self.get_request_url(checksum_url)
            self.checksum_response(checksum_resp, response, symbol)
        except Exception as e:
            print(f"⚠️ Skipping checksum validation for {symbol}: {e}")

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_file = z.namelist()[0]
            with z.open(csv_file) as f:
                df = pd.read_csv(f, header=None)

        if df.empty or df.shape[1] < 7:
            raise Exception(f"⛔ CSV for {symbol} is empty or malformed")

        df = df.iloc[:, :12]  # keep only the first 12 columns

        df.columns = [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "num_trades",
            "taker_base_vol",
            "taker_quote_vol",
            "ignore",
        ]

        ts = df["timestamp"].astype("int64")

        if ts.max() > 1e17:
            print(f"⚠️ Fixing timestamp for {symbol}: nanoseconds → ms")
            ts = ts // 1_000_000
        elif ts.max() > 1e14:
            print(f"⚠️ Fixing timestamp for {symbol}: microseconds → ms")
            ts = ts // 1_000
        elif ts.max() < 1e12:
            print(f"⚠️ Fixing timestamp for {symbol}: seconds → ms")
            ts = ts * 1000

        df["timestamp"] = pd.to_datetime(ts, unit="ms")
        df.set_index("timestamp", inplace=True)
        df["symbol"] = symbol

        return df[["open", "high", "low", "close", "volume", "symbol"]]

    def save_to_parquet(self, df: pd.DataFrame):
        """
        Save the DataFrame to a .parquet file with gzip compression.

        :param df: The DataFrame to be saved.
        """
        print("💾 Saving data to .parquet file")

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)

        if df.index.name != "timestamp":
            raise Exception("❌ 'timestamp' is not set as index")

        print(f"✅ Index before saving: {df.index.name}, type: {df.index.dtype}")
        df.to_parquet(self.save_path, compression="gzip", index=True)
        print(f"📁 File saved to {self.save_path}")
