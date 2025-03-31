from core.backtester import Backtester
from core.data_loader import DataLoader

from strategies.sma_cross import SmaCrossoverStrategy
from strategies.rsi_bb import RSI_Bollinger_Strategy
from strategies.vrap_reversion import VWAP_Reversion_Strategy
from core.metrics import MetricsStatistics


def main():
    loader = DataLoader()
    df = loader.load_or_get_data(num_symbols=20)
    
    backtester = Backtester(strategy_cls=VWAP_Reversion_Strategy, price_data=df)
    backtester.run()
    backtester = Backtester(strategy_cls=RSI_Bollinger_Strategy, price_data=df)
    backtester.run()
    backtester = Backtester(strategy_cls=SmaCrossoverStrategy, price_data=df)
    backtester.run()
    
    metrics_statistics = MetricsStatistics()
    
    metrics_df = metrics_statistics.load_all_metrics()
    
    metrics_statistics.generate_html_report(metrics_df)

if __name__ == "__main__":
    main()
