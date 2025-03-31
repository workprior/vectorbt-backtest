import pandas as pd
import vectorbt as vbt
import vectorbt.indicators as vbtind
from strategies.base import StrategyBase

class SmaCrossoverStrategy(StrategyBase):
    """
    Simple Moving Average (SMA) Crossover Strategy.
    
    This strategy generates buy and sell signals based on the crossover of two 
    SMAs: a fast one and a slow one.
    
    Buy Signal: When the fast SMA crosses above the slow SMA.
    Sell Signal: When the fast SMA crosses below the slow SMA.
    
    Attributes:
    -----------
    fast_window : int
        The window size for the fast SMA (default is 150).
    slow_window : int
        The window size for the slow SMA (default is 250).
    signals : dict
        A dictionary containing the generated entry and exit signals.
    result : Portfolio
        Backtest result stored as a Portfolio object.
    """

    name_strategy = "SMA Crossover"
    
    def __init__(self, price_data: pd.DataFrame, fast_window=150, slow_window=250):
        """
        Initializes the SMA Crossover strategy with price data and SMA parameters.
        
        Parameters:
        -----------
        price_data : pd.DataFrame
            Historical price data containing at least the 'close' prices.
        fast_window : int, optional
            The window size for the fast SMA (default is 150).
        slow_window : int, optional
            The window size for the slow SMA (default is 250).
        """
        super().__init__(price_data)
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self) -> pd.DataFrame:
        """
        Generates entry and exit signals based on SMA crossovers.
        
        The strategy generates:
        - `entries`: True when the fast SMA crosses above the slow SMA.
        - `exits`: True when the fast SMA crosses below the slow SMA.
        
        Returns:
        --------
        pd.DataFrame
            A DataFrame with 'entry' and 'exit' columns containing boolean values for each bar.
        """
        close = self.price_data['close']

        # Calculate fast and slow SMAs
        fast_sma = vbtind.MA.run(close, window=self.fast_window).ma
        slow_sma = vbtind.MA.run(close, window=self.slow_window).ma

        # Generate entries and exits based on crossover conditions
        entries = (fast_sma > slow_sma) & (fast_sma.shift(1) <= slow_sma.shift(1))
        exits = (fast_sma < slow_sma) & (fast_sma.shift(1) >= slow_sma.shift(1))

        self.signals = {'entries': entries, 'exits': exits}
        
        return pd.DataFrame({'entry': entries, 'exit': exits}, index=close.index)
