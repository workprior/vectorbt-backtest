import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class MetricsStatistics:
    def __init__(self, metrics_path='results/', statistic_path='results/statistic/'):
        """
        Initializes the MetricsStatistics class for collecting and visualizing metrics.

        :param metrics_path: Path to the directory where CSV metric files are stored.
        :param statistic_path: Path to the directory where visualization results will be saved.
        """
        self.metrics_path = metrics_path
        self.statistic_path = statistic_path
        os.makedirs(self.metrics_path, exist_ok=True)
        os.makedirs(self.statistic_path, exist_ok=True)

        self.symbols = []
        self.strategies = []

    def load_all_metrics(self):
        """
        Loads all CSV files containing metrics from the `metrics_path` directory, 
        and combines them into a single DataFrame.

        :return: A pandas DataFrame containing all the combined metrics.
        """
        all_metrics = []  # List to store all DataFrames

        # Loop through all files in the metrics directory
        for file_name in os.listdir(self.metrics_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(self.metrics_path, file_name)

                # Load CSV file into DataFrame
                df = pd.read_csv(file_path)

                # Append the DataFrame to the list
                all_metrics.append(df)

        # Combine all DataFrames into one
        combined_metrics = pd.concat(all_metrics, ignore_index=True)

        return combined_metrics

    def plot_equity_curve(self, metrics_df):
        """
        Builds and saves the equity curve for all strategies and pairs.

        :param metrics_df: A DataFrame containing the metrics to plot.
        :return: HTML representation of the equity curve plot.
        """
        fig = go.Figure()

        # Process each strategy
        for strategy_name in metrics_df['strategy_name'].unique():
            strategy_data = metrics_df[metrics_df['strategy_name'] == strategy_name]

            # Check if the necessary column is present
            if 'Total Return [%]' not in strategy_data.columns:
                print(f"Warning: 'Total Return [%]' not found for strategy {strategy_name}")
                continue

            # Add trace for equity curve of each strategy
            fig.add_trace(go.Scatter(
                x=strategy_data['symbol'],
                y=strategy_data['Total Return [%]'],
                mode='lines',
                name=f"{strategy_name} Equity Curve"
            ))

        # Update layout for the plot
        fig.update_layout(
            title="Equity Curve for All Strategies",
            xaxis_title="Symbol",
            yaxis_title="Total Return [%]",
            showlegend=True
        )

        # Save the plot to a file
        fig.write_image(os.path.join(self.statistic_path, "equity_curve_all_strategies.png"))
        return fig.to_html(full_html=False)

    def plot_heatmap(self, metrics_df):
        """
        Creates and saves a heatmap for the performance of all pairs and strategies.

        :param metrics_df: A DataFrame containing the metrics to plot.
        :return: HTML representation of the heatmap plot.
        """
        # Check if necessary column is present for creating the heatmap
        if 'Total Return [%]' not in metrics_df.columns:
            print("Error: 'Total Return [%]' not found in data.")
            return

        # Create the heatmap data pivot table
        heatmap_data = metrics_df.pivot(index='symbol', columns='strategy_name', values='Win Rate [%]')

        # Create heatmap using plotly.express
        fig = px.imshow(heatmap_data,
                        labels={'x': "Strategy", 'y': "Symbol"},
                        title="Performance Heatmap for All Strategies and Pairs")

        # Update layout for the heatmap
        fig.update_layout(
            width=1200,
            height=800,
            xaxis={'side': 'top'},  # Place strategies at the top
            coloraxis_colorbar=dict(title="Win Rate [%]")  # Color bar legend
        )

        # Save the heatmap
        fig.write_image(os.path.join(self.statistic_path, "performance_heatmap.png"))
        return fig.to_html(full_html=False)

    def plot_metrics_comparison(self, metrics_df):
        """
        Builds and saves comparison plots for various metrics, such as Sharpe Ratio, Max Drawdown, 
        Expectancy, and Exposure Time for all strategies and pairs.

        :param metrics_df: A DataFrame containing the metrics to plot.
        :return: HTML content with the comparison plots.
        """
        metrics = ['Sharpe Ratio', 'Max Drawdown [%]', 'Expectancy', 'Exposure Time [%]']
        html_content = ""

        # Loop through each metric
        for metric in metrics:
            # Check if the metric is available in the data
            if metric not in metrics_df.columns:
                print(f"Warning: '{metric}' not found in data.")
                continue

            fig = go.Figure()

            # Loop through each strategy
            for strategy_name in metrics_df['strategy_name'].unique():
                strategy_data = metrics_df[metrics_df['strategy_name'] == strategy_name]

                # Add trace for each strategy and its metric
                fig.add_trace(go.Scatter(
                    x=strategy_data['symbol'],
                    y=strategy_data[metric],
                    mode='lines',
                    name=f"{strategy_name} {metric}"
                ))

            # Update layout for the plot
            fig.update_layout(
                title=f"{metric} for All Strategies",
                xaxis_title="Symbol",
                yaxis_title=metric,
                showlegend=True
            )

            # Save the plot and append to HTML content
            fig.write_image(os.path.join(self.statistic_path, f"{metric}_all_strategies.png"))
            html_content += f"<h3>{metric}</h3>{fig.to_html(full_html=False)}<br>"

        return html_content

    def generate_html_report(self, metrics_df):
        """
        Generates an HTML report with interactive graphs for all metrics.

        :param metrics_df: A DataFrame containing the metrics to include in the report.
        :return: Path to the generated HTML report.
        """
        html_content = ""

        # Add equity curve plot
        html_content += "<h2>Equity Curve</h2>"
        html_content += self.plot_equity_curve(metrics_df)

        # Add heatmap
        html_content += "<h2>Performance Heatmap</h2>"
        html_content += self.plot_heatmap(metrics_df)

        # Add metrics comparison
        html_content += "<h2>Metrics Comparison</h2>"
        html_content += self.plot_metrics_comparison(metrics_df)

        # Save the HTML report
        report_file = os.path.join(self.statistic_path, "metrics_report.html")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML report generated: {report_file}")
        return report_file
