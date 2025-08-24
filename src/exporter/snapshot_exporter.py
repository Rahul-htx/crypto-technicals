import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import logging

class SnapshotExporter:
    """
    Export a compact, LLM-optimized snapshot of technical analysis data.
    
    Automatically determines what data to include based on freshness:
    - Core data: always updated
    - History arrays: if >60 minutes since last update
    - Long-horizon stats: if >24 hours since last update
    """
    
    def __init__(self, output_dir: Path, logger: logging.Logger, fetcher=None):
        self.output_dir = Path(output_dir)
        self.snapshots_dir = self.output_dir.parent / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        self.fetcher = fetcher  # CoinGecko fetcher for market data
        
        # Paths for snapshot files
        self.latest_snapshot_path = self.snapshots_dir / "latest_snapshot.json"
    
    def export(self, results: Dict[str, Dict[str, Any]], horizon: str, 
               force_hourly: bool = False, force_daily: bool = False) -> None:
        """
        Export snapshot with automatic freshness detection to combined horizon file.
        
        Args:
            results: Dictionary containing coin data and metadata
            horizon: Time horizon (e.g., 'intraday', 'swing')
            force_hourly: Force include history arrays regardless of timing
            force_daily: Force include long-horizon stats regardless of timing
        """
        
        if not results:
            self.logger.warning("No results to export in snapshot")
            return
            
        # Get metadata from first coin
        first_coin_data = next(iter(results.values()))
        granularity = first_coin_data['metadata']['granularity']
        coins = list(results.keys())
        
        # Load existing combined snapshot
        combined_snapshot = self._load_combined_snapshot()
        
        # Determine freshness based on this horizon's last run
        existing_horizon_data = combined_snapshot.get(horizon, {}) if combined_snapshot else {}
        now = datetime.utcnow()
        include_history, include_long_stats = self._determine_freshness_for_horizon(
            existing_horizon_data, now, granularity, force_hourly, force_daily
        )
        
        self.logger.info(f"Snapshot export [{horizon}]: history={include_history}, long_stats={include_long_stats}")
        
        # Fetch fresh market data for snapshot
        markets_data = self._fetch_markets_data(coins)
        global_market_data = self._fetch_global_market_data()
        
        # Build horizon-specific payload
        horizon_payload = {
            "meta": self._build_meta_section(now, horizon, granularity, coins, 
                                           include_history, include_long_stats),
            "market_overview": self._build_market_overview(global_market_data),
            "cross_coin": self._build_cross_coin_analysis(results),
            "coins": self._build_coins_section(results, markets_data, include_history, include_long_stats),
            "news": self._build_news_section(existing_horizon_data)
        }
        
        # Update combined snapshot
        if not combined_snapshot:
            combined_snapshot = {}
            
        combined_snapshot[horizon] = horizon_payload
        
        # Update top-level metadata
        combined_snapshot["meta"] = self._build_combined_meta(combined_snapshot, now, coins)
        
        # Write files (timestamped backup + combined latest)
        self._write_combined_snapshot_files(combined_snapshot, horizon_payload, now, horizon)
        
        self.logger.info(f"Combined snapshot updated for horizon '{horizon}' at {self.latest_snapshot_path}")
    
    def _load_combined_snapshot(self) -> Optional[Dict[str, Any]]:
        """Load existing combined snapshot file if it exists."""
        if not self.latest_snapshot_path.exists():
            return None
            
        try:
            with open(self.latest_snapshot_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load existing combined snapshot: {e}")
            return None
    
    def _load_existing_snapshot(self) -> Optional[Dict[str, Any]]:
        """Load existing snapshot file if it exists (legacy method)."""
        return self._load_combined_snapshot()
    
    def _determine_freshness(self, existing_snapshot: Optional[Dict[str, Any]], 
                           now: datetime, granularity: str, force_hourly: bool, force_daily: bool) -> Tuple[bool, bool]:
        """Determine what data to include based on data boundaries crossed and force flags."""
        
        # Force flags override everything
        if force_hourly and force_daily:
            return True, True
        elif force_hourly:
            return True, False
        elif force_daily:
            return True, True  # daily implies hourly
            
        # No existing snapshot = include everything
        if not existing_snapshot or 'meta' not in existing_snapshot:
            return True, True
            
        meta = existing_snapshot['meta']
        
        # Get last run timestamp
        try:
            last_run_str = meta.get('run_timestamp')
            if not last_run_str:
                return True, True
                
            last_run = datetime.fromisoformat(last_run_str.replace('Z', '+00:00'))
            last_run = last_run.replace(tzinfo=None)  # Remove timezone for comparison
            
        except Exception as e:
            self.logger.debug(f"Could not parse run timestamp: {e}")
            return True, True
        
        # Determine if we've crossed meaningful data boundaries
        include_history = self._crossed_data_boundary(last_run, now, granularity)
        include_long_stats = self._crossed_daily_boundary(last_run, now)
        
        self.logger.debug(f"Boundary check: last={last_run.isoformat()}, now={now.isoformat()}, "
                         f"granularity={granularity}, history={include_history}, long_stats={include_long_stats}")
        
        return include_history, include_long_stats
    
    def _crossed_data_boundary(self, last_run: datetime, now: datetime, granularity: str) -> bool:
        """Check if we've crossed a meaningful data boundary for the given granularity."""
        
        if granularity in ['1h']:
            # For hourly data, update if we've crossed an hour boundary
            return last_run.hour != now.hour or last_run.date() != now.date()
            
        elif granularity in ['4h']:
            # For 4-hour data, update if we've crossed a 4-hour boundary
            last_4h_period = last_run.hour // 4
            now_4h_period = now.hour // 4
            return (last_4h_period != now_4h_period or 
                   last_run.date() != now.date())
            
        elif granularity in ['1d']:
            # For daily data, update if we've crossed a day boundary
            return last_run.date() != now.date()
            
        else:
            # For unknown granularities, fall back to hourly logic
            return last_run.hour != now.hour or last_run.date() != now.date()
    
    def _crossed_daily_boundary(self, last_run: datetime, now: datetime) -> bool:
        """Check if we've crossed a daily boundary (for long-horizon stats)."""
        return last_run.date() != now.date()
    
    def _determine_freshness_for_horizon(self, existing_horizon_data: Dict[str, Any], 
                                       now: datetime, granularity: str, force_hourly: bool, force_daily: bool) -> Tuple[bool, bool]:
        """Determine freshness for a specific horizon's data."""
        return self._determine_freshness(existing_horizon_data, now, granularity, force_hourly, force_daily)
    
    def _build_combined_meta(self, combined_snapshot: Dict[str, Any], now: datetime, coins: List[str]) -> Dict[str, Any]:
        """Build top-level metadata for combined snapshot."""
        
        horizons_present = []
        for key in combined_snapshot.keys():
            if key != "meta" and isinstance(combined_snapshot[key], dict):
                horizons_present.append(key)
        
        return {
            "last_updated": now.isoformat() + 'Z',
            "horizons_present": sorted(horizons_present),
            "coins_tracked": coins
        }
    
    def _build_meta_section(self, now: datetime, horizon: str, granularity: str, 
                           coins: List[str], include_history: bool, include_long_stats: bool) -> Dict[str, Any]:
        """Build metadata section."""
        
        # Update timestamps based on what we're including
        history_timestamp = now.isoformat() + 'Z' if include_history else None
        long_stats_timestamp = now.isoformat() + 'Z' if include_long_stats else None
        
        # Preserve existing timestamps if we're not updating those sections
        existing_snapshot = self._load_existing_snapshot()
        if existing_snapshot and 'meta' in existing_snapshot:
            if not include_history and 'history_last_updated' in existing_snapshot['meta']:
                history_timestamp = existing_snapshot['meta']['history_last_updated']
            if not include_long_stats and 'long_stats_last_updated' in existing_snapshot['meta']:
                long_stats_timestamp = existing_snapshot['meta']['long_stats_last_updated']
        
        return {
            "run_timestamp": now.isoformat() + 'Z',
            "horizon": horizon,
            "granularity": granularity,
            "coins_tracked": coins,
            "history_last_updated": history_timestamp,
            "long_stats_last_updated": long_stats_timestamp,
            "data_completeness": {
                "price": True,
                "indicators": True,
                "news": False  # CryptoPanic not implemented yet
            }
        }
    
    def _build_market_overview(self, global_market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build market overview section from fresh global market data."""
        
        overview = {}
        
        if global_market_data and 'data' in global_market_data:
            data = global_market_data['data']
            
            # Extract total market cap
            if 'total_market_cap' in data and 'usd' in data['total_market_cap']:
                overview['total_market_cap_usd'] = data['total_market_cap']['usd']
            
            # Extract market cap percentages (BTC dominance)
            if 'market_cap_percentage' in data:
                market_cap_pct = data['market_cap_percentage']
                if 'btc' in market_cap_pct:
                    overview['btc_dominance_pct'] = market_cap_pct['btc']
                if 'eth' in market_cap_pct:
                    overview['eth_dominance_pct'] = market_cap_pct['eth']
            
            # Extract other useful global metrics
            if 'active_cryptocurrencies' in data:
                overview['active_cryptocurrencies'] = data['active_cryptocurrencies']
            
            if 'markets' in data:
                overview['markets'] = data['markets']
            
            # Extract total volume
            if 'total_volume' in data and 'usd' in data['total_volume']:
                overview['total_volume_24h_usd'] = data['total_volume']['usd']
            
            # Calculate market cap change if available
            if 'market_cap_change_percentage_24h_usd' in data:
                overview['market_cap_change_24h_pct'] = data['market_cap_change_percentage_24h_usd']
            
            # Derive sentiment from BTC dominance
            btc_dom = overview.get('btc_dominance_pct', 50)
            overview['sentiment'] = 'risk_off' if btc_dom > 50 else 'risk_on'
        
        # Fallback to market_context.json if no fresh data
        if not overview:
            overview = self._build_market_overview_fallback()
        
        return overview
    
    def _build_market_overview_fallback(self) -> Dict[str, Any]:
        """Fallback: Build market overview from existing market_context.json."""
        
        market_context_path = self.output_dir / "market_context.json"
        
        if market_context_path.exists():
            try:
                with open(market_context_path, 'r') as f:
                    market_context = json.load(f)
                    
                overview = {}
                
                # Extract BTC dominance and total market cap
                if 'global_market' in market_context and 'market_overview' in market_context['global_market']:
                    global_data = market_context['global_market']['market_overview']
                    overview['btc_dominance_pct'] = global_data.get('bitcoin_dominance_percentage', 0)
                    overview['total_market_cap_usd'] = global_data.get('total_market_cap', {}).get('usd', 0)
                
                # Derive sentiment from BTC dominance
                btc_dom = overview.get('btc_dominance_pct', 50)
                overview['sentiment'] = 'risk_off' if btc_dom > 50 else 'risk_on'
                
                return overview
                
            except Exception as e:
                self.logger.debug(f"Could not load market context: {e}")
        
        # Fallback to existing horizon data or defaults
        if existing_horizon_data and 'market_overview' in existing_horizon_data:
            return existing_horizon_data['market_overview']
            
        return {
            "btc_dominance_pct": 50.0,
            "total_market_cap_usd": 0,
            "sentiment": "neutral",
            "sector_leaders_24h": []
        }
    
    def _build_cross_coin_analysis(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Build cross-coin ranking analysis."""
        
        performance_24h = {}
        volume_avg = {}
        volatility = {}
        
        for coin, data in results.items():
            df = data['data']
            if df.empty:
                continue
                
            # Calculate 24h performance (approximate from available data)
            if len(df) >= 24:  # Assuming hourly data
                perf_24h = ((df['close'].iloc[-1] - df['close'].iloc[-24]) / df['close'].iloc[-24]) * 100
            else:
                perf_24h = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
            
            performance_24h[coin] = perf_24h
            volume_avg[coin] = float(df['volume'].mean())
            volatility[coin] = float(df['close'].std() / df['close'].mean() * 100) if df['close'].mean() > 0 else 0
        
        # Sort rankings
        top_momentum = sorted(performance_24h.items(), key=lambda x: x[1], reverse=True)
        top_volume = sorted(volume_avg.items(), key=lambda x: x[1], reverse=True)
        lowest_volatility = sorted(volatility.items(), key=lambda x: x[1])
        
        return {
            "top_momentum_24h": [coin for coin, _ in top_momentum],
            "top_volume": [coin for coin, _ in top_volume],
            "lowest_volatility": [coin for coin, _ in lowest_volatility]
        }
    
    def _build_coins_section(self, results: Dict[str, Dict[str, Any]], 
                           markets_data: Dict[str, Any], include_history: bool, include_long_stats: bool) -> Dict[str, Any]:
        """Build coins data section with categorical signals and market data."""
        
        coins_data = {}
        
        for coin, data in results.items():
            df = data['data']
            if df.empty:
                continue
                
            latest = df.iloc[-1]
            
            # Get market data for this coin
            market_data = markets_data.get(coin, {})
            
            # Determine latest price: prefer real-time current_price from markets endpoint
            spot_price = market_data.get('current_price') if market_data else None
            if spot_price is not None:
                latest_price = float(spot_price)
                price_source = 'spot'
            else:
                latest_price = float(latest['close'])
                price_source = 'candle_close'
            
            coin_data = {
                "price": latest_price,
                "price_source": price_source,
                "price_timestamp": market_data.get('last_updated') if market_data else None
            }
            
            # Add percentage changes - try markets data first, fallback to calculation
            pct_changes = {}
            
            # Try to get from CoinGecko markets data
            if market_data:
                if 'price_change_percentage_1h_in_currency' in market_data:
                    pct_changes['1h'] = market_data['price_change_percentage_1h_in_currency']
                if 'price_change_percentage_24h_in_currency' in market_data:
                    pct_changes['24h'] = market_data['price_change_percentage_24h_in_currency']
                if 'price_change_percentage_7d_in_currency' in market_data:
                    pct_changes['7d'] = market_data['price_change_percentage_7d_in_currency']
            
            # Calculate from OHLCV data if markets data is missing
            if not pct_changes and len(df) >= 2:
                current_price = latest_price
                
                # 1h change (from previous hour)
                if len(df) >= 2:
                    prev_price = float(df['close'].iloc[-2])
                    if prev_price > 0:
                        pct_changes['1h'] = ((current_price - prev_price) / prev_price) * 100
                
                # 24h change (from 24 hours ago, assuming hourly data)
                if len(df) >= 24:
                    day_ago_price = float(df['close'].iloc[-24])
                    if day_ago_price > 0:
                        pct_changes['24h'] = ((current_price - day_ago_price) / day_ago_price) * 100
                elif len(df) >= 2:
                    # Fallback to beginning of data
                    start_price = float(df['close'].iloc[0])
                    if start_price > 0:
                        pct_changes['24h'] = ((current_price - start_price) / start_price) * 100
                
                # 7d change (from 7*24=168 hours ago)
                if len(df) >= 168:
                    week_ago_price = float(df['close'].iloc[-168])
                    if week_ago_price > 0:
                        pct_changes['7d'] = ((current_price - week_ago_price) / week_ago_price) * 100
            
            if pct_changes:
                coin_data['pct_change'] = pct_changes
            
            # Add market & supply metrics from CoinGecko markets API
            if market_data:
                self._add_market_metrics(coin_data, market_data)
            
            # Add indicators with categorical signals
            self._add_indicator_signals(coin_data, df, latest)
            
            # Add history arrays if requested
            if include_history:
                coin_data.update(self._build_history_arrays(df))
            
            coins_data[coin] = coin_data
        
        return coins_data
    
    def _add_market_metrics(self, coin_data: Dict[str, Any], market_data: Dict[str, Any]) -> None:
        """Add market cap, supply, and other metrics from CoinGecko markets API."""
        
        # Market cap
        if 'market_cap' in market_data and market_data['market_cap']:
            coin_data['market_cap_usd'] = market_data['market_cap']
        
        # Supply metrics
        if 'circulating_supply' in market_data and market_data['circulating_supply']:
            coin_data['circulating_supply'] = market_data['circulating_supply']
        
        if 'total_supply' in market_data and market_data['total_supply']:
            coin_data['total_supply'] = market_data['total_supply']
        
        if 'max_supply' in market_data and market_data['max_supply']:
            coin_data['max_supply'] = market_data['max_supply']
        
        # Volume
        if 'total_volume' in market_data and market_data['total_volume']:
            coin_data['volume_24h_usd'] = market_data['total_volume']
        
        # Market cap rank
        if 'market_cap_rank' in market_data and market_data['market_cap_rank']:
            coin_data['market_cap_rank'] = market_data['market_cap_rank']
        
        # Fully diluted valuation
        if 'fully_diluted_valuation' in market_data and market_data['fully_diluted_valuation']:
            coin_data['fully_diluted_valuation_usd'] = market_data['fully_diluted_valuation']
        
        # Calculate supply metrics
        circulating = coin_data.get('circulating_supply', 0)
        total = coin_data.get('total_supply', 0)
        max_supply = coin_data.get('max_supply', 0)
        
        if circulating and total and circulating > 0:
            coin_data['supply_circulation_pct'] = round((circulating / total) * 100, 2)
        
        if circulating and max_supply and circulating > 0 and max_supply > 0:
            coin_data['supply_inflation_remaining_pct'] = round(((max_supply - circulating) / max_supply) * 100, 2)
        
        # Volume/market cap ratio
        volume = coin_data.get('volume_24h_usd', 0)
        market_cap = coin_data.get('market_cap_usd', 0)
        if volume and market_cap and market_cap > 0:
            coin_data['volume_mcap_ratio'] = round(volume / market_cap, 4)
    
    def _add_indicator_signals(self, coin_data: Dict[str, Any], df: pd.DataFrame, latest: pd.Series) -> None:
        """Add indicator values and categorical signals."""
        
        # RSI
        if 'rsi_14' in df.columns and not pd.isna(latest['rsi_14']):
            rsi_val = float(latest['rsi_14'])
            coin_data['rsi_14'] = rsi_val
            if rsi_val > 70:
                coin_data['rsi_state'] = 'overbought'
            elif rsi_val < 30:
                coin_data['rsi_state'] = 'oversold'
            else:
                coin_data['rsi_state'] = 'neutral'
        
        # MACD
        if 'macd_histogram' in df.columns and not pd.isna(latest['macd_histogram']):
            macd_hist = float(latest['macd_histogram'])
            coin_data['macd_hist'] = macd_hist
            
            # Check for signal line cross (simplified)
            if len(df) >= 2:
                prev_hist = df['macd_histogram'].iloc[-2]
                if not pd.isna(prev_hist):
                    if macd_hist > 0 and prev_hist <= 0:
                        coin_data['macd_state'] = 'bullish_cross'
                    elif macd_hist < 0 and prev_hist >= 0:
                        coin_data['macd_state'] = 'bearish_cross'
                    else:
                        coin_data['macd_state'] = 'neutral'
                else:
                    coin_data['macd_state'] = 'neutral'
            else:
                coin_data['macd_state'] = 'neutral'
        
        # EMA crossover (50 vs 200)
        if 'ema_50' in df.columns and 'ema_200' in df.columns:
            if not pd.isna(latest['ema_50']) and not pd.isna(latest['ema_200']):
                ema_50 = float(latest['ema_50'])
                ema_200 = float(latest['ema_200'])
                
                if ema_50 > ema_200:
                    coin_data['ema_50_200'] = 'above'
                else:
                    coin_data['ema_50_200'] = 'below'
        
        # Bollinger Bands %B
        if 'bb_percent_b' in df.columns and not pd.isna(latest['bb_percent_b']):
            bb_pct = float(latest['bb_percent_b'])
            coin_data['bb_percent_b'] = bb_pct
            
            if bb_pct > 1:
                coin_data['bb_state'] = 'above_band'
            elif bb_pct < 0:
                coin_data['bb_state'] = 'below_band'
            else:
                coin_data['bb_state'] = 'inside'
        
        # ADX
        if 'adx_14' in df.columns and not pd.isna(latest['adx_14']):
            adx_val = float(latest['adx_14'])
            coin_data['adx_14'] = adx_val
            coin_data['trend_strength'] = 'strong' if adx_val > 25 else 'weak'
        
        # ATR as percentage
        if 'atr_14' in df.columns and not pd.isna(latest['atr_14']):
            atr_pct = (float(latest['atr_14']) / float(latest['close'])) * 100
            coin_data['atr_pct'] = round(atr_pct, 2)
        
        # OBV trend (simplified - just check if rising/falling over last few periods)
        if 'obv' in df.columns and len(df) >= 5:
            recent_obv = df['obv'].tail(5).dropna()
            if len(recent_obv) >= 2:
                if recent_obv.iloc[-1] > recent_obv.iloc[0]:
                    coin_data['obv_trend'] = 'up'
                elif recent_obv.iloc[-1] < recent_obv.iloc[0]:
                    coin_data['obv_trend'] = 'down'
                else:
                    coin_data['obv_trend'] = 'flat'
    
    def _build_history_arrays(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Build history arrays for the last 12 hours (assuming hourly data)."""
        
        # Limit to last 12 periods
        recent_df = df.tail(12)
        
        price_history = []
        for idx, row in recent_df.iterrows():
            price_history.append([idx.isoformat() + 'Z', float(row['close'])])
        
        # Key indicators history
        indicator_history = {}
        
        if 'rsi_14' in recent_df.columns:
            indicator_history['rsi_14'] = [float(x) if not pd.isna(x) else None 
                                         for x in recent_df['rsi_14'].tolist()]
        
        if 'macd_histogram' in recent_df.columns:
            indicator_history['macd_hist'] = [float(x) if not pd.isna(x) else None 
                                            for x in recent_df['macd_histogram'].tolist()]
        
        return {
            "price_history": price_history,
            "indicator_history": indicator_history
        }
    
    def _build_news_section(self, existing_horizon_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build news section (placeholder for CryptoPanic integration)."""
        
        # Preserve existing news if available
        if existing_horizon_data and 'news' in existing_horizon_data:
            return existing_horizon_data['news']
        
        return {
            "headline_count": 0,
            "by_coin": {},
            "global_sentiment": "neutral"
        }
    
    def _write_combined_snapshot_files(self, combined_snapshot: Dict[str, Any], 
                                      horizon_payload: Dict[str, Any], timestamp: datetime, horizon: str) -> None:
        """Write both timestamped backup and combined latest snapshot files."""
        
        # Write timestamped backup of this horizon's payload (for audit trail)
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H-%M-%SZ")
        timestamped_path = self.snapshots_dir / f"snapshot_{horizon}_{timestamp_str}.json"
        
        with open(timestamped_path, 'w') as f:
            json.dump(horizon_payload, f, indent=2, default=str)
        
        # Write/overwrite combined latest file
        with open(self.latest_snapshot_path, 'w') as f:
            json.dump(combined_snapshot, f, indent=2, default=str)
        
        self.logger.debug(f"Wrote timestamped {horizon} snapshot: {timestamped_path}")
    
    def _write_snapshot_files(self, snapshot: Dict[str, Any], timestamp: datetime) -> None:
        """Write both timestamped and latest snapshot files (legacy method)."""
        
        # Write timestamped file
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H-%M-%SZ")
        timestamped_path = self.snapshots_dir / f"snapshot_{timestamp_str}.json"
        
        with open(timestamped_path, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        # Write/overwrite latest file
        with open(self.latest_snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        self.logger.debug(f"Wrote timestamped snapshot: {timestamped_path}")
    
    def _fetch_markets_data(self, coins: List[str]) -> Dict[str, Any]:
        """Fetch fresh market data for coins."""
        if not self.fetcher:
            self.logger.warning("No CoinGecko fetcher available for market data")
            return {}
        
        try:
            markets_data = self.fetcher.fetch_markets_data(coins)
            self.logger.debug(f"Fetched market data for {len(markets_data)} coins")
            return markets_data
        except Exception as e:
            self.logger.error(f"Failed to fetch markets data for snapshot: {e}")
            return {}
    
    def _fetch_global_market_data(self) -> Dict[str, Any]:
        """Fetch fresh global market data."""
        if not self.fetcher:
            self.logger.warning("No CoinGecko fetcher available for global market data")
            return {}
        
        try:
            global_data = self.fetcher.fetch_global_market_data()
            self.logger.debug("Fetched global market data")
            return global_data
        except Exception as e:
            self.logger.error(f"Failed to fetch global market data for snapshot: {e}")
            return {}
