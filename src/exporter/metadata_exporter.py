import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class MetadataExporter:
    """Export coin metadata to JSON format."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, metadata_by_coin: Dict[str, Dict[str, Any]]) -> None:
        """
        Export metadata for all coins to JSON file.
        
        Args:
            metadata_by_coin: Dictionary mapping coin_id to metadata
        """
        
        # Process and structure metadata
        processed_metadata = self._process_metadata(metadata_by_coin)
        
        # Export to JSON
        metadata_file = self.output_dir / "metadata.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(processed_metadata, f, indent=2, default=str)
    
    def _process_metadata(self, metadata_by_coin: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Process raw metadata into structured format."""
        
        processed = {
            'export_timestamp': datetime.now().isoformat(),
            'coins': {},
            'summary': {
                'total_coins': len(metadata_by_coin),
                'categories': set(),
                'platforms': set(),
                'total_market_cap': 0,
                'total_volume': 0
            }
        }
        
        for coin_id, metadata in metadata_by_coin.items():
            if not metadata:  # Skip if metadata fetch failed
                continue
                
            coin_data = {
                'basic_info': {
                    'id': metadata.get('id'),
                    'symbol': metadata.get('symbol', '').upper(),
                    'name': metadata.get('name'),
                    'description': self._clean_description(metadata.get('description', {}).get('en', '')),
                    'categories': metadata.get('categories', []),
                    'platforms': metadata.get('platforms', {}),
                    'genesis_date': metadata.get('genesis_date'),
                    'homepage': metadata.get('links', {}).get('homepage', []),
                    'blockchain_site': metadata.get('links', {}).get('blockchain_site', []),
                    'official_forum_url': metadata.get('links', {}).get('official_forum_url', []),
                    'chat_url': metadata.get('links', {}).get('chat_url', []),
                    'announcement_url': metadata.get('links', {}).get('announcement_url', []),
                    'twitter_screen_name': metadata.get('links', {}).get('twitter_screen_name'),
                    'facebook_username': metadata.get('links', {}).get('facebook_username'),
                    'telegram_channel_identifier': metadata.get('links', {}).get('telegram_channel_identifier'),
                    'subreddit_url': metadata.get('links', {}).get('subreddit_url'),
                    'repos_url': metadata.get('links', {}).get('repos_url', {})
                },
                'market_data': {
                    'current_price_usd': metadata.get('market_data', {}).get('current_price', {}).get('usd'),
                    'market_cap_usd': metadata.get('market_data', {}).get('market_cap', {}).get('usd'),
                    'total_volume_usd': metadata.get('market_data', {}).get('total_volume', {}).get('usd'),
                    'market_cap_rank': metadata.get('market_cap_rank'),
                    'coingecko_rank': metadata.get('coingecko_rank'),
                    'coingecko_score': metadata.get('coingecko_score'),
                    'developer_score': metadata.get('developer_score'),
                    'community_score': metadata.get('community_score'),
                    'liquidity_score': metadata.get('liquidity_score'),
                    'public_interest_score': metadata.get('public_interest_score'),
                    'circulating_supply': metadata.get('market_data', {}).get('circulating_supply'),
                    'total_supply': metadata.get('market_data', {}).get('total_supply'),
                    'max_supply': metadata.get('market_data', {}).get('max_supply'),
                    'ath': metadata.get('market_data', {}).get('ath', {}).get('usd'),
                    'ath_date': metadata.get('market_data', {}).get('ath_date', {}).get('usd'),
                    'atl': metadata.get('market_data', {}).get('atl', {}).get('usd'),
                    'atl_date': metadata.get('market_data', {}).get('atl_date', {}).get('usd'),
                    'price_change_24h': metadata.get('market_data', {}).get('price_change_24h'),
                    'price_change_percentage_24h': metadata.get('market_data', {}).get('price_change_percentage_24h'),
                    'price_change_percentage_7d': metadata.get('market_data', {}).get('price_change_percentage_7d'),
                    'price_change_percentage_30d': metadata.get('market_data', {}).get('price_change_percentage_30d'),
                    'price_change_percentage_1y': metadata.get('market_data', {}).get('price_change_percentage_1y')
                },
                'community_data': {
                    'facebook_likes': metadata.get('community_data', {}).get('facebook_likes'),
                    'twitter_followers': metadata.get('community_data', {}).get('twitter_followers'),
                    'reddit_average_posts_48h': metadata.get('community_data', {}).get('reddit_average_posts_48h'),
                    'reddit_average_comments_48h': metadata.get('community_data', {}).get('reddit_average_comments_48h'),
                    'reddit_subscribers': metadata.get('community_data', {}).get('reddit_subscribers'),
                    'reddit_accounts_active_48h': metadata.get('community_data', {}).get('reddit_accounts_active_48h'),
                    'telegram_channel_user_count': metadata.get('community_data', {}).get('telegram_channel_user_count')
                },
                'developer_data': {
                    'forks': metadata.get('developer_data', {}).get('forks'),
                    'stars': metadata.get('developer_data', {}).get('stars'),
                    'subscribers': metadata.get('developer_data', {}).get('subscribers'),
                    'total_issues': metadata.get('developer_data', {}).get('total_issues'),
                    'closed_issues': metadata.get('developer_data', {}).get('closed_issues'),
                    'pull_requests_merged': metadata.get('developer_data', {}).get('pull_requests_merged'),
                    'pull_request_contributors': metadata.get('developer_data', {}).get('pull_request_contributors'),
                    'code_additions_deletions_4_weeks': metadata.get('developer_data', {}).get('code_additions_deletions_4_weeks'),
                    'commit_count_4_weeks': metadata.get('developer_data', {}).get('commit_count_4_weeks'),
                    'last_4_weeks_commit_activity_series': metadata.get('developer_data', {}).get('last_4_weeks_commit_activity_series')
                },
                'sentiment_votes_up_percentage': metadata.get('sentiment_votes_up_percentage'),
                'sentiment_votes_down_percentage': metadata.get('sentiment_votes_down_percentage'),
                'watchlist_portfolio_users': metadata.get('watchlist_portfolio_users'),
                'status_updates': metadata.get('status_updates', [])
            }
            
            # Update summary statistics
            categories = metadata.get('categories', [])
            platforms = metadata.get('platforms', {})
            market_cap = metadata.get('market_data', {}).get('market_cap', {}).get('usd', 0) or 0
            volume = metadata.get('market_data', {}).get('total_volume', {}).get('usd', 0) or 0
            
            processed['summary']['categories'].update(categories)
            processed['summary']['platforms'].update(platforms.keys())
            processed['summary']['total_market_cap'] += market_cap
            processed['summary']['total_volume'] += volume
            
            processed['coins'][coin_id] = coin_data
        
        # Convert sets to lists for JSON serialization
        processed['summary']['categories'] = list(processed['summary']['categories'])
        processed['summary']['platforms'] = list(processed['summary']['platforms'])
        
        return processed
    
    def _clean_description(self, description: str) -> str:
        """Clean and truncate description text."""
        if not description:
            return ""
        
        # Remove HTML tags
        import re
        description = re.sub(r'<[^>]+>', '', description)
        
        # Truncate to reasonable length for LLM processing
        max_length = 1000
        if len(description) > max_length:
            description = description[:max_length] + "..."
        
        return description.strip()