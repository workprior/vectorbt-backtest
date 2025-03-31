# Vectorbt-Backtest

## Description
**Vectorbt-Backtest** is a backtesting tool for testing various trading strategies on historical market data. The project includes strategies like **VWAP Reversion**, **RSI with Bollinger Bands**, and **SMA Crossover**. It automates the process of backtesting strategies, collecting performance metrics, and generating reports.

## Features
- **Flexible Number of Currency Pairs**: Easily change the number of currencies to be tested.
- **Sorting Filters**: Sort trading pairs by volume (smallest to largest or reverse).
- **Multiple Strategies**: Backtest multiple strategies (VWAP Reversion, RSI with Bollinger Bands, and SMA Crossover).
- **Performance Reports**: Generate HTML performance reports and graphs for easy analysis.

## Installation

### Step 1: Clone the Repository
Clone the repository to your local machine:\

```bash
git clone https://github.com/workprior/vectorbt-backtest.git
cd vectorbt-backtest
```

### Step 2: Install Dependencies with pip
If you are using pip (without Poetry), follow these steps to install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration and Customization
### 1. Change the Number of Currencies to Test
In the main.py file, you can customize the number of currencies (symbols) that the backtester will process. Update the load_or_get_data() function call to adjust the number of currencies:

```bash
df = loader.load_or_get_data(num_symbols=20)  # Change 20 to your preferred number
```

### 2. Change Sorting Filters
You can adjust the sorting filter for the currencies by modifying the code where the data is loaded or processed. For example, if you want to filter by volume, you can modify the DataFrame sorting:

```bash
df = loader.load_or_get_data(reverse=True)  # Change the column name and sorting order as needed

```

## Running the Project
### Step 1: Run Backtests for All Strategies
To run the backtests for all the strategies, simply run the following command:

```bash
python main.py
```
This command will:

Load historical data for the specified number of currency pairs.

Run backtests for each strategy (VWAP Reversion, RSI with Bollinger Bands, SMA Crossover).

Generate performance metrics and save them as HTML reports in the results/statistic directory.

### Step 2: Check Results
After running the backtests, you can find the following results:

Performance Metrics: These are saved in CSV format in the results/ directory.

Equity Curves: Graphs of the equity curve for each strategy will be saved as PNG files in the screenshots/ directory.

## Running Tests
To run the unit tests, you can use:
```bash
python -m unittest .\tests\test_strategies.py
```

### Writing Your Own Tests
If you want to add more tests, simply create a new Python file in the tests/ directory, following the existing test structure, and run them using the above command.

## Documentation and Support
If you have any questions or need further assistance, feel free to open an issue on the repository or contact us at [lolprior.201@gmail.com].