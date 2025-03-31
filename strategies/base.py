import pandas as pd
import vectorbt as vbt
from abc import ABC, abstractmethod

class StrategyBase(ABC):
    """
    Base class for trading strategies.
    
    This class provides common functionality for all trading strategies, 
    such as running backtests, generating signals, and calculating performance metrics.
    
    Subclasses must implement the `generate_signals` method.
    """
    
    def __init__(self, price_data: pd.DataFrame):
        """
        Initializes the strategy with price data.
        
        Parameters:
        -----------
        price_data : pd.DataFrame
            Historical price data containing at least the 'close' prices.
        """
        self.price_data = price_data
        self.signals = None
        self.result = None

    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """
        Abstract method to generate entry and exit signals.
        
        Subclasses must implement this method to define their unique signal generation logic.
        """
        pass

    def run_backtest(self) -> pd.DataFrame:
        """
        Runs the backtest for the strategy using the generated entry and exit signals.
        
        Returns:
        --------
        pd.DataFrame
            A DataFrame containing the backtest statistics.
        """
        if self.signals is None:
            self.generate_signals()

        pf = vbt.Portfolio.from_signals(
            close=self.price_data['close'],
            entries=self.signals['entries'],
            exits=self.signals['exits'],
            init_cash=1000,
            fees=0.001,
            slippage=0.001
        )

        self.result = pf
        return pf.stats()

    def get_metrics(self) -> dict:
        """
        Retrieves key performance metrics from the backtest result.
        
        Metrics include:
        - Total Return [%]
        - Sharpe Ratio
        - Max Drawdown [%]
        - Win Rate [%]
        - Expectancy
        - Exposure Time [%]
        
        Returns:
        --------
        dict
            A dictionary of performance metrics.
        """
        if self.result is None:
            self.run_backtest()

        stats = self.result.stats()
        trades = self.result.get_trades()
        total_duration = len(self.result.wrapper.index)
        exposure_duration = trades.records['exit_idx'] - trades.records['entry_idx']
        exposure_time_percent = exposure_duration.sum() / total_duration * 100
        
        return {
            'Total Return [%]': stats.loc['Total Return [%]'],
            'Sharpe Ratio': stats.loc['Sharpe Ratio'],
            'Max Drawdown [%]': stats.loc['Max Drawdown [%]'],
            'Win Rate [%]': stats.loc['Win Rate [%]'],
            'Expectancy': stats.loc['Expectancy'],
            'Exposure Time [%]': exposure_time_percent
        }
