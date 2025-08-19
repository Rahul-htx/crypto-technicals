import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class CategoriesExporter:
    """Export categories and sector data to JSON format."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, categories_data: List[Dict[str, Any]], tracked_coins: List[str]) -> None:
        """
        Export categories and sector rotation data to JSON file.
        
        Args:
            categories_data: Raw categories data from CoinGecko API
            tracked_coins: List of coins being tracked
        """
        
        # Process and structure categories data
        processed_categories = self._process_categories_data(categories_data, tracked_coins)
        
        # Export to JSON
        categories_file = self.output_dir / "categories.json"
        
        with open(categories_file, 'w') as f:
            json.dump(processed_categories, f, indent=2, default=str)
    
    def _process_categories_data(self, categories_data: List[Dict[str, Any]], tracked_coins: List[str]) -> Dict[str, Any]:
        """Process raw categories data into structured format."""
        
        processed = {
            'export_timestamp': datetime.now().isoformat(),
            'tracked_coins': tracked_coins,
            'sector_analysis': {
                'total_categories': len(categories_data),
                'top_performers_24h': [],
                'worst_performers_24h': [],
                'largest_by_market_cap': [],
                'sector_rotation_signals': []
            },
            'categories': [],
            'tracked_coin_sectors': {}
        }
        
        # Sort categories by different metrics for analysis
        categories_by_change_24h = sorted(
            [cat for cat in categories_data if cat.get('market_cap_change_24h') is not None],
            key=lambda x: x.get('market_cap_change_24h', 0),
            reverse=True
        )
        
        categories_by_market_cap = sorted(
            [cat for cat in categories_data if cat.get('market_cap') is not None],
            key=lambda x: x.get('market_cap', 0),
            reverse=True
        )
        
        # Identify top and worst performers
        processed['sector_analysis']['top_performers_24h'] = [
            {
                'name': cat.get('name'),
                'id': cat.get('id'),
                'market_cap_change_24h': cat.get('market_cap_change_24h'),
                'volume_24h': cat.get('volume_24h'),
                'market_cap': cat.get('market_cap')
            }
            for cat in categories_by_change_24h[:5]
        ]
        
        processed['sector_analysis']['worst_performers_24h'] = [
            {
                'name': cat.get('name'),
                'id': cat.get('id'),
                'market_cap_change_24h': cat.get('market_cap_change_24h'),
                'volume_24h': cat.get('volume_24h'),
                'market_cap': cat.get('market_cap')
            }
            for cat in categories_by_change_24h[-5:]
        ]
        
        processed['sector_analysis']['largest_by_market_cap'] = [
            {
                'name': cat.get('name'),
                'id': cat.get('id'),
                'market_cap': cat.get('market_cap'),
                'market_cap_change_24h': cat.get('market_cap_change_24h'),
                'volume_24h': cat.get('volume_24h')
            }
            for cat in categories_by_market_cap[:10]
        ]
        
        # Process all categories
        for category in categories_data:
            cat_data = {
                'id': category.get('id'),
                'name': category.get('name'),
                'market_cap': category.get('market_cap'),
                'market_cap_change_24h': category.get('market_cap_change_24h'),
                'volume_24h': category.get('volume_24h'),
                'coins_count': category.get('coins_count'),
                'top_3_coins': category.get('top_3_coins', []),
                'performance_signals': self._analyze_category_performance(category)
            }
            
            processed['categories'].append(cat_data)
            
            # Map tracked coins to their sectors
            for coin in category.get('top_3_coins', []):
                coin_id = coin.lower()
                if coin_id in [c.lower() for c in tracked_coins]:
                    if coin_id not in processed['tracked_coin_sectors']:
                        processed['tracked_coin_sectors'][coin_id] = []
                    processed['tracked_coin_sectors'][coin_id].append({
                        'category_name': category.get('name'),
                        'category_id': category.get('id'),
                        'market_cap_change_24h': category.get('market_cap_change_24h'),
                        'category_rank': len(processed['tracked_coin_sectors'][coin_id]) + 1
                    })
        
        # Generate sector rotation signals
        processed['sector_analysis']['sector_rotation_signals'] = self._generate_rotation_signals(categories_data)
        
        return processed
    
    def _analyze_category_performance(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual category performance and generate signals."""
        
        market_cap_change = category.get('market_cap_change_24h', 0) or 0
        volume_24h = category.get('volume_24h', 0) or 0
        market_cap = category.get('market_cap', 0) or 0
        
        signals = {
            'momentum_signal': 'neutral',
            'volume_signal': 'normal',
            'size_category': 'unknown',
            'strength_score': 0
        }
        
        # Momentum analysis
        if market_cap_change > 10:
            signals['momentum_signal'] = 'strong_bullish'
            signals['strength_score'] += 3
        elif market_cap_change > 5:
            signals['momentum_signal'] = 'bullish'
            signals['strength_score'] += 2
        elif market_cap_change > 0:
            signals['momentum_signal'] = 'slightly_bullish'
            signals['strength_score'] += 1
        elif market_cap_change < -10:
            signals['momentum_signal'] = 'strong_bearish'
            signals['strength_score'] -= 3
        elif market_cap_change < -5:
            signals['momentum_signal'] = 'bearish'
            signals['strength_score'] -= 2
        elif market_cap_change < 0:
            signals['momentum_signal'] = 'slightly_bearish'
            signals['strength_score'] -= 1
        
        # Volume analysis (relative to market cap)
        if market_cap > 0:
            volume_ratio = volume_24h / market_cap
            if volume_ratio > 0.1:
                signals['volume_signal'] = 'high'
                signals['strength_score'] += 1
            elif volume_ratio < 0.01:
                signals['volume_signal'] = 'low'
                signals['strength_score'] -= 1
        
        # Size categorization
        if market_cap > 100_000_000_000:  # $100B+
            signals['size_category'] = 'mega_cap'
        elif market_cap > 10_000_000_000:  # $10B+
            signals['size_category'] = 'large_cap'
        elif market_cap > 1_000_000_000:  # $1B+
            signals['size_category'] = 'mid_cap'
        elif market_cap > 100_000_000:  # $100M+
            signals['size_category'] = 'small_cap'
        else:
            signals['size_category'] = 'micro_cap'
        
        return signals
    
    def _generate_rotation_signals(self, categories_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate sector rotation signals based on performance patterns."""
        
        signals = []
        
        # Find categories with significant outperformance
        strong_performers = [
            cat for cat in categories_data 
            if (cat.get('market_cap_change_24h') or 0) > 15
        ]
        
        # Find categories with high volume relative to market cap
        high_volume_categories = []
        for cat in categories_data:
            market_cap = cat.get('market_cap', 0) or 0
            volume_24h = cat.get('volume_24h', 0) or 0
            if market_cap > 0 and (volume_24h / market_cap) > 0.15:
                high_volume_categories.append(cat)
        
        # Generate signals
        if strong_performers:
            signals.append({
                'signal_type': 'sector_breakout',
                'description': f"{len(strong_performers)} sectors showing strong momentum (>15% gains)",
                'categories': [cat.get('name') for cat in strong_performers[:3]],
                'strength': 'high' if len(strong_performers) >= 3 else 'medium'
            })
        
        if high_volume_categories:
            signals.append({
                'signal_type': 'high_volume_rotation',
                'description': f"{len(high_volume_categories)} sectors showing unusual volume activity",
                'categories': [cat.get('name') for cat in high_volume_categories[:3]],
                'strength': 'high' if len(high_volume_categories) >= 5 else 'medium'
            })
        
        # Check for broad market rotation patterns
        positive_categories = len([cat for cat in categories_data if (cat.get('market_cap_change_24h') or 0) > 0])
        total_categories = len(categories_data)
        
        if total_categories > 0:
            positive_ratio = positive_categories / total_categories
            if positive_ratio > 0.8:
                signals.append({
                    'signal_type': 'broad_market_rally',
                    'description': f"{positive_ratio:.1%} of sectors showing positive performance",
                    'strength': 'high'
                })
            elif positive_ratio < 0.2:
                signals.append({
                    'signal_type': 'broad_market_decline',
                    'description': f"Only {positive_ratio:.1%} of sectors showing positive performance",
                    'strength': 'high'
                })
        
        return signals