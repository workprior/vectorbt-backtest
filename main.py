from core.data_loader import DataLoader
import pandas as pd

symbols = ["ETHBTC", "BNBBTC", "XRPBTC"]

loader = DataLoader(symbols=symbols)
df = loader.load_or_get_data()

print(df.head())
