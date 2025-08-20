import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import os

class MarketContextExporter:
    """Export all market intelligence data into a single aggregated market_context.json file."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_aggregated_market_context(self, coins: List[str]) -> None:
        """
        Aggregate all market intelligence files into a single market_context.json.
        
        Args:
            coins: List of coins being tracked
        """
        
        market_context = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'coins_tracked': coins,
                'total_coins': len(coins),
                'data_sources': [],
                'note': 'News data not available via CoinGecko Pro API'
            },
            'global_market': {},
            'sector_analysis': {},
            'coin_fundamentals': {},
            'liquidity_analysis': {},
            'onchain_data': {}
        }
        
        # News data collection disabled for CoinGecko (API limitation)
        # News aggregation skipped - CoinGecko Pro API does not provide reliable news endpoints
        
        # Aggregate global market data
        global_file = self.output_dir / 'global.json'
        if global_file.exists():
            try:
                with open(global_file, 'r') as f:
                    global_data = json.load(f)
                market_context['global_market'] = global_data
                market_context['metadata']['data_sources'].append('global_market')
            except Exception as e:
                market_context['global_market'] = {'error': f'Failed to load global data: {str(e)}'}
        
        # Aggregate categories/sector data
        categories_file = self.output_dir / 'categories.json'
        if categories_file.exists():
            try:
                with open(categories_file, 'r') as f:
                    categories_data = json.load(f)
                market_context['sector_analysis'] = categories_data
                market_context['metadata']['data_sources'].append('sector_analysis')
            except Exception as e:
                market_context['sector_analysis'] = {'error': f'Failed to load categories data: {str(e)}'}
        
        # Aggregate metadata/fundamentals
        metadata_file = self.output_dir / 'metadata.json'
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                market_context['coin_fundamentals'] = metadata_data
                market_context['metadata']['data_sources'].append('coin_fundamentals')
            except Exception as e:
                market_context['coin_fundamentals'] = {'error': f'Failed to load metadata: {str(e)}'}
        
        # Aggregate tickers/liquidity data
        tickers_file = self.output_dir / 'tickers.json'
        if tickers_file.exists():
            try:
                with open(tickers_file, 'r') as f:
                    tickers_data = json.load(f)
                market_context['liquidity_analysis'] = tickers_data
                market_context['metadata']['data_sources'].append('liquidity_analysis')
            except Exception as e:
                market_context['liquidity_analysis'] = {'error': f'Failed to load tickers data: {str(e)}'}
        
        # Add comprehensive market summary
        market_context['market_summary'] = self._generate_market_summary(market_context)
        
        # Write aggregated market context file
        context_file = self.output_dir / 'market_context.json'
        with open(context_file, 'w') as f:
            json.dump(market_context, f, indent=2, default=str)
    
    def _generate_market_summary(self, market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive market summary from all available data sources."""
        
        summary = {
            'data_completeness': {
                'available_sources': len(market_context['metadata']['data_sources']),
                'missing_sources': []
            },
            'key_insights': [],
            'market_sentiment': 'neutral',
            'risk_factors': [],
            'opportunities': []
        }
        
        # Check data completeness (news excluded due to CoinGecko API limitation)
        expected_sources = ['global_market', 'sector_analysis', 'coin_fundamentals', 'liquidity_analysis']
        available_sources = market_context['metadata']['data_sources']
        
        for source in expected_sources:
            if source not in available_sources:
                summary['data_completeness']['missing_sources'].append(source)
        
        # Extract key insights from global market data
        if 'global_market' in market_context and 'market_overview' in market_context['global_market']:
            global_data = market_context['global_market']['market_overview']
            
            if 'bitcoin_dominance_percentage' in global_data:
                btc_dom = global_data['bitcoin_dominance_percentage']
                if btc_dom > 50:
                    summary['key_insights'].append(f"Bitcoin dominance at {btc_dom:.1f}% suggests market flight to safety")
                    summary['market_sentiment'] = 'risk_off'
                else:
                    summary['key_insights'].append(f"Bitcoin dominance at {btc_dom:.1f}% suggests healthy altcoin activity")
                    summary['market_sentiment'] = 'risk_on'
        
        # News sentiment analysis disabled (CoinGecko API limitation)
        # Consider integrating alternative news sources like NewsAPI, Alpha Vantage, or Polygon.io
        
        # Extract sector insights
        if 'sector_analysis' in market_context and 'sector_analysis' in market_context['sector_analysis']:
            sector_data = market_context['sector_analysis']['sector_analysis']
            
            if 'top_performers_24h' in sector_data:
                top_sectors = sector_data['top_performers_24h'][:3]
                for sector in top_sectors:
                    if 'name' in sector and 'market_cap_change_24h' in sector:
                        summary['key_insights'].append(
                            f"Strong sector: {sector['name']} (+{sector['market_cap_change_24h']:.1f}%)"
                        )
        
        return summary