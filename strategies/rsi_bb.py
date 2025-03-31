import pandas as pd
import vectorbt as vbt
import vectorbt.indicators as vbtind
from strategies.base import StrategyBase

class RSI_Bollinger_Strategy(StrategyBase):
    """
    RSI with Bollinger Bands Strategy.
    
    This strategy generates entry and exit signals based on the RSI indicator 
    combined with Bollinger Bands.
    
    Buy Signal: When RSI < 30 and price is below the lower Bollinger Band.
    Sell Signal: When RSI > 70 and price is above the upper Bollinger Band.
    
    Attributes:
    -----------
    rsi_period : int
        The window size for the RSI indicator (default is 14).
    bb_period : int
        The window size for the Bollinger Bands (default is 20).
    bb_std : float
        The number of standard deviations for the Bollinger Bands (default is 2).
    signals : dict
        A dictionary containing the generated entry and exit signals.
    result : Portfolio
        Backtest result stored as a Portfolio object.
    """

    name_strategy = "RSI and Bollinger Bands"
    
    def __init__(self, price_data: pd.DataFrame, rsi_period=14, bb_period=20, bb_std=2):
        """
        Initializes the RSI and Bollinger Bands strategy with price data and indicator parameters.
        
        Parameters:
        -----------
        price_data : pd.DataFrame
            Historical price data containing at least the 'close' prices.
        rsi_period : int, optional
            The window size for the RSI (default is 14).
        bb_period : int, optional
            The window size for the Bollinger Bands (default is 20).
        bb_std : float, optional
            The number of standard deviations for the Bollinger Bands (default is 2).
        """
        super().__init__(price_data)
        self.rsi_period = rsi_period
        self.bb_period = bb_period
        self.bb_std = bb_std

    def generate_signals(self) -> pd.DataFrame:
        """
        Generates entry and exit signals based on RSI and Bollinger Bands.
        
        The strategy generates:
        - `entries`: True when RSI < 30 and price is below the lower Bollinger Band.
        - `exits`: True when RSI > 70 and price is above the upper Bollinger Band.
        
        Returns:
        --------
        pd.DataFrame
            A DataFrame with 'entry' and 'exit' columns containing boolean values for each bar.
        """
        close = self.price_data['close']
        
        # Calculate RSI and Bollinger Bands
        rsi = vbtind.RSI.run(close, window=self.rsi_period).rsi
        bb = vbtind.BBANDS.run(close, window=self.bb_period, window_dev=self.bb_std)
        bb_upper = bb.upper
        bb_lower = bb.lower

        # Generate entries and exits based on conditions
        entries = (rsi < 30) & (close < bb_lower)
        exits = (rsi > 70) & (close > bb_upper)

        self.signals = {'entries': entries, 'exits': exits}
        
        return pd.DataFrame({'entry': entries, 'exit': exits}, index=close.index)
