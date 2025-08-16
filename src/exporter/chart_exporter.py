import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import numpy as np

class ChartExporter:
    """Export data as charts/visualizations."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def export(self, results: Dict[str, Dict[str, Any]], horizon: str) -> None:
        """
        Export results as charts.
        
        Args:
            results: Dictionary containing coin data and metadata
            horizon: Time horizon (e.g., 'intraday', 'swing')
        """
        
        # Create horizon-specific directory
        horizon_dir = self.output_dir / horizon / "charts"
        horizon_dir.mkdir(parents=True, exist_ok=True)
        
        # Export individual coin charts
        for coin, data in results.items():
            self._export_coin_chart(coin, data, horizon_dir)
        
        # Export comparison chart if multiple coins
        if len(results) > 1:
            self._export_comparison_chart(results, horizon, horizon_dir)
    
    def _export_coin_chart(self, coin: str, data: Dict[str, Any], output_dir: Path) -> None:
        """Export comprehensive chart for a single coin."""
        
        df = data['data']
        metadata = data['metadata']
        
        if df.empty:
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
        fig.suptitle(f'{coin.upper()} - {metadata["granularity"]} - Technical Analysis', fontsize=16, fontweight='bold')
        
        # Subplot 1: Price and Moving Averages
        self._plot_price_and_mas(axes[0], df, coin)
        
        # Subplot 2: RSI
        self._plot_rsi(axes[1], df)
        
        # Subplot 3: MACD
        self._plot_macd(axes[2], df)
        
        # Format x-axis
        axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        axes[2].xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save chart
        filename = f"{coin}_{metadata['granularity']}_chart.png"
        filepath = output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_price_and_mas(self, ax, df: pd.DataFrame, coin: str) -> None:
        """Plot price with moving averages and Bollinger Bands."""
        
        # Plot candlestick-style price
        ax.plot(df.index, df['close'], label='Close Price', linewidth=1.5, color='black')
        
        # Plot moving averages
        if 'ema_20' in df.columns:
            ax.plot(df.index, df['ema_20'], label='EMA 20', alpha=0.8, linewidth=1)
        if 'ema_50' in df.columns:
            ax.plot(df.index, df['ema_50'], label='EMA 50', alpha=0.8, linewidth=1)
        if 'ema_200' in df.columns:
            ax.plot(df.index, df['ema_200'], label='EMA 200', alpha=0.8, linewidth=1)
        
        # Plot Bollinger Bands
        if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'bb_middle']):
            ax.plot(df.index, df['bb_upper'], label='BB Upper', alpha=0.6, linestyle='--')
            ax.plot(df.index, df['bb_lower'], label='BB Lower', alpha=0.6, linestyle='--')
            ax.fill_between(df.index, df['bb_upper'], df['bb_lower'], alpha=0.1, color='gray')
        
        ax.set_title(f'{coin.upper()} Price with Technical Indicators')
        ax.set_ylabel('Price (USD)')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
    
    def _plot_rsi(self, ax, df: pd.DataFrame) -> None:
        """Plot RSI indicator."""
        
        if 'rsi_14' not in df.columns:
            ax.text(0.5, 0.5, 'RSI data not available', transform=ax.transAxes, 
                   ha='center', va='center', fontsize=12)
            ax.set_title('RSI (14)')
            return
        
        ax.plot(df.index, df['rsi_14'], label='RSI (14)', color='purple', linewidth=1.5)
        
        # Add overbought/oversold lines
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax.axhline(y=50, color='blue', linestyle='-', alpha=0.5, label='Midline (50)')
        
        # Fill overbought/oversold areas
        ax.fill_between(df.index, 70, 100, alpha=0.1, color='red')
        ax.fill_between(df.index, 0, 30, alpha=0.1, color='green')
        
        ax.set_title('RSI (14)')
        ax.set_ylabel('RSI')
        ax.set_ylim(0, 100)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
    
    def _plot_macd(self, ax, df: pd.DataFrame) -> None:
        """Plot MACD indicator."""
        
        if not all(col in df.columns for col in ['macd', 'macd_signal', 'macd_histogram']):
            ax.text(0.5, 0.5, 'MACD data not available', transform=ax.transAxes, 
                   ha='center', va='center', fontsize=12)
            ax.set_title('MACD (12,26,9)')
            return
        
        # Plot MACD lines
        ax.plot(df.index, df['macd'], label='MACD', color='blue', linewidth=1.5)
        ax.plot(df.index, df['macd_signal'], label='Signal', color='red', linewidth=1.5)
        
        # Plot histogram
        colors = ['green' if x >= 0 else 'red' for x in df['macd_histogram']]
        ax.bar(df.index, df['macd_histogram'], label='Histogram', alpha=0.6, 
               color=colors, width=0.8)
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        ax.set_title('MACD (12,26,9)')
        ax.set_ylabel('MACD')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
    
    def _export_comparison_chart(self, results: Dict[str, Dict[str, Any]], horizon: str, output_dir: Path) -> None:
        """Export comparison chart for multiple coins."""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Multi-Coin Comparison - {horizon.title()}', fontsize=16, fontweight='bold')
        
        # Normalize prices for comparison (percentage change from first value)
        normalized_prices = {}
        rsi_data = {}
        volume_data = {}
        
        for coin, data in results.items():
            df = data['data']
            if df.empty:
                continue
            
            # Normalize prices to percentage change
            first_price = df['close'].iloc[0]
            normalized_prices[coin] = ((df['close'] / first_price) - 1) * 100
            
            # Collect RSI data
            if 'rsi_14' in df.columns:
                rsi_data[coin] = df['rsi_14']
            
            # Collect volume data
            volume_data[coin] = df['volume']
        
        # Plot 1: Normalized price comparison
        ax1 = axes[0, 0]
        for coin, prices in normalized_prices.items():
            ax1.plot(prices.index, prices, label=coin.upper(), linewidth=1.5)
        ax1.set_title('Price Performance Comparison (%)')
        ax1.set_ylabel('Price Change (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: RSI comparison
        ax2 = axes[0, 1]
        for coin, rsi in rsi_data.items():
            ax2.plot(rsi.index, rsi, label=coin.upper(), alpha=0.8)
        ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5)
        ax2.set_title('RSI Comparison')
        ax2.set_ylabel('RSI')
        ax2.set_ylim(0, 100)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Volume comparison (normalized)
        ax3 = axes[1, 0]
        for coin, volume in volume_data.items():
            # Normalize volume to show relative changes
            normalized_volume = volume / volume.mean()
            ax3.plot(volume.index, normalized_volume, label=coin.upper(), alpha=0.8)
        ax3.set_title('Relative Volume Comparison')
        ax3.set_ylabel('Volume (Normalized)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Latest values summary
        ax4 = axes[1, 1]
        self._plot_latest_summary(ax4, results)
        
        # Format dates
        for ax in axes.flat:
            if hasattr(ax, 'xaxis'):
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save comparison chart
        filename = f"comparison_{horizon}.png"
        filepath = output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_latest_summary(self, ax, results: Dict[str, Dict[str, Any]]) -> None:
        """Plot summary of latest indicator values."""
        
        summary_data = []
        coins = []
        
        for coin, data in results.items():
            df = data['data']
            if df.empty:
                continue
            
            latest = df.iloc[-1]
            coins.append(coin.upper())
            
            row_data = []
            if 'rsi_14' in df.columns and pd.notna(latest['rsi_14']):
                row_data.append(float(latest['rsi_14']))
            else:
                row_data.append(0)
            
            if 'bb_percent_b' in df.columns and pd.notna(latest['bb_percent_b']):
                row_data.append(float(latest['bb_percent_b']) * 100)  # Convert to percentage
            else:
                row_data.append(0)
            
            if 'adx_14' in df.columns and pd.notna(latest['adx_14']):
                row_data.append(float(latest['adx_14']))
            else:
                row_data.append(0)
            
            summary_data.append(row_data)
        
        if not summary_data:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes, 
                   ha='center', va='center', fontsize=12)
            ax.set_title('Latest Indicator Values')
            return
        
        # Create heatmap
        import numpy as np
        summary_array = np.array(summary_data)
        
        im = ax.imshow(summary_array.T, cmap='RdYlGn_r', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(coins)))
        ax.set_xticklabels(coins)
        ax.set_yticks(range(3))
        ax.set_yticklabels(['RSI', 'BB %B', 'ADX'])
        
        # Add text annotations
        for i in range(len(coins)):
            for j in range(3):
                if j < summary_array.shape[1]:
                    text = ax.text(i, j, f'{summary_array[i, j]:.1f}',
                                 ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_title('Latest Indicator Values')
        plt.colorbar(im, ax=ax, shrink=0.6)