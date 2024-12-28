import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from io import BytesIO


matplotlib.use('Agg')  # Use a non-interactive backend




def plot_price_to_sales(ax, data, highlight_ticker):
    tickers = [item['Ticker'] for item in data if item.get('ps') is not None]
    ps_values = [item['ps'] for item in data if item.get('ps') is not None]
    
    # Define bar colors
    colors = ['green' if ticker == highlight_ticker else 'skyblue' for ticker in tickers]
    
    # Plotting on the given axis
    bars = ax.bar(tickers, ps_values, color=colors)
    
    # Add labels and title
    ax.set_xlabel('Tickers')
    ax.set_ylabel('Price-to-Sales Ratio')
    ax.set_title('Price-to-Sales Ratios of Companies')
    
    # Add data labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom')

def plot_revenue_growth(ax, data, highlight_ticker):
    filtered_data = [item for item in data if item.get('1YearGrowth') is not None and item.get('3YearGrowth') is not None]
    
    # Extract data for plotting
    tickers = [item['Ticker'] for item in filtered_data]
    one_year_growth = [item['1YearGrowth'] for item in filtered_data]
    three_year_growth = [item['3YearGrowth'] for item in filtered_data]
    
    # Define colors for bars
    colors_one_year = ['lightgreen' if ticker == highlight_ticker else 'skyblue' for ticker in tickers]
    colors_three_year = ['green' if ticker == highlight_ticker else 'blue' for ticker in tickers]
    
    # Create a grouped bar chart
    x = np.arange(len(tickers))  # X-axis positions
    width = 0.35  # Bar width
    
    bars1 = ax.bar(x - width / 2, one_year_growth, width, label='1-Year Growth', color=colors_one_year)
    bars2 = ax.bar(x + width / 2, three_year_growth, width, label='3-Year Growth', color=colors_three_year)
    
    # Add labels, title, and legend
    ax.set_xlabel('Tickers')
    ax.set_ylabel('Revenue Growth (%)')
    ax.set_title('1-Year and 3-Year Revenue Growth by Company')
    ax.set_xticks(x)
    ax.set_xticklabels(tickers)
    ax.legend()
    
    # Add data labels on bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}%', ha='center', va='bottom')
    
    add_labels(bars1)
    add_labels(bars2)


def plot_operating_margins(ax, data, highlight_ticker):
    filtered_data = [item for item in data if item.get('operating_margins') is not None]
    
    # Extract tickers and operating margins
    tickers = [item['Ticker'] for item in filtered_data]
    margins = [item['operating_margins'] for item in filtered_data]
    
    # Define bar colors
    colors = ['green' if ticker == highlight_ticker else 'skyblue' for ticker in tickers]
    
    # Plotting on the given axis
    bars = ax.bar(tickers, margins, color=colors)
    
    # Customize x-axis labels
    ax.set_xticks(range(len(tickers)))
    ax.set_xticklabels([f"{ticker}\n{margin:.2f}%" for ticker, margin in zip(tickers, margins)], rotation=0)
    
    # Labels and title
    ax.set_xlabel('Tickers and Operating Margins')
    ax.set_ylabel('Operating Margin (%)')
    ax.set_title('Operating Margins of Companies')

import matplotlib.pyplot as plt

def plot_rev(ax, data, highlight):
    def readable(i):
        """Convert large numbers to human-readable format."""
        if i >= 1e12:
            return f"{round(i / 1e12, 1)}T"
        elif i >= 1e9:
            return f"{round(i / 1e9, 1)}B"
        elif i >= 1e6:
            return f"{round(i / 1e6, 1)}M"
        elif i >= 1e3:
            return f"{round(i / 1e3, 1)}k"
        else:
            return str(i)

    # Filter out data without revenue and process values
    clean = [item for item in data if item.get('revenue') is not None]
    tickers = [item['Ticker'] for item in clean]
    readable_revs = [readable(item['revenue']) for item in clean]
    revs = [item['revenue'] for item in clean]
    colors = ['green' if highlight == item['Ticker'] else 'skyblue' for item in clean]

    # Plot the bar chart
    ax.bar(tickers, revs, color=colors)

    # Update x-axis labels
    ax.set_xticks(range(len(tickers)))
    ax.set_xticklabels(
        [f"{ticker}\n{rev}" for ticker, rev in zip(tickers, readable_revs)],
        rotation=0
    )

    # Add labels and title
    ax.set_xlabel('Companies and Revenues', fontsize=10)
    ax.set_ylabel('Revenues (USD)', fontsize=10)
    ax.set_title('Company Revenues', fontsize=12)

    # Show grid for better readability (optional)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout
    plt.tight_layout()



def plot_combined(data, highlight_ticker):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))  # Create a 2x2 grid of subplots

    # Generate each plot on its respective subplot
    plot_price_to_sales(axs[0, 0], data, highlight_ticker)  # Top-left
    plot_revenue_growth(axs[0, 1], data, highlight_ticker)  # Top-right
    plot_operating_margins(axs[1, 0], data, highlight_ticker)  # Bottom-left
    plot_rev(axs[1, 1], data, highlight_ticker)  # Bottom-left
    # Adjust layout to prevent overlap
    plt.tight_layout()