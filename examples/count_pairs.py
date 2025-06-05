import os
import sys
from datetime import datetime, timedelta

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
    CryptoComExchange,
)

def count_pairs():
    """Count the number of BRL pairs from each exchange."""
    exchanges = {
        "Binance": BinanceExchange(),
        "Mercado Bitcoin": MercadoBitcoinExchange(),
        "Foxbit": FoxbitExchange(),
        "OKX": OKXExchange(),
        "Novadax": NovadaxExchange(),
        "Bitget": BitgetExchange(),
        "Bybit": BybitExchange(),
        "MEXC": MEXCExchange(),
        "Crypto.com": CryptoComExchange(),
    }

    total_pairs = 0
    print("\nBRL Pairs per Exchange:")
    print("-" * 50)
    
    for name, exchange in exchanges.items():
        try:
            pairs = exchange.get_supported_pairs()
            pair_count = len(pairs)
            total_pairs += pair_count
            print(f"{name}: {pair_count} pairs")
            print(f"Sample pairs: {', '.join(pairs[:5])}")
            print("-" * 50)
        except Exception as e:
            print(f"Error getting pairs from {name}: {str(e)}")
            print("-" * 50)

    print(f"\nTotal number of unique BRL pairs across all exchanges: {total_pairs}")

if __name__ == "__main__":
    count_pairs() 