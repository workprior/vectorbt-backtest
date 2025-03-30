from core.data_loader import DataLoader
import pandas as pd


loader = DataLoader()
df = loader.load_or_get_data()
print(df.head())