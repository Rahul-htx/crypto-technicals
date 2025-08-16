import click
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config_loader import Config
from .pipeline import Pipeline
from .utils.logging_utils import setup_logger

@click.command()
@click.option(
    '--coins',
    type=str,
    help='Comma-separated list of coins (e.g., "eth,btc,sol")'
)
@click.option(
    '--horizons',
    type=str,
    help='Comma-separated list of horizons (e.g., "intraday,swing")'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    default='config.yaml',
    help='Path to configuration file'
)
@click.option(
    '--output-dir',
    type=str,
    help='Override output directory'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose logging'
)
def main(
    coins: Optional[str],
    horizons: Optional[str],
    config: str,
    output_dir: Optional[str],
    verbose: bool
):
    """
    CryptoTechnicals - Technical Analysis Data Engine
    
    Pulls historical price/volume data from CoinGecko API and computes
    technical indicators for cryptocurrency assets.
    """
    
    # Setup logging
    logger = setup_logger(verbose)
    
    try:
        # Load configuration
        config_obj = Config(config)
        logger.info(f"Loaded configuration from {config}")
        
        # Override config with CLI arguments if provided
        coin_list = coins.split(',') if coins else config_obj.coins
        horizon_list = horizons.split(',') if horizons else list(config_obj.horizons.keys())
        output_directory = output_dir if output_dir else config_obj.output_dir
        
        logger.info(f"Processing coins: {coin_list}")
        logger.info(f"Processing horizons: {horizon_list}")
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_output_dir = Path(output_directory) / timestamp
        run_output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Output directory: {run_output_dir}")
        
        # Initialize and run pipeline
        pipeline = Pipeline(config_obj, str(run_output_dir), logger)
        
        for horizon in horizon_list:
            if horizon not in config_obj.horizons:
                logger.warning(f"Horizon '{horizon}' not found in config, skipping")
                continue
                
            logger.info(f"Processing horizon: {horizon}")
            pipeline.run(coin_list, horizon)
        
        logger.info("Pipeline completed successfully")
        print(f"Results saved to: {run_output_dir}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()