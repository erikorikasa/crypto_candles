import os
import sys
from datetime import datetime, timedelta

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crypto_candles.exchanges import BinanceExchange, MercadoBitcoinExchange, FoxbitExchange, OKXExchange, NovadaxExchange, BitgetExchange, BybitExchange, MEXCExchange, CryptoComExchange


def test_exchange(exchange, exchange_name, symbol="BTC-USDT", timeframe="1d", days=5):
    """Test a specific exchange."""
    print(f"\nTesting {exchange_name}...")
    print("-" * 80)

    try:
        # Test supported pairs
        # pairs = exchange.get_supported_pairs()
        # print(f"Supported pairs: {', '.join(pairs)}")

        # Test supported timeframes
        timeframes = exchange.get_supported_timeframes()
        print(f"Supported timeframes: {', '.join(timeframes)}")

        # Test fetching candles
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        print(f"Start date: {start_date}")
        print(f"End date: {end_date}")

        candles = exchange.get_candles(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
        )

        print(f"\nFetched {len(candles)} candles for {symbol} on {timeframe} timeframe:")
        print("-" * 80)
        print(f"{'Timestamp':<20} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<15}")
        print("-" * 80)

        for candle in candles:
            print(
                f"{candle.timestamp.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{candle.open:<10.2f} "
                f"{candle.high:<10.2f} "
                f"{candle.low:<10.2f} "
                f"{candle.close:<10.2f} "
                f"{candle.volume:<15.8f}"
            )

    except Exception as e:
        print(f"Error testing {exchange_name}: {str(e)}")


def main():
    # Initialize exchanges
    exchanges = {
        "Binance": BinanceExchange(),
        "Mercado Bitcoin": MercadoBitcoinExchange(),
        "Foxbit": FoxbitExchange(),
        "OKX": OKXExchange(),
        "Novadax": NovadaxExchange(),
        "Bitget": BitgetExchange(),
        "Bybit": BybitExchange(),
        "Mexc": MEXCExchange(),
        "Crypto.com": CryptoComExchange(),
    }

    # Test each exchange
    for name, exchange in exchanges.items():
        test_exchange(exchange, name)


if __name__ == "__main__":
    main() 