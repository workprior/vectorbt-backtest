from abc import ABC, abstractmethod
import pandas as pd


class StrategyBase(ABC):
    """
    Abstract base class for all trading strategies.
    Provides standard interface for generating signals, backtesting, and metrics.
    """

    def __init__(self, price_data: pd.DataFrame):
        """
        Initialize strategy with price data.

        :param price_data: DataFrame with OHLCV data.
        """
        self.price_data = price_data

    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """
        Generate trading signals based on strategy logic.

        :return: DataFrame with signals (1 = buy, -1 = sell, 0 = hold).
        """
        pass

    @abstractmethod
    def run_backtest(self) -> pd.DataFrame:
        """
        Run backtest based on generated signals.

        :return: DataFrame with backtest results.
        """
        pass

    @abstractmethod
    def get_metrics(self) -> dict:
        """
        Calculate and return strategy performance metrics.

        :return: Dictionary of metrics (e.g., Sharpe, Return, Drawdown).
        """
        pass
