from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock

from crypto_candles.exchanges import BinanceExchange
from crypto_candles.models.candle import Candle


@pytest.fixture
def mock_requests():
    with patch("requests.request") as mock:
        yield mock


@pytest.fixture
def binance_exchange(mock_requests):
    return BinanceExchange(api_key="test_key", api_secret="test_secret")


def test_get_candles(binance_exchange, mock_requests):
    # Mock response data
    mock_response = MagicMock()
    mock_response.json.return_value = [
        [
            1625097600000,  # timestamp
            "35000.0",      # open
            "36000.0",      # high
            "34000.0",      # low
            "35500.0",      # close
            "100.0",        # volume
            1625097899999,  # close time
            "3500000.0",    # quote asset volume
            100,            # number of trades
            "50.0",         # taker buy base asset volume
            "1750000.0",    # taker buy quote asset volume
            "0"             # ignore
        ]
    ]
    mock_requests.return_value = mock_response

    # Test get_candles
    candles = binance_exchange.get_candles(
        symbol="BTC-BRL",
        timeframe="1h",
        since=datetime.now() - timedelta(hours=1),
        limit=1
    )

    # Verify results
    assert len(candles) == 1
    candle = candles[0]
    assert isinstance(candle, Candle)
    assert candle.symbol == "BTC-BRL"
    assert candle.exchange == "binance"
    assert candle.timeframe == "1h"
    assert candle.open == 35000.0
    assert candle.high == 36000.0
    assert candle.low == 34000.0
    assert candle.close == 35500.0
    assert candle.volume == 100.0
    assert candle.quote_volume == 3500000.0

    # Verify request was made correctly
    mock_requests.assert_called_once()
    args, kwargs = mock_requests.call_args
    assert args[0] == "GET"
    assert "klines" in args[1]
    assert kwargs["params"]["symbol"] == "BTCBRL"
    assert kwargs["params"]["interval"] == "1h"


def test_invalid_symbol(binance_exchange, mock_requests):
    # Mock exchange info response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "symbols": [
            {"symbol": "BTCBRL", "status": "TRADING"},
            {"symbol": "ETHBRL", "status": "TRADING"}
        ]
    }
    mock_requests.return_value = mock_response

    with pytest.raises(ValueError, match="Unsupported symbol"):
        binance_exchange.get_candles("INVALID-BRL")


def test_invalid_timeframe(binance_exchange):
    with pytest.raises(ValueError, match="Unsupported timeframe"):
        binance_exchange.get_candles("BTC-BRL", timeframe="invalid")


def test_get_supported_timeframes(binance_exchange):
    timeframes = binance_exchange.get_supported_timeframes()
    assert isinstance(timeframes, list)
    assert "1h" in timeframes
    assert "1d" in timeframes


def test_api_error_handling(binance_exchange, mock_requests):
    # Mock API error
    mock_requests.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="Failed to fetch candles"):
        binance_exchange.get_candles("BTC-BRL") 