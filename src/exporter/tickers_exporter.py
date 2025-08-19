import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class TickersExporter:
    """Export tickers and exchange data to JSON format."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, tickers_by_coin: Dict[str, Dict[str, Any]]) -> None:
        """
        Export tickers/exchange data for all coins to JSON file.
        
        Args:
            tickers_by_coin: Dictionary mapping coin_id to tickers data
        """
        
        # Process and structure tickers data
        processed_tickers = self._process_tickers_data(tickers_by_coin)
        
        # Export to JSON
        tickers_file = self.output_dir / "tickers.json"
        
        with open(tickers_file, 'w') as f:
            json.dump(processed_tickers, f, indent=2, default=str)
    
    def _process_tickers_data(self, tickers_by_coin: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Process raw tickers data into structured format."""
        
        processed = {
            'export_timestamp': datetime.now().isoformat(),
            'exchange_analysis': {
                'total_exchanges': set(),
                'cex_dominance': {},
                'dex_presence': {},
                'liquidity_analysis': {},
                'trading_pairs_analysis': {}
            },
            'coins': {}
        }
        
        for coin_id, tickers_data in tickers_by_coin.items():
            if not tickers_data or 'tickers' not in tickers_data:
                continue
            
            coin_data = {
                'total_tickers': len(tickers_data.get('tickers', [])),
                'exchanges': [],
                'top_exchanges_by_volume': [],
                'trading_pairs': {},
                'liquidity_metrics': {
                    'total_volume_24h': 0,
                    'average_spread': 0,
                    'exchange_count': 0,
                    'cex_volume_share': 0,
                    'dex_volume_share': 0
                },
                'market_structure': {
                    'centralized_exchanges': [],
                    'decentralized_exchanges': [],
                    'derivatives_exchanges': []
                }
            }
            
            # Process each ticker
            total_volume = 0
            spreads = []
            exchanges_seen = set()
            cex_volume = 0
            dex_volume = 0
            
            for ticker in tickers_data.get('tickers', []):
                exchange_name = ticker.get('market', {}).get('name', '')
                if not exchange_name:
                    continue
                
                exchanges_seen.add(exchange_name)
                processed['exchange_analysis']['total_exchanges'].add(exchange_name)
                
                volume_24h = ticker.get('volume', 0) or 0
                total_volume += volume_24h
                
                # Calculate spread if available
                bid = ticker.get('bid_ask_spread_percentage')
                if bid is not None:
                    spreads.append(bid)
                
                # Categorize exchange type
                exchange_type = self._categorize_exchange(exchange_name)
                if exchange_type == 'CEX':
                    cex_volume += volume_24h
                    coin_data['market_structure']['centralized_exchanges'].append(exchange_name)
                elif exchange_type == 'DEX':
                    dex_volume += volume_24h
                    coin_data['market_structure']['decentralized_exchanges'].append(exchange_name)
                elif exchange_type == 'DERIVATIVES':
                    coin_data['market_structure']['derivatives_exchanges'].append(exchange_name)
                
                # Track trading pairs
                base = ticker.get('base', '')
                target = ticker.get('target', '')
                if base and target:
                    pair = f"{base}/{target}"
                    if pair not in coin_data['trading_pairs']:
                        coin_data['trading_pairs'][pair] = {
                            'exchanges': [],
                            'total_volume': 0
                        }
                    coin_data['trading_pairs'][pair]['exchanges'].append(exchange_name)
                    coin_data['trading_pairs'][pair]['total_volume'] += volume_24h
                
                # Store exchange data
                exchange_data = {
                    'name': exchange_name,
                    'base': base,
                    'target': target,
                    'volume': volume_24h,
                    'last_price': ticker.get('last'),
                    'bid_ask_spread_percentage': ticker.get('bid_ask_spread_percentage'),
                    'timestamp': ticker.get('timestamp'),
                    'last_traded_at': ticker.get('last_traded_at'),
                    'last_fetch_at': ticker.get('last_fetch_at'),
                    'is_anomaly': ticker.get('is_anomaly', False),
                    'is_stale': ticker.get('is_stale', False),
                    'trust_score': ticker.get('trust_score'),
                    'trade_url': ticker.get('trade_url')
                }
                
                coin_data['exchanges'].append(exchange_data)
            
            # Sort exchanges by volume
            coin_data['exchanges'].sort(key=lambda x: x.get('volume', 0) or 0, reverse=True)
            coin_data['top_exchanges_by_volume'] = [
                {
                    'name': ex['name'],
                    'volume': ex['volume'],
                    'market_share': (ex['volume'] / total_volume * 100) if total_volume > 0 else 0
                }
                for ex in coin_data['exchanges'][:10]
            ]
            
            # Calculate liquidity metrics
            coin_data['liquidity_metrics']['total_volume_24h'] = total_volume
            coin_data['liquidity_metrics']['exchange_count'] = len(exchanges_seen)
            coin_data['liquidity_metrics']['average_spread'] = sum(spreads) / len(spreads) if spreads else 0
            
            if total_volume > 0:
                coin_data['liquidity_metrics']['cex_volume_share'] = (cex_volume / total_volume) * 100
                coin_data['liquidity_metrics']['dex_volume_share'] = (dex_volume / total_volume) * 100
            
            # Remove duplicates from exchange lists
            coin_data['market_structure']['centralized_exchanges'] = list(set(coin_data['market_structure']['centralized_exchanges']))
            coin_data['market_structure']['decentralized_exchanges'] = list(set(coin_data['market_structure']['decentralized_exchanges']))
            coin_data['market_structure']['derivatives_exchanges'] = list(set(coin_data['market_structure']['derivatives_exchanges']))
            
            processed['coins'][coin_id] = coin_data
        
        # Calculate global exchange analysis
        processed['exchange_analysis']['total_exchanges'] = list(processed['exchange_analysis']['total_exchanges'])
        
        # Analyze CEX vs DEX dominance across all coins
        for coin_id, coin_data in processed['coins'].items():
            cex_share = coin_data['liquidity_metrics']['cex_volume_share']
            dex_share = coin_data['liquidity_metrics']['dex_volume_share']
            
            processed['exchange_analysis']['cex_dominance'][coin_id] = cex_share
            processed['exchange_analysis']['dex_presence'][coin_id] = dex_share
            
            # Liquidity analysis
            total_volume = coin_data['liquidity_metrics']['total_volume_24h']
            exchange_count = coin_data['liquidity_metrics']['exchange_count']
            avg_spread = coin_data['liquidity_metrics']['average_spread']
            
            liquidity_score = self._calculate_liquidity_score(total_volume, exchange_count, avg_spread)
            processed['exchange_analysis']['liquidity_analysis'][coin_id] = {
                'volume_24h': total_volume,
                'exchange_count': exchange_count,
                'average_spread': avg_spread,
                'liquidity_score': liquidity_score
            }
        
        return processed
    
    def _categorize_exchange(self, exchange_name: str) -> str:
        """Categorize exchange as CEX, DEX, or DERIVATIVES."""
        
        exchange_lower = exchange_name.lower()
        
        # Known DEX patterns
        dex_indicators = [
            'uniswap', 'sushiswap', 'pancakeswap', 'curve', 'balancer',
            'dex', 'swap', 'defi', 'compound', 'aave', 'yearn',
            'quickswap', 'trader joe', 'spookyswap', 'honeyswap'
        ]
        
        # Known derivatives exchanges
        derivatives_indicators = [
            'bitmex', 'bybit', 'okex', 'ftx', 'dydx', 'perpetual',
            'futures', 'options', 'derivatives', 'leverage'
        ]
        
        for indicator in dex_indicators:
            if indicator in exchange_lower:
                return 'DEX'
        
        for indicator in derivatives_indicators:
            if indicator in exchange_lower:
                return 'DERIVATIVES'
        
        # Default to CEX
        return 'CEX'
    
    def _calculate_liquidity_score(self, volume: float, exchange_count: int, avg_spread: float) -> float:
        """Calculate a composite liquidity score."""
        
        # Normalize volume (log scale for very large numbers)
        import math
        volume_score = math.log10(max(volume, 1)) / 10  # Scale to 0-1 range roughly
        
        # Exchange count score (more exchanges = better liquidity)
        exchange_score = min(exchange_count / 20, 1.0)  # Cap at 20 exchanges
        
        # Spread score (lower spread = better liquidity)
        spread_score = max(0, 1 - (avg_spread / 5))  # 5% spread = 0 score
        
        # Weighted combination
        liquidity_score = (volume_score * 0.5) + (exchange_score * 0.3) + (spread_score * 0.2)
        
        return round(liquidity_score, 3)