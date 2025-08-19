import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class GlobalExporter:
    """Export global market data to JSON format."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, global_data: Dict[str, Any]) -> None:
        """
        Export global cryptocurrency market data to JSON file.
        
        Args:
            global_data: Raw global data from CoinGecko API
        """
        
        # Process and structure global data
        processed_global = self._process_global_data(global_data)
        
        # Export to JSON
        global_file = self.output_dir / "global.json"
        
        with open(global_file, 'w') as f:
            json.dump(processed_global, f, indent=2, default=str)
    
    def _process_global_data(self, global_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw global data into structured format."""
        
        data = global_data.get('data', {})
        
        processed = {
            'export_timestamp': datetime.now().isoformat(),
            'market_overview': {
                'total_market_cap_usd': data.get('total_market_cap', {}).get('usd'),
                'total_volume_24h_usd': data.get('total_volume', {}).get('usd'),
                'bitcoin_dominance_percentage': data.get('market_cap_percentage', {}).get('btc'),
                'ethereum_dominance_percentage': data.get('market_cap_percentage', {}).get('eth'),
                'active_cryptocurrencies': data.get('active_cryptocurrencies'),
                'upcoming_icos': data.get('upcoming_icos'),
                'ongoing_icos': data.get('ongoing_icos'),
                'ended_icos': data.get('ended_icos'),
                'markets': data.get('markets')
            },
            'market_cap_change_24h': {
                'percentage': data.get('market_cap_change_percentage_24h_usd'),
                'trend': self._determine_trend(data.get('market_cap_change_percentage_24h_usd', 0))
            },
            'dominance_analysis': self._analyze_dominance(data.get('market_cap_percentage', {})),
            'volume_analysis': self._analyze_volume(data),
            'market_sentiment': self._analyze_market_sentiment(data),
            'defi_metrics': self._extract_defi_metrics(data),
            'raw_data': data  # Keep raw data for advanced analysis
        }
        
        return processed
    
    def _determine_trend(self, change_percentage: float) -> str:
        """Determine market trend based on percentage change."""
        
        if change_percentage > 5:
            return 'strong_bullish'
        elif change_percentage > 2:
            return 'bullish'
        elif change_percentage > 0:
            return 'slightly_bullish'
        elif change_percentage > -2:
            return 'slightly_bearish'
        elif change_percentage > -5:
            return 'bearish'
        else:
            return 'strong_bearish'
    
    def _analyze_dominance(self, market_cap_percentages: Dict[str, float]) -> Dict[str, Any]:
        """Analyze cryptocurrency dominance patterns."""
        
        btc_dominance = market_cap_percentages.get('btc', 0)
        eth_dominance = market_cap_percentages.get('eth', 0)
        
        # Calculate altcoin dominance
        altcoin_dominance = 100 - btc_dominance - eth_dominance
        
        analysis = {
            'bitcoin_dominance': btc_dominance,
            'ethereum_dominance': eth_dominance,
            'altcoin_dominance': altcoin_dominance,
            'dominance_signals': []
        }
        
        # Generate dominance signals
        if btc_dominance > 50:
            analysis['dominance_signals'].append({
                'type': 'btc_dominance_high',
                'description': f'Bitcoin dominance at {btc_dominance:.1f}% suggests market seeking safety',
                'implication': 'bearish_for_alts'
            })
        elif btc_dominance < 40:
            analysis['dominance_signals'].append({
                'type': 'btc_dominance_low',
                'description': f'Bitcoin dominance at {btc_dominance:.1f}% suggests alt season potential',
                'implication': 'bullish_for_alts'
            })
        
        if eth_dominance > 20:
            analysis['dominance_signals'].append({
                'type': 'eth_dominance_high',
                'description': f'Ethereum dominance at {eth_dominance:.1f}% shows strong DeFi/smart contract activity',
                'implication': 'bullish_for_defi'
            })
        
        if altcoin_dominance > 40:
            analysis['dominance_signals'].append({
                'type': 'alt_season_signal',
                'description': f'Altcoin dominance at {altcoin_dominance:.1f}% suggests active alt season',
                'implication': 'bullish_for_alts'
            })
        
        return analysis
    
    def _analyze_volume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trading volume patterns."""
        
        total_volume = data.get('total_volume', {}).get('usd', 0)
        total_market_cap = data.get('total_market_cap', {}).get('usd', 0)
        
        volume_analysis = {
            'total_volume_24h_usd': total_volume,
            'volume_to_market_cap_ratio': 0,
            'volume_signals': []
        }
        
        if total_market_cap > 0:
            volume_ratio = total_volume / total_market_cap
            volume_analysis['volume_to_market_cap_ratio'] = volume_ratio
            
            # Generate volume signals
            if volume_ratio > 0.15:
                volume_analysis['volume_signals'].append({
                    'type': 'high_volume',
                    'description': f'Volume-to-market-cap ratio at {volume_ratio:.3f} indicates high trading activity',
                    'implication': 'high_volatility_expected'
                })
            elif volume_ratio < 0.05:
                volume_analysis['volume_signals'].append({
                    'type': 'low_volume',
                    'description': f'Volume-to-market-cap ratio at {volume_ratio:.3f} indicates low trading activity',
                    'implication': 'low_volatility_consolidation'
                })
        
        return volume_analysis
    
    def _analyze_market_sentiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall market sentiment indicators."""
        
        market_cap_change = data.get('market_cap_change_percentage_24h_usd', 0)
        active_cryptos = data.get('active_cryptocurrencies', 0)
        markets = data.get('markets', 0)
        
        sentiment = {
            'overall_trend': self._determine_trend(market_cap_change),
            'market_cap_change_24h': market_cap_change,
            'market_maturity_indicators': {
                'active_cryptocurrencies': active_cryptos,
                'total_markets': markets,
                'market_diversity_score': min(active_cryptos / 10000, 1.0) if active_cryptos else 0
            },
            'sentiment_signals': []
        }
        
        # Generate sentiment signals based on various factors
        if market_cap_change > 10:
            sentiment['sentiment_signals'].append({
                'type': 'euphoria',
                'description': f'Market cap increased {market_cap_change:.1f}% in 24h - potential euphoria phase',
                'risk_level': 'high'
            })
        elif market_cap_change < -10:
            sentiment['sentiment_signals'].append({
                'type': 'panic',
                'description': f'Market cap decreased {market_cap_change:.1f}% in 24h - potential panic selling',
                'opportunity_level': 'high'
            })
        
        return sentiment
    
    def _extract_defi_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract DeFi-related metrics from global data."""
        
        # Note: CoinGecko's global endpoint might not have specific DeFi metrics
        # This is a placeholder for when such data becomes available
        
        defi_metrics = {
            'note': 'DeFi-specific metrics may require additional API endpoints',
            'estimated_defi_tvl': None,  # Would need DeFiPulse or similar API
            'defi_token_market_cap': None,  # Could be calculated from categories
            'defi_dominance': None
        }
        
        # If we have market cap percentages for DeFi tokens, we could estimate
        # For now, this is a placeholder for future enhancement
        
        return defi_metrics