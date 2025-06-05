import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crypto_candles.exchanges import (
    BinanceExchange,
    MercadoBitcoinExchange,
    FoxbitExchange,
    OKXExchange,
    NovadaxExchange,
    BitgetExchange,
    BybitExchange,
    MEXCExchange,
)
from src.crypto_candles.storage.s3_storage import S3Storage


def get_candles_df(candles, exchange_name):
    """Convert candles to DataFrame."""
    df = pd.DataFrame([
        {
            'timestamp': candle.timestamp,
            'open': candle.open,
            'high': candle.high,
            'low': candle.low,
            'close': candle.close,
            'volume': candle.volume,
            'quote_volume': candle.quote_volume,
            'pair': candle.symbol,
            'exchange': exchange_name
        }
        for candle in candles
    ])
    return df


def main():
    # Initialize exchanges
    exchanges = {
        "binance": BinanceExchange(),
        "mercado_bitcoin": MercadoBitcoinExchange(),
        "foxbit": FoxbitExchange(),
        "okx": OKXExchange(),
        "novadax": NovadaxExchange(),
        "bitget": BitgetExchange(),
        "bybit": BybitExchange(),
        "mexc": MEXCExchange(),
    }

    # Initialize S3 storage
    s3_storage = S3Storage(
        bucket_name=os.getenv("AWS_S3_BUCKET", "your-bucket-name"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        partition_by_day=os.getenv("PARTITION_BY_DAY", "false").lower() == "true",
    )

    # Example parameters
    symbol = "BTC-BRL"
    timeframe = "1h"
    hours = 24  # Last 24 hours

    # Calculate start and end time
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours)

    try:
        # Fetch candles from all exchanges
        all_dfs = {}
        
        for exchange_name, exchange in exchanges.items():
            try:
                print(f"\nFetching candles from {exchange_name}...")
                candles = exchange.get_candles(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date,
                )
                all_dfs[exchange_name] = get_candles_df(candles, exchange_name)
                print(f"Successfully fetched {len(candles)} candles")
            except Exception as e:
                print(f"Error fetching from {exchange_name}: {str(e)}")

        if not all_dfs:
            print("No data was fetched from any exchange")
            return

        # Store data in S3
        print("\nStoring data in S3...")
        results = s3_storage.store_multiple_exchanges(all_dfs, symbol)
        
        # Print results
        print("\nStorage Results:")
        print("=" * 50)
        for exchange, success in results.items():
            status = "Success" if success else "Failed"
            print(f"{exchange}: {status}")

        # Combine all DataFrames for local CSV
        df = pd.concat(all_dfs.values(), ignore_index=True)
        
        # Sort by timestamp and exchange
        df = df.sort_values(['timestamp', 'exchange'])
        
        # Display the DataFrame
        print("\nCandle Data:")
        print("=" * 100)
        print(df)
        
        # Save to CSV locally as backup
        output_file = "candles_data.csv"
        df.to_csv(output_file, index=False)
        print(f"\nLocal backup saved to {output_file}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 