import yaml
import os
from typing import Dict, Any, List
from pathlib import Path

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)
    
    @property
    def coins(self) -> List[str]:
        return self._config.get('coins', [])
    
    @property
    def horizons(self) -> Dict[str, Dict[str, Any]]:
        return self._config.get('horizons', {})
    
    @property
    def indicators(self) -> List[str]:
        return self._config.get('indicators', [])
    
    @property
    def export_settings(self) -> Dict[str, bool]:
        return self._config.get('export', {})
    
    @property
    def output_dir(self) -> str:
        return self._config.get('output_dir', 'data/runs')
    
    def get_horizon_config(self, horizon: str) -> Dict[str, Any]:
        return self.horizons.get(horizon, {})
    
    def should_export(self, format_type: str) -> bool:
        return self.export_settings.get(format_type, False)
    
    def should_export_individual_coin_files(self) -> bool:
        return self.export_settings.get('individual_coin_files', False)
    
    @property
    def market_data_settings(self) -> Dict[str, Any]:
        return self._config.get('market_data', {})
    
    def should_collect_market_data(self, data_type: str) -> bool:
        return self.market_data_settings.get(f'collect_{data_type}', False)
    
    def get_news_limit(self) -> int:
        return self.market_data_settings.get('news_limit', 10)
    
    def get_update_frequency(self, data_type: str) -> str:
        frequencies = self.market_data_settings.get('update_frequencies', {})
        return frequencies.get(data_type, 'every_run')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get any configuration value with optional default."""
        return self._config.get(key, default)