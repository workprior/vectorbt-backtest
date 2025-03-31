import os
import pandas as pd
from strategies.base import StrategyBase
from typing import Type
from metrics import MetricsStatistics

class Backtester:
    """
    Backtester that runs a strategy (subclass of StrategyBase)
    on multiple trading pairs and saves the results, including performance metrics and equity curves.

    Attributes:
    -----------
    strategy_cls : Type[StrategyBase]
        The strategy class to be used for backtesting. It should be a subclass of StrategyBase.
    price_data : pd.DataFrame
        DataFrame containing historical price data (must include a 'symbol' column).
    results_path : str
        Directory where the results (metrics and plots) will be saved.
    metrics : list
        List that stores the metrics for each backtest.
    """

    def __init__(self, strategy_cls: Type[StrategyBase], price_data: pd.DataFrame, results_path='results/'):
        """
        Initializes the Backtester with the given strategy, price data, and results directory.

        Parameters:
        -----------
        strategy_cls : Type[StrategyBase]
            Strategy class (must inherit from StrategyBase).
        price_data : pd.DataFrame
            Combined OHLCV DataFrame for all symbols (must include a 'symbol' column).
        results_path : str, optional
            Path to save metrics and plots. Default is 'results/'.
        """
        self.strategy_cls = strategy_cls
        self.price_data = price_data
        self.results_path = results_path
        self.screenshots_path = os.path.join(self.results_path, 'screenshots')
        self.metrics = []

        self.metrics_statistics = MetricsStatistics()

        # Create results directory if it doesn't exist
        os.makedirs(self.results_path, exist_ok=True)
        os.makedirs(os.path.join(self.results_path, 'screenshots'), exist_ok=True)


    def run(self):
        """
        Run backtest on each symbol and collect stats and charts.
        
        This method loops through all unique symbols in the provided price data, 
        applies the strategy, and collects the metrics and equity curve for each symbol.

        After running the backtests for all symbols, it saves the metrics to a CSV 
        file and the equity curves to PNG files.
        """
        symbols = self.price_data['symbol'].unique()

        # Loop over each symbol to run the backtest
        for symbol in symbols:
            print(f"🚀 Running backtest for {symbol}...")

            # Filter data for the current symbol
            symbol_data = self.price_data[self.price_data['symbol'] == symbol].copy()

            # Initialize the strategy
            strategy = self.strategy_cls(symbol_data)

            # Generate entry and exit signals, and run backtest
            strategy.generate_signals()
            strategy.run_backtest()

            # Collect metrics and add symbol and strategy name
            metrics = strategy.get_metrics()
            metrics['symbol'] = symbol
            metrics['strategy_name'] = self.strategy_cls.name_strategy
            self.metrics.append(metrics)

            print(f"Metrics for {symbol} collected")
            
            pf = strategy.result
            pf.plot().write_image(os.path.join(self.screenshots_path, f"{symbol}_{self.strategy_cls.name_strategy}_equity_curve.png"))

        # Save all metrics to a CSV file
        df_metrics = pd.DataFrame(self.metrics)
        df_metrics = df_metrics[['symbol', 'strategy_name', 'Total Return [%]', 'Sharpe Ratio', 'Max Drawdown [%]',
                                 'Win Rate [%]', 'Expectancy', 'Exposure Time [%]']]  # Ordered columns for CSV
        metrics_csv_path = os.path.join(self.results_path, f"{self.strategy_cls.name_strategy}_metrics.csv")
        df_metrics.to_csv(metrics_csv_path, index=False)

        # Output the collected metrics and confirm the CSV file saving
        print(f"📊 Metrics saved to {metrics_csv_path}")
