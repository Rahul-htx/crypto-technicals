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