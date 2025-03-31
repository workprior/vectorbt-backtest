import pandas as pd
import vectorbt as vbt
import vectorbt.indicators as vbtind
from strategies.base import StrategyBase


class SmaCrossoverStrategy(StrategyBase):
    """
    Simple SMA Crossover strategy.
    
    This strategy buys when the fast Simple Moving Average (SMA) crosses above 
    the slow SMA, and sells when the fast SMA crosses below the slow SMA.
    
    Attributes:
    -----------
    name_strategy : str
        Name of the strategy, used for saving and logging purposes.
    fast_window : int
        The window size for the fast SMA (default is 10).
    slow_window : int
        The window size for the slow SMA (default is 50).
    signals : dict
        Dictionary containing the generated entry and exit signals.
    result : Portfolio
        Backtest result stored as a Portfolio object.
    """
    
    name_strategy = "SMA Crossover"
    
    def __init__(self, price_data: pd.DataFrame, fast_window=150, slow_window=250):
        """
        Initialize the SMA Crossover strategy with price data and the SMA window sizes.

        Parameters:
        -----------
        price_data : pd.DataFrame
            Historical price data containing at least the 'close' prices.
        fast_window : int, optional
            The window size for the fast SMA (default is 10).
        slow_window : int, optional
            The window size for the slow SMA (default is 50).
        """
        super().__init__(price_data)
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.signals = None  # Placeholder for the signals
        self.result = None  # Placeholder for the backtest result

    def generate_signals(self) -> pd.DataFrame:
        """
        Generate entry and exit signals for the strategy based on SMA crossovers.
        
        The strategy will generate:
        - `entries`: True when fast SMA crosses above slow SMA.
        - `exits`: True when fast SMA crosses below slow SMA.

        Returns:
        --------
        pd.DataFrame
            A DataFrame with 'entry' and 'exit' columns containing boolean values for each bar.
        """
        close = self.price_data['close']

        # Calculate fast and slow SMAs
        fast_sma = vbtind.MA.run(close, window=self.fast_window).ma
        slow_sma = vbtind.MA.run(close, window=self.slow_window).ma

        # Generate entries and exits based on SMA crossovers
        entries = (fast_sma > slow_sma) & (fast_sma.shift(1) <= slow_sma.shift(1))
        exits = (fast_sma < slow_sma) & (fast_sma.shift(1) >= slow_sma.shift(1))

        self.signals = {'entries': entries, 'exits': exits}
        
        # Return signals as a DataFrame
        return pd.DataFrame({'entry': entries, 'exit': exits}, index=close.index)

    def run_backtest(self) -> pd.DataFrame:
        """
        Run the backtest for the strategy using the generated entry and exit signals.

        If signals are not generated yet, this method will call `generate_signals()` first.

        Returns:
        --------
        pd.DataFrame
            A DataFrame containing the backtest statistics.
        """
        if self.signals is None:
            self.generate_signals()

        # Create Portfolio from entry and exit signals
        pf = vbt.Portfolio.from_signals(
            close=self.price_data['close'],
            entries=self.signals['entries'],
            exits=self.signals['exits'],
            init_cash=1000,
            fees=0.001,  # Example transaction fee
            slippage=0.001  # Example slippage
        )

        self.result = pf
        return pf.stats()  # Return the statistics of the backtest

    def get_metrics(self) -> dict:
        """
        Retrieve key performance metrics from the backtest result.

        If the backtest hasn't been run yet, it will call `run_backtest()`.

        Returns:
        --------
        dict
            A dictionary containing the following metrics:
            - Total Return [%]
            - Sharpe Ratio
            - Max Drawdown [%]
            - Win Rate [%]
            - Expectancy
            - Exposure Time [%]
        """
        if self.result is None:
            self.run_backtest()

        stats = self.result.stats()

        # Calculate exposure time based on trades
        trades = self.result.get_trades()
        total_duration = len(self.result.wrapper.index)  # Total bars in the backtest
        exposure_duration = trades.records['exit_idx'] - trades.records['entry_idx']  # Duration of each trade
        exposure_time_percent = exposure_duration.sum() / total_duration * 100  # Calculate % of exposure time
        
        # Return metrics as a dictionary
        return {
            'Total Return [%]': stats.loc['Total Return [%]'],
            'Sharpe Ratio': stats.loc['Sharpe Ratio'],
            'Max Drawdown [%]': stats.loc['Max Drawdown [%]'],
            'Win Rate [%]': stats.loc['Win Rate [%]'],
            'Expectancy': stats.loc['Expectancy'],
            'Exposure Time [%]': exposure_time_percent
        }
