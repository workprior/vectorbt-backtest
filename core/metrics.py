import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class MetricsStatistics:
    def __init__(self, metrics_path='results/', statistic_path='results/statistic/'):
        """
        Ініціалізація класу Metrics.

        :param strategy: Стратегія, для якої будемо збирати метрики.
        :param results_path: Шлях до директорії, де зберігатимуться результати.
        """
        self.metrics_path = metrics_path
        self.statistic_path = statistic_path
        os.makedirs(self.metrics_path, exist_ok=True)
        os.makedirs(self.statistic_path, exist_ok=True)
  
        self.symbols= []
        self.strategies = []

    def load_all_metrics(self):
        """
        Завантаження всіх CSV файлів з папки для подальшого аналізу.
        Об'єднує всі файли в один DataFrame.
        """
        all_metrics = []  # Список для зберігання всіх DataFrame

        # Перевіряємо всі файли в папці 'results'
        for file_name in os.listdir(self.metrics_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(self.metrics_path, file_name)
                
                # Завантажуємо CSV файл в DataFrame
                df = pd.read_csv(file_path)
                
                # Додаємо DataFrame в список
                all_metrics.append(df)
        
        # Об'єднуємо всі DataFrame в один
        combined_metrics = pd.concat(all_metrics, ignore_index=True)
    
        return combined_metrics
    

    def plot_equity_curve(self, metrics_df):
        """
        Побудова та збереження equity curve для всіх стратегій та пар.
        """
        # Створюємо порожній графік
        fig = go.Figure()

        # Обробляємо кожну стратегію
        for strategy_name in metrics_df['strategy_name'].unique():
            strategy_data = metrics_df[metrics_df['strategy_name'] == strategy_name]

            # Перевіряємо наявність необхідних колонок для побудови equity curve
            if 'Total Return [%]' not in strategy_data.columns:
                print(f"Warning: 'Total Return [%]' not found for strategy {strategy_name}")
                continue

            # Побудова equity curve для стратегії
            fig.add_trace(go.Scatter(
                x=strategy_data['symbol'],  # Для осі X використовуємо символи пар
                y=strategy_data['Total Return [%]'],  # Для осі Y використовуємо Total Return
                mode='lines', 
                name=f"{strategy_name} Equity Curve"
            ))

        # Оновлюємо макет графіка
        fig.update_layout(
            title="Equity Curve for All Strategies",
            xaxis_title="Symbol",
            yaxis_title="Total Return [%]",
            showlegend=True
        )

        # Збереження графіка у файл
        fig.write_image(os.path.join(self.statistic_path, "equity_curve_all_strategies.png"))
        fig.show()
    
    def plot_heatmap(self, metrics_df):
        """
        Створення та збереження heatmap для performance по всіх парах та стратегіях.
        """
        # Перевірка, чи є необхідні колонки для побудови теплової карти
        if 'Total Return [%]' not in metrics_df.columns:
            print("Error: 'Total Return [%]' not found in data.")
            return

        # Формуємо таблицю для heatmap
        heatmap_data = metrics_df.pivot(index='symbol', columns='strategy_name', values='Total Return [%]')

        # Створюємо теплову карту за допомогою plotly.express
        fig = px.imshow(heatmap_data, 
                        labels={'x': "Strategy", 'y': "Symbol"}, 
                        title="Performance Heatmap for All Strategies and Pairs")

        # Оновлюємо макет графіка
        fig.update_layout(
            width=1200,
            height=800,
            xaxis={'side': 'top'},  # Розміщуємо стратегії зверху
            coloraxis_colorbar=dict(title="Total Return [%]")  # Легенда для кольору
        )

        # Збереження heatmap
        fig.write_image(os.path.join(self.statistic_path, "performance_heatmap.png"))
        fig.show()
    
    def compare_metrics(self, metrics_df):
        """
        Порівняння метрик по стратегіях (побудова графіків).
        """
        fig = go.Figure()

        for strategy_name in metrics_df['strategy_name'].unique():
            strategy_data = metrics_df[metrics_df['strategy_name'] == strategy_name]
            fig.add_trace(go.Bar(
                x=strategy_data['symbol'],
                y=strategy_data['Total Return'],
                name=f"Strategy: {strategy_name}"
            ))

        fig.update_layout(
            title="Comparison of Strategies",
            xaxis_title="Symbol",
            yaxis_title="Total Return",
            barmode='group'
        )

        # Збереження порівняння
        fig.write_image(os.path.join(self.screenshots_path, f"{self.symbol}_{self.strategy_name}_comparison.png"))
        fig.show()
    
    def generate_html_report(self):
        """
        Генерація HTML звіту з інтерактивними графіками.
        """
        html_file = os.path.join(self.results_path, f"{self.symbol}_{self.strategy_name}_report.html")

        # Збереження графіків як HTML файлів
        fig_equity = go.Figure(data=[go.Scatter(
            x=self.strategy.result.equity_curve().index,
            y=self.strategy.result.equity_curve().values,
            mode='lines',
            name='Equity Curve'
        )])
        
        fig_equity.write_html(html_file, full_html=True)
        
        return html_file
