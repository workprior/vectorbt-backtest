import pandas as pd
import vectorbt as vbt
from strategies.base import StrategyBase

class VWAP_Reversion_Strategy(StrategyBase):
    """
    VWAP Reversion Strategy.
    
    This strategy generates buy and sell signals based on price deviation from the 
    Volume Weighted Average Price (VWAP).
    
    Buy Signal: When price is below the VWAP by a certain threshold.
    Sell Signal: When price is above the VWAP by the same threshold.
    
    Attributes:
    -----------
    deviation_threshold : float
        The threshold for the price deviation from VWAP (default is 0.01).
    signals : dict
        A dictionary containing the generated entry and exit signals.
    result : Portfolio
        Backtest result stored as a Portfolio object.
    """
    
    name_strategy = "VWAP Reversion"
    
    def __init__(self, price_data: pd.DataFrame, deviation_threshold=0.01):
        """
        Initializes the VWAP Reversion strategy with price data and deviation threshold.
        
        Parameters:
        -----------
        price_data : pd.DataFrame
            Historical price data containing at least the 'close' and 'volume' prices.
        deviation_threshold : float, optional
            The threshold for deviation from VWAP (default is 0.01).
        """
        super().__init__(price_data)
        self.deviation_threshold = deviation_threshold
        self.price_data['VWAP'] = self.compute_vwap()

    def compute_vwap(self):
        """
        Computes the Volume Weighted Average Price (VWAP).
        
        Returns:
        --------
        pd.Series
            The VWAP series computed using cumulative volume and price.
        """
        cumulative_volume = self.price_data['volume'].cumsum()
        cumulative_price_volume = (self.price_data['close'] * self.price_data['volume']).cumsum()
        vwap = cumulative_price_volume / cumulative_volume
        return vwap

    def generate_signals(self) -> pd.DataFrame:
        """
        Generates entry and exit signals based on price deviation from VWAP.
        
        The strategy generates:
        - `entries`: True when price is below VWAP by a threshold.
        - `exits`: True when price is above VWAP by a threshold.
        
        Returns:
        --------
        pd.DataFrame
            A DataFrame with 'entry' and 'exit' columns containing boolean values for each bar.
        """
        close = self.price_data['close']
        vwap = self.price_data['VWAP']

        # Generate entry and exit signals
        entries = close < vwap * (1 - self.deviation_threshold)
        exits = close > vwap * (1 + self.deviation_threshold)

        self.signals = {'entries': entries, 'exits': exits}
        
        return pd.DataFrame({'entry': entries, 'exit': exits}, index=close.index)
