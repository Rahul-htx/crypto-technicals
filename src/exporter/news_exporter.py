import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class NewsExporter:
    """Export news data to JSON format."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, news_data: Dict[str, Any], coins: List[str]) -> None:
        """
        Export news data to JSON file.
        
        Args:
            news_data: Raw news data from CoinGecko API
            coins: List of coins being tracked
        """
        
        # Process and structure news data
        processed_news = self._process_news_data(news_data, coins)
        
        # Export to JSON
        news_file = self.output_dir / "news.json"
        
        with open(news_file, 'w') as f:
            json.dump(processed_news, f, indent=2, default=str)
    
    def _process_news_data(self, news_data: Dict[str, Any], coins: List[str]) -> Dict[str, Any]:
        """Process raw news data into structured format."""
        
        processed = {
            'export_timestamp': datetime.now().isoformat(),
            'tracked_coins': coins,
            'news_summary': {
                'total_articles': len(news_data.get('data', [])),
                'sources': set(),
                'coin_mentions': {coin: 0 for coin in coins}
            },
            'articles': []
        }
        
        # Process each article
        for article in news_data.get('data', []):
            article_data = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'source': article.get('source', ''),
                'published_at': article.get('published_at', ''),
                'thumb_2x': article.get('thumb_2x', ''),
                'relevance_score': article.get('relevance_score'),
                'mentioned_coins': [],
                'sentiment_indicators': self._extract_sentiment_indicators(
                    article.get('title', '') + ' ' + article.get('description', '')
                )
            }
            
            # Track source
            if article_data['source']:
                processed['news_summary']['sources'].add(article_data['source'])
            
            # Check for coin mentions
            title_desc = (article_data['title'] + ' ' + article_data['description']).lower()
            for coin in coins:
                coin_variations = [coin.lower(), coin.upper(), coin.capitalize()]
                # Add common variations
                if coin == 'bitcoin':
                    coin_variations.extend(['btc', 'BTC'])
                elif coin == 'ethereum':
                    coin_variations.extend(['eth', 'ETH'])
                elif coin == 'solana':
                    coin_variations.extend(['sol', 'SOL'])
                elif coin == 'chainlink':
                    coin_variations.extend(['link', 'LINK'])
                elif coin == 'ripple':
                    coin_variations.extend(['xrp', 'XRP'])
                elif coin == 'cardano':
                    coin_variations.extend(['ada', 'ADA'])
                
                for variation in coin_variations:
                    if variation in title_desc:
                        article_data['mentioned_coins'].append(coin)
                        processed['news_summary']['coin_mentions'][coin] += 1
                        break
            
            processed['articles'].append(article_data)
        
        # Convert sets to lists for JSON serialization
        processed['news_summary']['sources'] = list(processed['news_summary']['sources'])
        
        # Sort articles by relevance score if available
        processed['articles'].sort(
            key=lambda x: x.get('relevance_score', 0) or 0, 
            reverse=True
        )
        
        return processed
    
    def _extract_sentiment_indicators(self, text: str) -> Dict[str, Any]:
        """Extract basic sentiment indicators from text."""
        
        text_lower = text.lower()
        
        # Positive sentiment keywords
        positive_keywords = [
            'bullish', 'surge', 'rally', 'breakout', 'pump', 'moon', 'ath', 
            'adoption', 'partnership', 'upgrade', 'launch', 'milestone',
            'gains', 'soar', 'rocket', 'explosive', 'breakthrough'
        ]
        
        # Negative sentiment keywords
        negative_keywords = [
            'bearish', 'crash', 'dump', 'fall', 'decline', 'drop', 'collapse',
            'hack', 'exploit', 'regulation', 'ban', 'controversy', 'lawsuit',
            'loss', 'plunge', 'sell-off', 'correction', 'bearish'
        ]
        
        # Neutral/Technical keywords
        technical_keywords = [
            'analysis', 'technical', 'support', 'resistance', 'volume',
            'indicator', 'pattern', 'trend', 'consolidation', 'sideways'
        ]
        
        sentiment_data = {
            'positive_signals': [kw for kw in positive_keywords if kw in text_lower],
            'negative_signals': [kw for kw in negative_keywords if kw in text_lower],
            'technical_signals': [kw for kw in technical_keywords if kw in text_lower],
            'sentiment_score': 0
        }
        
        # Calculate basic sentiment score
        pos_count = len(sentiment_data['positive_signals'])
        neg_count = len(sentiment_data['negative_signals'])
        
        if pos_count + neg_count > 0:
            sentiment_data['sentiment_score'] = (pos_count - neg_count) / (pos_count + neg_count)
        
        return sentiment_data