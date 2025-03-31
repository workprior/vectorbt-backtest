from core.data_loader import DataLoader
import pandas as pd
from strategies.sma_cross import SmaCrossoverStrategy
from core.backtester import Backtester

loader = DataLoader()
df = loader.load_or_get_data()
print(df.head())

backtester = Backtester(strategy_cls=SmaCrossoverStrategy, price_data=df)
backtester.run()