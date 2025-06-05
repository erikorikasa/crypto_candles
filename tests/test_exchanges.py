import unittest
from datetime import datetime, timedelta
from src.crypto_candles.exchanges import (
    BinanceExchange,
    MercadoBitcoinExchange,
    FoxbitExchange,
    OKXExchange,
    NovadaxExchange,
)


class TestExchanges(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.binance = BinanceExchange()
        self.mercado_bitcoin = MercadoBitcoinExchange()
        self.foxbit = FoxbitExchange()
        self.okx = OKXExchange()
        self.novadax = NovadaxExchange()
        self.symbol = "BTC-BRL"
        self.timeframe = "1h"
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=1)

    def test_binance(self):
        """Test Binance exchange."""
        print("\nTesting Binance...")
        
        # Test supported pairs
        pairs = self.binance.get_supported_pairs()
        print(f"Supported pairs: {pairs}")
        self.assertIsInstance(pairs, list)
        self.assertGreater(len(pairs), 0)
        
        # Test supported timeframes
        timeframes = self.binance.get_supported_timeframes()
        print(f"Supported timeframes: {timeframes}")
        self.assertIsInstance(timeframes, list)
        self.assertGreater(len(timeframes), 0)
        
        # Test getting candles
        candles = self.binance.get_candles(
            symbol=self.symbol,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        print(f"Fetched {len(candles)} candles")
        self.assertIsInstance(candles, list)
        self.assertGreater(len(candles), 0)
        
        # Test candle structure
        candle = candles[0]
        self.assertIsNotNone(candle.timestamp)
        self.assertIsNotNone(candle.open)
        self.assertIsNotNone(candle.high)
        self.assertIsNotNone(candle.low)
        self.assertIsNotNone(candle.close)
        self.assertIsNotNone(candle.volume)
        self.assertIsNotNone(candle.quote_volume)
        self.assertEqual(candle.symbol, self.symbol)
        self.assertEqual(candle.exchange, "binance")

    def test_mercado_bitcoin(self):
        """Test Mercado Bitcoin exchange."""
        print("\nTesting Mercado Bitcoin...")
        
        # Test supported pairs
        pairs = self.mercado_bitcoin.get_supported_pairs()
        print(f"Supported pairs: {pairs}")
        self.assertIsInstance(pairs, list)
        self.assertGreater(len(pairs), 0)
        
        # Test supported timeframes
        timeframes = self.mercado_bitcoin.get_supported_timeframes()
        print(f"Supported timeframes: {timeframes}")
        self.assertIsInstance(timeframes, list)
        self.assertGreater(len(timeframes), 0)
        
        # Test getting candles
        candles = self.mercado_bitcoin.get_candles(
            symbol=self.symbol,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        print(f"Fetched {len(candles)} candles")
        self.assertIsInstance(candles, list)
        self.assertGreater(len(candles), 0)
        
        # Test candle structure
        candle = candles[0]
        self.assertIsNotNone(candle.timestamp)
        self.assertIsNotNone(candle.open)
        self.assertIsNotNone(candle.high)
        self.assertIsNotNone(candle.low)
        self.assertIsNotNone(candle.close)
        self.assertIsNotNone(candle.volume)
        self.assertIsNotNone(candle.quote_volume)
        self.assertEqual(candle.symbol, self.symbol)
        self.assertEqual(candle.exchange, "mercado_bitcoin")

    def test_foxbit(self):
        """Test Foxbit exchange."""
        print("\nTesting Foxbit...")
        
        # Test supported pairs
        pairs = self.foxbit.get_supported_pairs()
        print(f"Supported pairs: {pairs}")
        self.assertIsInstance(pairs, list)
        self.assertGreater(len(pairs), 0)
        
        # Test supported timeframes
        timeframes = self.foxbit.get_supported_timeframes()
        print(f"Supported timeframes: {timeframes}")
        self.assertIsInstance(timeframes, list)
        self.assertGreater(len(timeframes), 0)
        
        # Test getting candles
        candles = self.foxbit.get_candles(
            symbol=self.symbol,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        print(f"Fetched {len(candles)} candles")
        self.assertIsInstance(candles, list)
        self.assertGreater(len(candles), 0)
        
        # Test candle structure
        candle = candles[0]
        self.assertIsNotNone(candle.timestamp)
        self.assertIsNotNone(candle.open)
        self.assertIsNotNone(candle.high)
        self.assertIsNotNone(candle.low)
        self.assertIsNotNone(candle.close)
        self.assertIsNotNone(candle.volume)
        self.assertIsNotNone(candle.quote_volume)
        self.assertEqual(candle.symbol, self.symbol)
        self.assertEqual(candle.exchange, "foxbit")

    def test_okx(self):
        """Test OKX exchange."""
        print("\nTesting OKX...")
        
        # Test supported pairs
        pairs = self.okx.get_supported_pairs()
        print(f"Supported pairs: {pairs}")
        self.assertIsInstance(pairs, list)
        self.assertGreater(len(pairs), 0)
        
        # Test supported timeframes
        timeframes = self.okx.get_supported_timeframes()
        print(f"Supported timeframes: {timeframes}")
        self.assertIsInstance(timeframes, list)
        self.assertGreater(len(timeframes), 0)
        
        # Test getting candles
        candles = self.okx.get_candles(
            symbol=self.symbol,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        print(f"Fetched {len(candles)} candles")
        self.assertIsInstance(candles, list)
        self.assertGreater(len(candles), 0)
        
        # Test candle structure
        candle = candles[0]
        self.assertIsNotNone(candle.timestamp)
        self.assertIsNotNone(candle.open)
        self.assertIsNotNone(candle.high)
        self.assertIsNotNone(candle.low)
        self.assertIsNotNone(candle.close)
        self.assertIsNotNone(candle.volume)
        self.assertIsNotNone(candle.quote_volume)
        self.assertEqual(candle.symbol, self.symbol)
        self.assertEqual(candle.exchange, "okx")

    def test_novadax(self):
        """Test Novadax exchange."""
        print("\nTesting Novadax...")
        
        # Test supported pairs
        pairs = self.novadax.get_supported_pairs()
        print(f"Supported pairs: {pairs}")
        self.assertIsInstance(pairs, list)
        self.assertGreater(len(pairs), 0)
        
        # Test supported timeframes
        timeframes = self.novadax.get_supported_timeframes()
        print(f"Supported timeframes: {timeframes}")
        self.assertIsInstance(timeframes, list)
        self.assertGreater(len(timeframes), 0)
        
        # Test getting candles
        candles = self.novadax.get_candles(
            symbol=self.symbol,
            timeframe=self.timeframe,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        print(f"Fetched {len(candles)} candles")
        self.assertIsInstance(candles, list)
        self.assertGreater(len(candles), 0)
        
        # Test candle structure
        candle = candles[0]
        self.assertIsNotNone(candle.timestamp)
        self.assertIsNotNone(candle.open)
        self.assertIsNotNone(candle.high)
        self.assertIsNotNone(candle.low)
        self.assertIsNotNone(candle.close)
        self.assertIsNotNone(candle.volume)
        self.assertIsNotNone(candle.quote_volume)
        self.assertEqual(candle.symbol, self.symbol)
        self.assertEqual(candle.exchange, "novadax")


if __name__ == "__main__":
    unittest.main() 