from core.data_loader import DataLoader
import pandas as pd
from strategies.sma_cross import SmaCrossoverStrategy
from strategies.rsi_bb import RSI_Bollinger_Strategy
from strategies.vrap_reversion import VWAP_Reversion_Strategy
from core.backtester import Backtester

loader = DataLoader()
df = loader.load_or_get_data()
print(df.head())

backtester = Backtester(strategy_cls=VWAP_Reversion_Strategy, price_data=df)
backtester.run()