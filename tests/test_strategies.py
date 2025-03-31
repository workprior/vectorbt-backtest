import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from strategies.sma_cross import SmaCrossoverStrategy
from strategies.rsi_bb import RSI_Bollinger_Strategy
from strategies.vrap_reversion import VWAP_Reversion_Strategy

class TestSmaCrossoverStrategy(unittest.TestCase):
    """
    Unit tests for the SmaCrossoverStrategy class.
    These tests validate the signal generation and backtesting functionality of the SMA Crossover strategy.
    """

    @patch('vectorbt.Portfolio.from_signals')  # Mocking the backtest execution
    def test_generate_signals(self, mock_backtest):
        """
        Test the signal generation for the SMA Crossover strategy.

        This test verifies that the correct entry and exit signals are generated based on the price data.
        """
        # Create test price data for the backtest
        price_data = pd.DataFrame({
            'close': [100, 105, 110, 115, 120, 125],
            'symbol': ['BTC/USD'] * 6
        })

        # Initialize the strategy with test data
        strategy = SmaCrossoverStrategy(price_data, fast_window=3, slow_window=5)

        # Generate the signals
        signals = strategy.generate_signals()

        # Assert that the DataFrame has the correct number of rows and necessary columns
        self.assertEqual(signals.shape[0], 6)
        self.assertIn('entry', signals.columns)
        self.assertIn('exit', signals.columns)

        # Ensure that the signals are of boolean type
        self.assertTrue(signals['entry'].dtype == bool)
        self.assertTrue(signals['exit'].dtype == bool)

    @patch('vectorbt.Portfolio.from_signals')  # Mocking the backtest execution
    def test_run_backtest(self, mock_backtest):
        """
        Test the backtest execution for the SMA Crossover strategy.

        This test verifies that the strategy runs the backtest correctly and the expected metrics are calculated.
        """
        # Create test price data for the backtest
        price_data = pd.DataFrame({
            'close': [100, 105, 110, 115, 120, 125],
            'symbol': ['BTC/USD'] * 6
        })

        # Initialize the strategy with test data
        strategy = SmaCrossoverStrategy(price_data, fast_window=3, slow_window=5)

        # Mock the backtest result to return a Portfolio mock with specific stats
        mock_result = MagicMock()
        mock_result.stats.return_value = {
            'Total Return [%]': 20,
            'Sharpe Ratio': 1.5,
            'Max Drawdown [%]': -10
        }
        mock_backtest.return_value = mock_result

        # Run the backtest
        result = strategy.run_backtest()

        # Check if the backtest method was called once
        mock_backtest.assert_called_once()

        # Verify the result contains the expected metrics
        self.assertEqual(result['Total Return [%]'], 20)
        self.assertEqual(result['Sharpe Ratio'], 1.5)
        self.assertEqual(result['Max Drawdown [%]'], -10)


class TestVWAPReversionStrategy(unittest.TestCase):
    """
    Unit tests for the VWAP Reversion Strategy class.
    These tests validate the signal generation and backtesting functionality for the VWAP Reversion strategy.
    """

    @patch('vectorbt.Portfolio.from_signals')  # Mocking the backtest execution
    def test_generate_signals(self, mock_backtest):
        """
        Test the signal generation for the VWAP Reversion strategy.

        This test checks that the correct signals are generated based on the price and volume data.
        """
        # Create test price and volume data
        price_data = pd.DataFrame({
            'close': [100, 105, 110, 115, 120],
            'volume': [1000, 1200, 1300, 1400, 1500],
            'symbol': ['BTC/USD'] * 5
        })

        # Initialize the strategy
        strategy = VWAP_Reversion_Strategy(price_data, deviation_threshold=0.01)

        # Generate the signals
        signals = strategy.generate_signals()

        # Assert that the DataFrame has the correct number of rows and necessary columns
        self.assertEqual(signals.shape[0], 5)
        self.assertIn('entry', signals.columns)
        self.assertIn('exit', signals.columns)

    @patch('vectorbt.Portfolio.from_signals')  # Mocking the backtest execution
    def test_run_backtest(self, mock_backtest):
        """
        Test the backtest execution for the VWAP Reversion strategy.

        This test verifies that the strategy executes the backtest correctly and the expected metrics are calculated.
        """
        # Create test price and volume data
        price_data = pd.DataFrame({
            'close': [100, 105, 110, 115, 120],
            'volume': [1000, 1200, 1300, 1400, 1500],
            'symbol': ['BTC/USD'] * 5
        })

        # Initialize the strategy
        strategy = VWAP_Reversion_Strategy(price_data, deviation_threshold=0.01)

        # Mock the backtest result to return a Portfolio mock with specific stats
        mock_result = MagicMock()
        mock_result.stats.return_value = {
            'Total Return [%]': 15,
            'Sharpe Ratio': 1.2,
            'Max Drawdown [%]': -8
        }
        mock_backtest.return_value = mock_result

        # Run the backtest
        result = strategy.run_backtest()

        # Check if the backtest method was called once
        mock_backtest.assert_called_once()

        # Verify the result contains the expected metrics
        self.assertEqual(result['Total Return [%]'], 15)
        self.assertEqual(result['Sharpe Ratio'], 1.2)
        self.assertEqual(result['Max Drawdown [%]'], -8)


class TestRSIBollingerStrategy(unittest.TestCase):
    """
    Unit tests for the RSI with Bollinger Bands strategy.
    These tests validate the signal generation and backtesting functionality for the RSI with Bollinger Bands strategy.
    """

    @patch('vectorbt.Portfolio.from_signals')  # Mocking the backtest execution
    def test_generate_signals(self, mock_backtest):
        """
        Test the signal generation for the RSI with Bollinger Bands strategy.

        This test ensures that the entry and exit signals are correctly generated based on price data.
        """
        # Create test price data for the backtest
        price_data = pd.DataFrame({
            'close': [100, 105, 110, 115, 120],
            'symbol': ['BTC/USD'] * 5
        })

        # Initialize the strategy
        strategy = RSI_Bollinger_Strategy(price_data)

        # Generate the signals
        signals = strategy.generate_signals()

        # Assert that the DataFrame has the correct number of rows and necessary columns
        self.assertEqual(signals.shape[0], 5)
        self.assertIn('entry', signals.columns)
        self.assertIn('exit', signals.columns)

    @patch('vectorbt.Portfolio.from_signals')  # Mocking the backtest execution
    def test_run_backtest(self, mock_backtest):
        """
        Test the backtest execution for the RSI with Bollinger Bands strategy.

        This test checks that the strategy executes the backtest and calculates the expected metrics correctly.
        """
        # Create test price data for the backtest
        price_data = pd.DataFrame({
            'close': [100, 105, 110, 115, 120],
            'symbol': ['BTC/USD'] * 5
        })

        # Initialize the strategy
        strategy = RSI_Bollinger_Strategy(price_data)

        # Mock the backtest result to return a Portfolio mock with specific stats
        mock_result = MagicMock()
        mock_result.stats.return_value = {
            'Total Return [%]': 25,
            'Sharpe Ratio': 2.0,
            'Max Drawdown [%]': -5
        }
        mock_backtest.return_value = mock_result

        # Run the backtest
        result = strategy.run_backtest()

        # Check if the backtest method was called once
        mock_backtest.assert_called_once()

        # Verify the result contains the expected metrics
        self.assertEqual(result['Total Return [%]'], 25)
        self.assertEqual(result['Sharpe Ratio'], 2.0)
        self.assertEqual(result['Max Drawdown [%]'], -5)


if __name__ == '__main__':
    unittest.main()
